
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
