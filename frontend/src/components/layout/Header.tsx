
export function Header() {
    return (
        <header className="flex h-16 items-center gap-4 border-b bg-background px-6">
            <div className="flex-1">
                <h2 className="text-lg font-semibold">Dashboard</h2>
            </div>
            <div className="flex items-center gap-4">
                <button className="text-sm font-medium text-muted-foreground hover:text-foreground">Help</button>
                <button className="text-sm font-medium text-muted-foreground hover:text-foreground">Feedback</button>
            </div>
        </header>
    );
}
