"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getProfiles } from '@/lib/api/profiles';
import { BusinessProfile } from '@/types/profile';

export default function ProfilesPage() {
    const [profiles, setProfiles] = useState<BusinessProfile[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getProfiles()
            .then(setProfiles)
            .catch((err) => console.error(err))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="container py-8 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">Business Profiles</h1>
                <Link
                    href="/dashboard/profiles/new"
                    className="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow hover:bg-primary/90"
                >
                    Create Profile
                </Link>
            </div>

            {loading ? (
                <div className="text-center py-12 text-muted-foreground">Loading profiles...</div>
            ) : profiles.length === 0 ? (
                <div className="rounded-lg border border-dashed p-12 text-center text-muted-foreground">
                    <p>No profiles found. Create one to get started.</p>
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {profiles.map((profile) => (
                        <div key={profile.id} className="rounded-lg border bg-card text-card-foreground shadow-sm p-6 hover:shadow-md transition-shadow">
                            <h3 className="font-semibold text-xl mb-2">{profile.business_name}</h3>
                            <p className="text-sm text-muted-foreground mb-4">{profile.industry || 'Unknown Industry'}</p>
                            <div className="flex flex-wrap gap-2 mb-4">
                                {profile.products?.slice(0, 3).map((p, i) => (
                                    <span key={i} className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                        {p}
                                    </span>
                                ))}
                                {profile.products && profile.products.length > 3 && (
                                    <span className="text-xs text-muted-foreground self-center">+{profile.products.length - 3} more</span>
                                )}
                            </div>
                            <Link href={`/dashboard/profiles/${profile.id}`} className="text-sm font-medium hover:underline text-primary">
                                View Details &rarr;
                            </Link>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
