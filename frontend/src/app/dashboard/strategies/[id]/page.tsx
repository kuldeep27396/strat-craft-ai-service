
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getStrategy } from "@/lib/api/strategies";
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

    useEffect(() => {
        if (id) {
            getStrategy(id)
                .then(setStrategy)
                .catch(() => setError("Failed to load strategy"))
                .finally(() => setLoading(false));
        }
    }, [id]);

    if (loading) return <div className="container py-12 text-center text-muted-foreground">Loading strategy details...</div>;
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
