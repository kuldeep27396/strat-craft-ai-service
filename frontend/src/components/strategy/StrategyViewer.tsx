
import { Strategy } from "@/types/strategy";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface StrategyViewerProps {
    strategy: Strategy;
}

export function StrategyViewer({ strategy }: StrategyViewerProps) {
    const { strategy_content } = strategy;

    if (!strategy || !strategy.strategy_content || strategy.status === 'generating') {
        return (
            <div className="p-12 text-center border rounded-lg bg-muted/20">
                <div className="flex justify-center mb-4">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary"></div>
                </div>
                <h3 className="text-xl font-semibold mb-2">AI Agents Working on Your Strategy</h3>
                <p className="text-muted-foreground max-w-md mx-auto">
                    Our multi-agent system is analyzing your requirements. This includes:
                </p>
                <ul className="text-left text-sm text-muted-foreground max-w-xs mx-auto mt-4 space-y-1">
                    <li>• Building context from your profile</li>
                    <li>• Generating SEO strategy</li>
                    <li>• Creating content marketing roadmap</li>
                    <li>• Estimating pricing and resources</li>
                </ul>
                <p className="text-muted-foreground mt-4 text-sm">This typically takes 15-30 seconds.</p>
            </div>
        );
    }

    // Check if content structure is valid (has sections)
    // @ts-ignore
    const { title, sections, pricing } = strategy.strategy_content;

    if (!sections || !Array.isArray(sections)) {
        return (
            <div className="p-8 text-center border rounded-lg bg-red-50 text-red-900">
                <h3 className="text-lg font-medium">Strategy Content Error</h3>
                <p className="mt-2">The generated strategy content appears to be malformed or incomplete.</p>
            </div>
        );
    }

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-extrabold tracking-tight text-primary">
                    {strategy_content.title || "Untitled Strategy"}
                </h1>
                <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                    Version {strategy.version}
                </div>
            </div>

            <div className="grid gap-8">
                {strategy_content.sections?.map((section, index) => (
                    <Card key={index} className="overflow-hidden border-l-4 border-l-primary shadow-md">
                        <CardHeader className="bg-muted/10 pb-4">
                            <CardTitle className="text-xl font-bold">{section.heading}</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-6 space-y-6">
                            <div className="prose prose-slate dark:prose-invert max-w-none">
                                <p className="whitespace-pre-wrap leading-relaxed">{section.content}</p>
                            </div>

                            {section.tactics && section.tactics.length > 0 && (
                                <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 p-4">
                                    <h4 className="font-semibold text-blue-700 dark:text-blue-300 mb-2 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="m5 12 7-7 7 7" /><path d="M12 19V5" /></svg>
                                        Tactical Actions
                                    </h4>
                                    <ul className="list-disc pl-5 space-y-1 text-sm">
                                        {section.tactics.map((tactic, i) => (
                                            <li key={i}>{tactic}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {section.kpis && section.kpis.length > 0 && (
                                <div className="rounded-lg bg-green-50 dark:bg-green-900/20 p-4">
                                    <h4 className="font-semibold text-green-700 dark:text-green-300 mb-2 flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="M12 20V10" /><path d="M18 20V4" /><path d="M6 20v-4" /></svg>
                                        Success Metrics (KPIs)
                                    </h4>
                                    <div className="flex flex-wrap gap-2">
                                        {section.kpis.map((kpi, i) => (
                                            <span key={i} className="inline-flex items-center rounded-md bg-white dark:bg-black/20 border px-2 py-1 text-xs font-medium text-green-700 dark:text-green-400 ring-1 ring-inset ring-green-600/20">
                                                {kpi}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                ))}
            </div>

            {strategy_content.pricing && (
                <Card className="bg-primary/5 border-primary/20">
                    <CardHeader>
                        <CardTitle>Estimated Resources</CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col md:flex-row justify-between items-center gap-4">
                        <div>
                            <h4 className="font-semibold mb-2">Recommended Team</h4>
                            <div className="flex gap-2 flex-wrap">
                                {strategy_content.pricing.team.map((role, i) => (
                                    <span key={i} className="bg-background border px-3 py-1 rounded-full text-sm">{role}</span>
                                ))}
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-muted-foreground">Est. Monthly Budget</p>
                            <p className="text-3xl font-bold text-primary">${strategy_content.pricing.monthly_cost.toLocaleString()}</p>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
