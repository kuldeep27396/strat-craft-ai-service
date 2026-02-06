"use client";

import { useEffect, useState } from "react";
import Link from 'next/link';
import { useRouter } from "next/navigation";
import { getQuestionnaires } from "@/lib/api/questionnaires";
import { generateStrategy } from "@/lib/api/strategies";
import { Questionnaire } from "@/types/questionnaire";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";

export default function QuestionnairesPage() {
    const router = useRouter();
    const [questionnaires, setQuestionnaires] = useState<Questionnaire[]>([]);
    const [loading, setLoading] = useState(true);
    const [generatingId, setGeneratingId] = useState<string | null>(null);

    useEffect(() => {
        getQuestionnaires()
            .then(setQuestionnaires)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const handleGenerate = async (qId: string) => {
        setGeneratingId(qId);
        try {
            const strategy = await generateStrategy({ questionnaire_id: qId });
            router.push(`/dashboard/strategies/${strategy.id}`);
        } catch (error) {
            console.error("Generation failed", error);
            alert("Failed to start generation");
        } finally {
            setGeneratingId(null);
        }
    };

    return (
        <div className="container py-8 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">Questionnaires</h1>
                <Link href="/dashboard/questionnaires/new">
                    <Button>Create Questionnaire</Button>
                </Link>
            </div>

            {loading ? (
                <div className="text-center py-12 text-muted-foreground">Loading...</div>
            ) : questionnaires.length === 0 ? (
                <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground bg-muted/20">
                    <p className="mb-4">No questionnaires found. Start by creating one.</p>
                    <Link href="/dashboard/questionnaires/new">
                        <Button variant="outline">Create Questionnaire</Button>
                    </Link>
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {questionnaires.map((q) => (
                        <Card key={q.id} className="flex flex-col">
                            <CardHeader>
                                <CardTitle className="text-lg">{q.client_name || "Unnamed Client"}</CardTitle>
                                <div className="text-xs text-muted-foreground">
                                    Product: {q.product_description?.substring(0, 30)}...
                                </div>
                            </CardHeader>
                            <CardContent className="flex-1">
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Budget:</span>
                                        <span className="font-medium">{q.budget_range || "N/A"}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Target:</span>
                                        <span className="font-medium truncate max-w-[150px]">{q.target_icp || "Generic"}</span>
                                    </div>
                                </div>
                            </CardContent>
                            <CardFooter className="pt-4 border-t bg-muted/10">
                                <Button
                                    className="w-full bg-gradient-to-r from-primary to-violet-600 hover:from-primary/90 hover:to-violet-600/90 text-white shadow-md transition-all hover:-translate-y-0.5"
                                    onClick={() => handleGenerate(q.id)}
                                    disabled={generatingId === q.id}
                                >
                                    {generatingId === q.id ? (
                                        <>
                                            <span className="animate-spin mr-2">⟳</span> Generating...
                                        </>
                                    ) : (
                                        <>
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="m5 12 7-7 7 7" /><path d="M12 19V5" /></svg>
                                            Generate Strategy
                                        </>
                                    )}
                                </Button>
                            </CardFooter>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
