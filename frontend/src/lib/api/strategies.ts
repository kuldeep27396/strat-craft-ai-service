
import { Strategy, StrategyCreate } from '@/types/strategy';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getStrategies(): Promise<Strategy[]> {
    const res = await fetch(`${API_URL}/api/strategies/`);
    if (!res.ok) throw new Error('Failed to fetch strategies');
    return res.json();
}

export async function getStrategy(id: string): Promise<Strategy> {
    const res = await fetch(`${API_URL}/api/strategies/${id}`);
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Failed to fetch strategy' }));
        throw new Error(errorData.detail || 'Failed to fetch strategy');
    }
    return res.json();
}

export async function getStrategyStatus(id: string): Promise<{ id: string; status: string; progress: number }> {
    const res = await fetch(`${API_URL}/api/strategies/${id}/status`);
    if (!res.ok) throw new Error('Failed to fetch strategy status');
    return res.json();
}

export async function generateStrategy(data: StrategyCreate): Promise<Strategy> {
    const res = await fetch(`${API_URL}/api/strategies/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Failed to start generation' }));
        throw new Error(errorData.detail || 'Failed to start generation');
    }
    return res.json();
}

/**
 * Poll for strategy completion with progress updates
 * @param strategyId - ID of the strategy to poll
 * @param onProgress - Callback with progress updates (0-100)
 * @param interval - Polling interval in ms (default 2000ms)
 * @param maxAttempts - Maximum number of polling attempts (default 30 = ~1 minute)
 */
export async function pollStrategyCompletion(
    strategyId: string,
    onProgress?: (progress: number) => void,
    interval: number = 2000,
    maxAttempts: number = 30
): Promise<Strategy> {
    let attempts = 0;

    while (attempts < maxAttempts) {
        const strategy = await getStrategy(strategyId);

        // Update progress based on status
        if (strategy.status === 'completed') {
            onProgress?.(100);
            return strategy;
        }

        if (strategy.status === 'failed') {
            throw new Error('Strategy generation failed');
        }

        // Calculate progress (estimating based on attempts)
        const progress = Math.min(10 + (attempts / maxAttempts) * 80, 90);
        onProgress?.(Math.round(progress));

        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, interval));
        attempts++;
    }

    throw new Error('Strategy generation timed out');
}
