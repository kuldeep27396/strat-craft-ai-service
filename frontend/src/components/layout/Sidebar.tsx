"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
    { name: 'Dashboard', href: '/dashboard', icon: (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="9" x="3" y="3" rx="1" /><rect width="7" height="5" x="14" y="3" rx="1" /><rect width="7" height="9" x="14" y="12" rx="1" /><rect width="7" height="5" x="3" y="16" rx="1" /></svg> },
    { name: 'Profiles', href: '/dashboard/profiles', icon: (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" /><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" /><path d="M4 22h16" /><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" /><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" /><path d="M18 2h-4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Z" /><path d="M6 2H2a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Z" /></svg> },
    { name: 'Questionnaires', href: '/dashboard/questionnaires', icon: (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg> },
    { name: 'Strategies', href: '/dashboard/strategies', icon: (props: any) => <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v8" /><path d="m4.93 10.93 1.41 1.41" /><path d="M2 18h2" /><path d="M20 18h2" /><path d="m19.07 10.93-1.41 1.41" /><path d="M22 22H2" /><path d="m16 6-4-4-4 4" /><path d="M16 18a4 4 0 0 0-8 0" /></svg> },
];

export function Sidebar() {
    // Note: usePathname needs to be used in Client Component
    return (
        <div className="hidden border-r bg-muted/40 md:block w-64 flex-col">
            <div className="flex h-16 items-center border-b px-6">
                <Link href="/" className="flex items-center gap-2 font-bold text-lg">
                    <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white">
                        SC
                    </div>
                    <span>StratCraft</span>
                </Link>
            </div>
            <div className="flex-1 overflow-auto py-4">
                <nav className="grid items-start px-4 text-sm font-medium space-y-2">
                    <NavLinks />
                </nav>
            </div>
            <div className="border-t p-4">
                <div className="flex items-center gap-3 rounded-lg bg-card p-3 shadow-sm border">
                    <div className="h-8 w-8 rounded-full bg-primary/20" />
                    <div className="grid gap-0.5 text-xs">
                        <div className="font-medium">Demo User</div>
                        <div className="text-muted-foreground">demo@stratcraft.ai</div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Separate client component for navigation logic
function NavLinks() {
    const pathname = usePathname();
    return (
        <>
            {navItems.map((item) => {
                const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
                return (
                    <Link
                        key={item.href}
                        href={item.href}
                        className={`group flex items-center gap-3 rounded-lg px-3 py-2 transition-all hover:text-primary ${isActive ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-muted'
                            }`}
                    >
                        <item.icon className="h-4 w-4" />
                        {item.name}
                    </Link>
                )
            })}
        </>
    )
}
