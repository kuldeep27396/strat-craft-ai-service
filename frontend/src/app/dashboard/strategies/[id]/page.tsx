
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getStrategy, pollStrategyCompletion } from "@/lib/api/strategies";
import { Strategy } from "@/types/strategy";
import { StrategyViewer } from "@/components/strategy/StrategyViewer";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function StrategyDetailPage() {
    const params = useParams();
    const id = params.id as string;
    const [strategy, setStrategy] = useState<Strategy | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (!id) return;

        const loadStrategy = async () => {
            try {
                const initialStrategy = await getStrategy(id);
                setStrategy(initialStrategy);

                // If still generating, poll for completion
                if (initialStrategy.status === 'generating') {
                    setLoading(true);
                    const completed = await pollStrategyCompletion(
                        id,
                        (prog) => setProgress(prog),
                        2000,
                        45
                    );
                    setStrategy(completed);
                }
                setLoading(false);
            } catch (err) {
                setError("Failed to load strategy");
                setLoading(false);
            }
        };

        loadStrategy();
    }, [id]);

    if (loading) {
        return (
            <div className="container py-12 text-center">
                <div className="max-w-md mx-auto space-y-4">
                    <div className="flex justify-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                    </div>
                    <h2 className="text-xl font-semibold">
                        {strategy?.status === 'generating' ? 'AI Agents Working...' : 'Loading strategy...'}
                    </h2>
                    {progress > 0 && (
                        <div className="space-y-2">
                            <div className="bg-gray-200 rounded-full h-2">
                                <div
                                    className="bg-primary h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                            <p className="text-sm text-muted-foreground">{progress}% complete</p>
                        </div>
                    )}
                    {strategy?.status === 'generating' && (
                        <p className="text-sm text-muted-foreground">
                            Our AI agents are analyzing your requirements and generating a customized strategy...
                        </p>
                    )}
                </div>
            </div>
        );
    }
    if (error) return <div className="container py-12 text-center text-red-500">{error}</div>;
    if (!strategy) return <div className="container py-12 text-center">Strategy not found.</div>;

    return (
        <div className="container py-8 space-y-6">
            <div className="flex justify-between items-center print:hidden">
                <Link href="/dashboard/strategies" className="text-sm text-muted-foreground hover:underline">
                    &larr; Back to Strategies
                </Link>
                <Button variant="outline" onClick={() => window.print()}>
                    Export PDF
                </Button>
            </div>

            <StrategyViewer strategy={strategy} />
        </div>
    );
}
