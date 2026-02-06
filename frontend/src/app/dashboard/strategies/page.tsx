"use client";

import { useEffect, useState } from "react";
import Link from 'next/link';
import { getStrategies } from "@/lib/api/strategies";
import { Strategy } from "@/types/strategy";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function StrategiesPage() {
    const [strategies, setStrategies] = useState<Strategy[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getStrategies()
            .then(setStrategies)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="container py-8 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">My Strategies</h1>
                <Link href="/dashboard/questionnaires">
                    <Button>Generate New Strategy</Button>
                </Link>
            </div>

            {loading ? (
                <div className="text-center py-12 text-muted-foreground">Loading...</div>
            ) : strategies.length === 0 ? (
                <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground bg-muted/20">
                    <p className="mb-4">No strategies generated yet.</p>
                    <Link href="/dashboard/questionnaires">
                        <Button variant="outline">Start First Generation</Button>
                    </Link>
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {strategies.map((strategy) => (
                        <Card key={strategy.id} className="hover:shadow-md transition-shadow cursor-pointer group">
                            <Link href={`/dashboard/strategies/${strategy.id}`}>
                                <CardHeader>
                                    <div className="flex justify-between items-start">
                                        <CardTitle className="line-clamp-1 group-hover:text-primary transition-colors">
                                            {strategy.strategy_content?.title || "Untitled Strategy"}
                                        </CardTitle>
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        {new Date(strategy.created_at).toLocaleDateString()}
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="flex justify-between items-center mt-2">
                                        <div className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${strategy.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-yellow-100 text-yellow-700'
                                            }`}>
                                            {strategy.status}
                                        </div>
                                        <span className="text-sm font-medium text-primary group-hover:translate-x-1 transition-transform">
                                            View &rarr;
                                        </span>
                                    </div>
                                </CardContent>
                            </Link>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
