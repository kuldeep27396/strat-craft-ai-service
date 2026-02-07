"""
Test script for the AI Agent Orchestrator.

This script tests the Groq-powered strategy generation without needing a full server.
Run this after setting your GROQ_API_KEY in .env
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_orchestrator():
    """Test the strategy orchestrator with sample data."""
    from app.agents.orchestrator import StrategyOrchestrator

    print("🤖 Testing Groq-Powered AI Agent Orchestrator\n")

    # Sample business profile data
    business_profile = {
        "name": "TechFlow Solutions",
        "industry": "B2B SaaS",
        "products": ["Project Management Tool", "Team Collaboration Platform"],
        "problems_solving": [
            "Remote team communication gaps",
            "Project visibility issues",
            "Resource allocation inefficiencies"
        ],
        "target_customers": ["Mid-market tech companies", "Startups 50-500 employees"]
    }

    # Sample questionnaire data
    questionnaire = {
        "client_name": "TechFlow Solutions",
        "problem_statement": "Need to increase qualified leads and improve organic visibility for our project management platform targeting remote teams.",
        "target_icp": "CTOs and VP of Engineering at tech companies with 50-500 employees, using remote/hybrid work models",
        "business_objectives": [
            "Increase organic traffic by 50% in 6 months",
            "Generate 100+ qualified leads per month",
            "Establish thought leadership in remote work space"
        ],
        "budget_range": "$5,000 - $10,000/month",
        "marketing_channels": ["SEO", "Content Marketing", "LinkedIn", "Email Marketing"]
    }

    print("📋 Input Data:")
    print(f"  Client: {business_profile['name']}")
    print(f"  Industry: {business_profile['industry']}")
    print(f"  Problem: {questionnaire['problem_statement'][:60]}...")
    print(f"  Budget: {questionnaire['budget_range']}\n")

    try:
        print("⚙️  Initializing orchestrator...")
        orchestrator = StrategyOrchestrator()
        print("  ✓ Orchestrator initialized\n")

        print("🔄 Generating strategy (this may take 15-30 seconds)...")
        print("  - Running context builder...")
        print("  - Running executive summary agent...")
        print("  - Running SEO agent...")
        print("  - Running content agent...")
        print("  - Running quality reviewer...")

        strategy = await orchestrator.generate_strategy(
            business_profile=business_profile,
            questionnaire=questionnaire
        )

        print("\n✅ Strategy Generation Complete!\n")

        # Display results
        print("📄 Generated Strategy:")
        print(f"  Title: {strategy.get('title')}\n")

        sections = strategy.get('sections', [])
        print(f"  Sections ({len(sections)}):")
        for i, section in enumerate(sections, 1):
            print(f"\n  {i}. {section.get('heading')}")
            content_preview = section.get('content', '')[:100]
            print(f"     {content_preview}...")
            print(f"     Tactics: {len(section.get('tactics', []))}")
            print(f"     KPIs: {len(section.get('kpis', []))}")

        pricing = strategy.get('pricing')
        if pricing:
            print(f"\n  💰 Pricing: ${pricing.get('monthly_cost', 0)}/month")
            print(f"  👥 Team: {', '.join(pricing.get('team', []))}")

        metadata = strategy.get('metadata', {})
        print(f"\n  📊 Generated with: {metadata.get('model', 'unknown')}")
        print(f"  🕐 At: {metadata.get('generated_at', 'unknown')[:19]}")

        return True

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n💡 To fix:")
        print("   1. Get your Groq API key from https://console.groq.com/")
        print("   2. Add it to backend/.env: GROQ_API_KEY=gsk_your_key_here")
        return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_structured_output():
    """Test just the structured output models."""
    from app.schemas.agent_output import StrategySection, PricingInfo, StrategyContent

    print("\n🧪 Testing Structured Output Models\n")

    # Create a test section
    section = StrategySection(
        heading="Test Section",
        content="This is a test section for the marketing strategy.",
        tactics=["Tactic 1", "Tactic 2", "Tactic 3"],
        kpis=["KPI 1", "KPI 2"]
    )

    print(f"  StrategySection: {section.heading}")
    print(f"    Tactics: {len(section.tactics)}")
    print(f"    KPIs: {len(section.kpis)}")

    # Create pricing
    pricing = PricingInfo(
        monthly_cost=5000,
        team=["SEO Specialist", "Content Writer", "Account Manager"]
    )

    print(f"\n  PricingInfo: ${pricing.monthly_cost}/month")
    print(f"    Team: {', '.join(pricing.team)}")

    print("\n  ✓ All models validate correctly!\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test the AI Agent Orchestrator")
    parser.add_argument("--models-only", action="store_true", help="Only test the Pydantic models")
    args = parser.parse_args()

    if args.models_only:
        asyncio.run(test_structured_output())
    else:
        success = asyncio.run(test_orchestrator())
        if not success:
            sys.exit(1)
