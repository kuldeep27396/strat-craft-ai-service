import Link from 'next/link'

export default function Home() {
    return (
        <div className="flex min-h-screen flex-col bg-background selection:bg-primary/20">
            {/* Navigation */}
            <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-xl">
                <div className="container flex h-16 items-center justify-between px-4 md:px-6">
                    <div className="flex gap-2 items-center font-bold text-xl tracking-tight">
                        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" /></svg>
                        </div>
                        StratCraft AI
                    </div>
                    <nav className="hidden gap-6 md:flex">
                        <Link href="#features" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Features</Link>
                        <Link href="#pricing" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Pricing</Link>
                        <Link href="/docs" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">Docs</Link>
                    </nav>
                    <div className="flex gap-4">
                        <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors flex items-center">Log in</Link>
                        <Link href="/dashboard" className="hidden sm:inline-flex h-9 items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50">
                            Get Started
                        </Link>
                    </div>
                </div>
            </header>

            <main className="flex-1">
                {/* Hero Section */}
                <section className="relative pt-24 pb-32 md:pt-32 md:pb-48 overflow-hidden">
                    <div className="absolute inset-0 bg-grid-pattern [mask-image:linear-gradient(to_bottom,white,transparent)] pointer-events-none" />
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-primary/20 blur-[100px] rounded-full pointer-events-none opacity-50" />

                    <div className="container px-4 md:px-6 relative z-10">
                        <div className="flex flex-col items-center text-center space-y-8">
                            <div className="inline-flex items-center rounded-full border bg-background px-3 py-1 text-sm font-medium text-muted-foreground shadow-sm">
                                <span className="flex h-2 w-2 rounded-full bg-primary mr-2" />
                                v0.1 MVP Now Live
                            </div>

                            <h1 className="text-4xl font-extrabold tracking-tight lg:text-7xl max-w-4xl text-balance bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70 sm:text-6xl">
                                Craft Marketing Strategies <br />
                                <span className="text-primary">in Minutes, Not Days</span>
                            </h1>

                            <p className="mx-auto max-w-[700px] text-lg text-muted-foreground md:text-xl leading-relaxed text-balance">
                                Transform raw business data and client objectives into comprehensive, data-driven marketing proposals using our multi-agent AI engine.
                            </p>

                            <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
                                <Link href="/dashboard" className="inline-flex h-12 items-center justify-center rounded-lg bg-primary px-8 text-base font-medium text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:-translate-y-0.5">
                                    Generate Strategy
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="ml-2 h-4 w-4"><path d="M5 12h14" /><path d="m12 5 7 7-7 7" /></svg>
                                </Link>
                                <Link href="#" className="inline-flex h-12 items-center justify-center rounded-lg border border-input bg-background/50 backdrop-blur-sm px-8 text-base font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground hover:-translate-y-0.5">
                                    View Demo
                                </Link>
                            </div>
                        </div>

                        {/* Hero Image / Dashboard Preview */}
                        <div className="mx-auto mt-20 max-w-5xl rounded-xl border bg-background/50 shadow-2xl overflow-hidden ring-1 ring-white/10 backdrop-blur-sm">
                            <div className="flex items-center gap-2 border-b bg-muted/50 px-4 py-2">
                                <div className="flex gap-1.5">
                                    <div className="h-3 w-3 rounded-full bg-red-400/80" />
                                    <div className="h-3 w-3 rounded-full bg-yellow-400/80" />
                                    <div className="h-3 w-3 rounded-full bg-green-400/80" />
                                </div>
                                <div className="mx-auto text-xs font-medium text-muted-foreground">app.stratcraft.ai</div>
                            </div>
                            <div className="p-8 aspect-[16/9] bg-gradient-to-tr from-muted/50 to-background flex items-center justify-center text-muted-foreground">
                                <div className="text-center space-y-4">
                                    <div className="w-16 h-16 bg-primary/10 text-primary rounded-2xl mx-auto flex items-center justify-center animate-pulse">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-8 h-8"><circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" /></svg>
                                    </div>
                                    <p>Dashboard Preview UI Placeholder</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Features Grid */}
                <section id="features" className="container px-4 md:px-6 py-24 border-t">
                    <div className="grid gap-12 lg:grid-cols-3">
                        <div className="group space-y-4">
                            <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" /><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" /><path d="M4 22h16" /><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" /><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" /><path d="M18 2h-4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Z" /><path d="M6 2H2a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Z" /></svg>
                            </div>
                            <h3 className="text-xl font-bold">Business Intelligence</h3>
                            <p className="text-muted-foreground">Store reusable client profiles, products, and target audiences. Stop repeating the same inputs for every strategy.</p>
                        </div>
                        <div className="group space-y-4">
                            <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
                            </div>
                            <h3 className="text-xl font-bold">Client Questionnaires</h3>
                            <p className="text-muted-foreground">Send smart forms to clients to capture their specific objectives, budget, and constraints instantly.</p>
                        </div>
                        <div className="group space-y-4">
                            <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-6 w-6"><path d="M12 2v8" /><path d="m4.93 10.93 1.41 1.41" /><path d="M2 18h2" /><path d="M20 18h2" /><path d="m19.07 10.93-1.41 1.41" /><path d="M22 22H2" /><path d="m16 6-4-4-4 4" /><path d="M16 18a4 4 0 0 0-8 0" /></svg>
                            </div>
                            <h3 className="text-xl font-bold">AI Strategy Engine</h3>
                            <p className="text-muted-foreground">Orchestrate multi-agent workflows to generate SEO, Content, and ABM strategies tailored to the specific client need.</p>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="border-t py-12 bg-muted/30">
                <div className="container px-4 md:px-6 flex flex-col md:flex-row justify-between items-center gap-6">
                    <p className="text-sm text-muted-foreground">© 2024 StratCraft AI. All rights reserved.</p>
                    <div className="flex gap-4">
                        <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">Privacy</Link>
                        <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">Terms</Link>
                        <Link href="#" className="text-sm text-muted-foreground hover:text-foreground">Twitter</Link>
                    </div>
                </div>
            </footer>
        </div>
    )
}
