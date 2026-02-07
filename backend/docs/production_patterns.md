# Production-Ready Patterns for StratCraft AI

This document provides implementation patterns for missing production-ready practices.

## Table of Contents
1. [Resilience Patterns](#resilience-patterns)
2. [Logging & Observability](#logging--observability)
3. [API Safety](#api-safety)
4. [Testing Patterns](#testing-patterns)

---

## Resilience Patterns

### 1. Retry with Exponential Backoff

```python
# backend/app/utils/resilience.py
import asyncio
from functools import wraps
from typing import Callable, TypeVar, ParamSpec
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

P = ParamSpec('P')
T = TypeVar('T')

# Using tenacity library (pip install tenacity)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
)
async def call_llm_with_retry(chain, params: dict) -> T:
    """Call LLM with automatic retry on transient failures."""
    return await chain.ainvoke(params)


# Manual implementation without tenacity
def async_retry(max_attempts: int = 3, base_delay: float = 1.0):
    """Decorator for async retry with exponential backoff."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


# Usage in agents
from app.utils.resilience import async_retry

class BaseLLMAgent:
    @async_retry(max_attempts=3, base_delay=1.0)
    async def execute(self, context: AgentContext) -> StrategySection:
        return await self.chain.ainvoke(self._build_params(context))
```

### 2. Circuit Breaker Pattern

```python
# backend/app/utils/circuit_breaker.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Callable

class CircuitState(Enum):
    CLOSED = auto()    # Normal operation
    OPEN = auto()      # Failing, reject requests
    HALF_OPEN = auto() # Testing if recovery

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5        # Open after N failures
    timeout_seconds: int = 60         # Stay open for N seconds
    half_open_attempts: int = 1       # Try N requests in half-open

class CircuitBreaker:
    """Circuit breaker to prevent cascading failures."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_attempts = 0

    def record_success(self):
        """Record a successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.half_open_attempts = 0

    def record_failure(self):
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

    def can_attempt(self) -> bool:
        """Check if request should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if (datetime.utcnow() - self.last_failure_time).total_seconds() > self.config.timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.half_open_attempts = 0
                return True
            return False

        # HALF_OPEN state
        return self.half_open_attempts < self.config.half_open_attempts

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if not self.can_attempt():
            raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


# Usage
from app.utils.circuit_breaker import CircuitBreaker, CircuitBreakerConfig

class LLMService:
    def __init__(self):
        self.breaker = CircuitBreaker(CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=60
        ))

    async def generate(self, prompt: str):
        return await self.breaker.call(self._llm_call, prompt)

    async def _llm_call(self, prompt: str):
        # Actual LLM call here
        pass
```

### 3. Timeout Handling

```python
# backend/app/utils/timeouts.py
import asyncio
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec('P')
T = TypeVar('T')

def with_timeout(timeout_seconds: float):
    """Decorator to add timeout to async functions."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"{func.__name__} timed out after {timeout_seconds}s")
        return wrapper
    return decorator


# Usage in orchestrator
from app.utils.timeouts import with_timeout

class StrategyOrchestrator:
    @with_timeout(timeout_seconds=120)  # 2 minute max
    async def generate_strategy(self, business_profile, questionnaire):
        # Generation logic
        pass
```

---

## Logging & Observability

### 1. Structured Logging

```python
# backend/app/utils/logging.py
import logging
import json
import uuid
from contextvars import ContextVar
from typing import Any
from datetime import datetime

# Request context for correlation
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

class StructuredLogger:
    """Structured JSON logger."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        self.logger.addHandler(handler)

    def _log(self, level: str, message: str, **kwargs):
        """Internal log method."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "request_id": request_id_var.get(),
            **kwargs
        }
        getattr(self.logger, level)(json.dumps(log_entry))

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


# Usage
from app.utils.logging import StructuredLogger, request_id_var

logger = StructuredLogger(__name__)

async def generate_strategy(...):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

    logger.info("strategy_generation_started",
                client_name=context.client_name,
                industry=context.industry)

    try:
        result = await orchestrator.generate(...)
        logger.info("strategy_generation_completed",
                    sections_count=len(result['sections']))
        return result
    except Exception as e:
        logger.error("strategy_generation_failed",
                     error=str(e),
                     error_type=type(e).__name__)
        raise
```

### 2. Metrics/Telemetry

```python
# backend/app/utils/metrics.py
import time
from functools import wraps
from typing import Callable, ParamSpec
from collections import defaultdict
from prometheus_client import Counter, Histogram, Gauge

# Prometheus metrics
strategy_requests = Counter(
    'strategy_requests_total',
    'Total strategy generation requests',
    ['status']
)

strategy_duration = Histogram(
    'strategy_duration_seconds',
    'Strategy generation duration',
    buckets=[1, 5, 10, 30, 60, 120]
)

active_strategies = Gauge(
    'active_strategies',
    'Currently active strategy generations'
)

llm_tokens_used = Counter(
    'llm_tokens_total',
    'Total LLM tokens consumed',
    ['model', 'agent']
)

class Metrics:
    """Metrics collector."""

    @staticmethod
    def track_strategy(func: Callable) -> Callable:
        """Decorator to track strategy generation metrics."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            active_strategies.inc()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                strategy_requests.labels(status='success').inc()
                return result
            except Exception as e:
                strategy_requests.labels(status='error').inc()
                raise
            finally:
                duration = time.time() - start_time
                strategy_duration.observe(duration)
                active_strategies.dec()

        return wrapper


# Usage
from app.utils.metrics import Metrics, llm_tokens_used

@Metrics.track_strategy
async def generate_strategy(...):
    # Automatically tracked
    pass

# Manual tracking
llm_tokens_used.labels(model='llama-3.1-70b', agent='seo').inc(1500)
```

### 3. Request Correlation Middleware

```python
# backend/app/middleware/correlation.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid

from app.utils.logging import request_id_var

class CorrelationMiddleware(BaseHTTPMiddleware):
    """Add request ID to all logs for a request."""

    async def dispatch(self, request: Request, call_next):
        # Get or create request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request_id_var.set(request_id)

        # Add to response
        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response


# Register in main.py
app.add_middleware(CorrelationMiddleware)
```

---

## API Safety

### 1. Rate Limiting

```python
# backend/app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict

class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[key] = [
            t for t in self.requests[key]
            if t > minute_ago
        ]

        # Check limit
        if len(self.requests[key]) >= self.requests_per_minute:
            return False

        self.requests[key].append(now)
        return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    def __init__(self, app, limiter: RateLimiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        # Get client identifier
        client_id = request.client.host
        api_key = request.headers.get('X-API-Key')
        if api_key:
            client_id = f"api_key:{api_key}"

        # Check rate limit
        if not self.limiter.is_allowed(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(self.limiter.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 60)
                }
            )

        return await call_next(request)


# Register in main.py
limiter = RateLimiter(requests_per_minute=60)
app.add_middleware(RateLimitMiddleware, limiter=limiter)
```

### 2. Idempotency Keys

```python
# backend/app/utils/idempotency.py
import hashlib
from typing import Optional
from sqlalchemy.orm import Session

class IdempotencyManager:
    """Ensure operations are idempotent."""

    def __init__(self, redis_client):  # Or database
        self.cache = redis_client

    def generate_key(self, request_data: dict) -> str:
        """Generate idempotency key from request."""
        data_str = json.dumps(request_data, sort_keys=True)
        return f"idempotency:{hashlib.sha256(data_str.encode()).hexdigest()}"

    async def check_and_store(self, key: str, result: any, ttl: int = 3600) -> Optional[any]:
        """Return cached result if exists, otherwise store new result."""
        cached = await self.cache.get(key)
        if cached:
            return json.loads(cached)

        await self.cache.setex(key, ttl, json.dumps(result))
        return None


# Usage in API
@router.post("/generate")
async def generate_strategy(
    request: StrategyGenerate,
    idempotency: IdempotencyManager = Depends(get_idempotency_manager)
):
    # Check for duplicate request
    idempotency_key = idempotency.generate_key(request.dict())
    cached_result = await idempotency.check_and_store(
        idempotency_key,
        result
    )

    if cached_result:
        return cached_result  # Return cached result

    # Proceed with generation
    result = await orchestrator.generate(...)
    await idempotency.check_and_store(idempotency_key, result)
    return result
```

### 3. Health Checks

```python
# backend/app/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.interfaces.llm_provider import LLMProvider

router = APIRouter()

class HealthStatus:
    """Health check status."""

    def __init__(self):
        self.checks = {}

    def add_check(self, name: str, status: bool, message: str = ""):
        self.checks[name] = {"status": "healthy" if status else "unhealthy", "message": message}

    def is_healthy(self) -> bool:
        return all(c["status"] == "healthy" for c in self.checks.values())

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Basic health check."""
    status = HealthStatus()

    # Database check
    try:
        db.execute("SELECT 1")
        status.add_check("database", True)
    except Exception as e:
        status.add_check("database", False, str(e))

    # LLM check
    try:
        # Simple ping to LLM provider
        status.add_check("llm_provider", True)
    except Exception as e:
        status.add_check("llm_provider", False, str(e))

    return {
        "status": "healthy" if status.is_healthy() else "unhealthy",
        "checks": status.checks
    }

@router.get("/health/ready")
async def readiness_check():
    """Readiness check (for Kubernetes)."""
    # Check if service can accept traffic
    return {"status": "ready"}

@router.get("/health/live")
async def liveness_check():
    """Liveness check (for Kubernetes)."""
    # Check if service is alive
    return {"status": "alive"}
```

---

## Testing Patterns

### 1. Unit Tests with Pytest

```python
# tests/agents/test_seo_agent.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.base import SEOAgent
from app.schemas.agent_output import AgentContext

@pytest.fixture
def mock_chain():
    """Mock LLM chain."""
    chain = AsyncMock()
    chain.ainvoke.return_value = Mock(
        heading="SEO Strategy",
        content="Test content",
        tactics=["Tactic 1"],
        kpis=["KPI 1"]
    )
    return chain

@pytest.fixture
def sample_context():
    """Sample agent context."""
    return AgentContext(
        client_name="Test Client",
        industry="Technology",
        problem_statement="Test problem",
        target_icp="Developers",
        business_objectives=["Growth"]
    )

class TestSEOAgent:
    """Tests for SEOAgent."""

    @pytest.mark.asyncio
    async def test_execute_generates_section(self, mock_chain, sample_context):
        """Test agent generates strategy section."""
        agent = SEOAgent(mock_chain, "seo_section")
        result = await agent.execute(sample_context)

        assert result.heading == "SEO Strategy"
        assert result.content == "Test content"
        mock_chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_skip_always_false(self, mock_chain):
        """Test SEO agent never skips."""
        agent = SEOAgent(mock_chain, "seo_section")
        context = Mock(budget_range="$0")
        assert agent.should_skip(context) is False

    def test_name_property(self, mock_chain):
        """Test agent name property."""
        agent = SEOAgent(mock_chain, "seo_section")
        assert agent.name == "Seo"
```

### 2. Integration Tests

```python
# tests/integration/test_strategy_generation.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
class TestStrategyGenerationFlow:
    """End-to-end tests for strategy generation."""

    async def test_full_generation_flow(self, client: AsyncClient, db: AsyncSession):
        """Test complete strategy generation flow."""
        # Create business profile
        profile_response = await client.post(
            "/api/profiles/",
            json={
                "business_name": "Test Corp",
                "industry": "Technology",
                "products": ["SaaS Platform"],
                "problems_solving": ["Inefficiency"],
                "target_customers": ["Enterprises"]
            }
        )
        assert profile_response.status_code == 201
        profile_id = profile_response.json()["id"]

        # Create questionnaire
        questionnaire_response = await client.post(
            "/api/questionnaires/",
            json={
                "business_profile_id": profile_id,
                "client_name": "Test Client",
                "problem_statement": "Need growth",
                "target_icp": "CTOs",
                "business_objectives": ["100 leads/month"],
                "budget_range": "$5000-$10000"
            }
        )
        assert questionnaire_response.status_code == 201
        questionnaire_id = questionnaire_response.json()["id"]

        # Generate strategy
        strategy_response = await client.post(
            "/api/strategies/generate",
            json={"questionnaire_id": questionnaire_id}
        )

        # Wait for completion (poll)
        strategy_id = strategy_response.json()["id"]
        for _ in range(30):  # Max 30 seconds
            status = await client.get(f"/api/strategies/{strategy_id}/status")
            if status.json()["status"] == "completed":
                break
            await asyncio.sleep(1)

        # Verify strategy
        final_strategy = await client.get(f"/api/strategies/{strategy_id}")
        assert final_strategy.status_code == 200
        data = final_strategy.json()
        assert data["status"] == "completed"
        assert "title" in data["strategy_content"]
        assert len(data["strategy_content"]["sections"]) >= 2
```

### 3. Test Fixtures

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from app.main import app
from app.models import Base

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    """Create test client with database."""
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as ac:
        # Override database dependency
        app.dependency_overrides[get_db] = lambda: db_session
        yield ac
        app.dependency_overrides.clear()
```

### 4. Mock LLM for Testing

```python
# tests/mocks/mock_llm.py
from langchain_core.runnables import Runnable
from app.schemas.agent_output import StrategySection

class MockLLMChain(Runnable):
    """Mock LLM chain for testing."""

    def __init__(self, response: StrategySection | None = None):
        self.response = response or self._default_response()
        self.call_count = 0

    def _default_response(self) -> StrategySection:
        return StrategySection(
            heading="Mock Strategy",
            content="This is mock content for testing",
            tactics=["Mock tactic 1", "Mock tactic 2"],
            kpis=["Mock KPI 1"]
        )

    async def ainvoke(self, *args, **kwargs):
        """Return mock response."""
        self.call_count += 1
        return self.response

# Usage in tests
def test_with_mock_llm():
    mock_chain = MockLLMChain()
    agent = SEOAgent(mock_chain, "seo_section")

    result = await agent.execute(sample_context)
    assert result.heading == "Mock Strategy"
    assert mock_chain.call_count == 1
```

---

## Configuration Management

```python
# backend/app/config/environments.py
from pydantic import BaseSettings, Field
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class BaseConfig(BaseSettings):
    """Base configuration."""
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False

    class Config:
        env_file = ".env"

class DevelopmentConfig(BaseConfig):
    """Development environment config."""
    debug: bool = True
    log_level: str = "DEBUG"

class ProductionConfig(BaseConfig):
    """Production environment config."""
    debug: bool = False
    log_level: str = "INFO"
    # Override with production-specific settings

def get_config() -> BaseConfig:
    """Get config based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
    }
    return configs[env]()

# Usage
from app.config.environments import get_config

config = get_config()
logger.setLevel(config.log_level)
```

---

## Quick Reference

### Add to requirements.txt:
```
# Resilience
tenacity>=8.2.0

# Observability
prometheus-client>=0.19.0

# Rate limiting (for production, use Redis)
redis>=5.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
pytest-mock>=3.11.0
```

### File Structure:
```
backend/app/
├── utils/
│   ├── resilience.py      # Retry, circuit breaker
│   ├── logging.py         # Structured logging
│   ├── metrics.py         # Prometheus metrics
│   ├── timeouts.py        # Timeout decorators
│   └── idempotency.py     # Idempotency keys
├── middleware/
│   ├── correlation.py     # Request correlation
│   └── rate_limit.py      # Rate limiting
├── api/
│   └── health.py          # Health checks
└── tests/
    ├── unit/              # Unit tests
    ├── integration/       # Integration tests
    └── conftest.py        # Test fixtures
```
