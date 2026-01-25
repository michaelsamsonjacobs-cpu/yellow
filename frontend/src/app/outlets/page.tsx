'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Outlet } from '@/lib/firestore'; // Import Shared Type
import { useAuth } from '@/components/auth/AuthContext';
import { Loader2 } from 'lucide-react';

export default function OutletsPage() {
    const { user } = useAuth();
    const [outlets, setOutlets] = useState<Outlet[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.getOutlets()
            .then((res) => setOutlets(res))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const getColor = (score: number) => {
        if (score >= 90) return 'text-primary';
        if (score >= 70) return 'text-yellow-400';
        return 'text-red-500';
    };

    return (
        <div className="bg-background-dark font-display text-white overflow-hidden h-screen flex w-full">
            {/* Column 1: Sidebar (Shared Layout) */}
            <aside className="hidden md:flex flex-col items-center w-16 h-full bg-black/40 border-r border-primary/10 py-6 shrink-0 z-20">
                <div className="mb-8 text-primary">
                    <span className="material-symbols-outlined text-3xl">terminal</span>
                </div>
                <nav className="flex flex-col gap-8 flex-1">
                    <Link href="/dashboard" className="flex flex-col items-center text-primary/40 hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">bolt</span>
                    </Link>
                    <Link href="/outlets" className="flex flex-col items-center text-primary active-nav-border pl-1 shadow-[-2px_0_0_0_#f9d406]">
                        <span className="material-symbols-outlined">analytics</span>
                    </Link>
                    <Link href="/admin/omission" className="flex flex-col items-center text-primary/40 hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">folder_managed</span>
                    </Link>
                </nav>
                <div className="mt-auto text-primary/40">
                    <Link href="/settings"><span className="material-symbols-outlined">settings</span></Link>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col h-full overflow-hidden bg-background-dark relative">
                {/* Header */}
                <div className="hidden md:flex items-center bg-background-dark p-4 pb-2 justify-between border-b border-primary/10">
                    <div className="flex flex-col">
                        <h2 className="text-primary text-xs font-bold leading-tight tracking-[0.2em] uppercase">Intelligence Center</h2>
                        <div className="flex items-center gap-1.5">
                            <span className="text-[10px] text-primary/60 uppercase tracking-widest">Global Outlet Index</span>
                        </div>
                    </div>
                </div>

                <div className="px-4 py-3 bg-background-dark/80 backdrop-blur-md sticky top-0 z-10 border-b border-white/5 flex justify-between items-center">
                    <h1 className="text-white text-xl font-bold tracking-tight uppercase">Outlet Integrity <span className="text-primary/40">/ RANKINGS</span></h1>
                </div>

                {/* Grid */}
                {loading ? (
                    <div className="flex-1 flex items-center justify-center">
                        <Loader2 className="animate-spin text-primary" size={32} />
                    </div>
                ) : (
                    <div className="flex-1 overflow-y-auto p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {outlets.map((outlet) => (
                                <Link key={outlet.id} href={`/outlets/${outlet.id}`}>
                                    <div className="group bg-white/5 border border-white/10 hover:border-primary/50 transition-colors rounded-xl p-5 cursor-pointer relative overflow-hidden">
                                        <div className="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-100 transition-opacity">
                                            <span className="material-symbols-outlined text-primary">arrow_outward</span>
                                        </div>

                                        <div className="flex justify-between items-start mb-4">
                                            <div>
                                                <h3 className="text-lg font-bold uppercase tracking-tight leading-none mb-1">{outlet.name}</h3>
                                                <span className="text-[10px] font-mono text-white/40 uppercase tracking-widest">ID: {outlet.id.substring(0, 6)}</span>
                                            </div>
                                            <div className="text-right">
                                                <div className={`text-2xl font-black ${getColor(outlet.batting_average)}`}>
                                                    {outlet.batting_average ?? 0}%
                                                </div>
                                                <div className="text-[9px] text-white/40 uppercase">Integrity</div>
                                            </div>
                                        </div>

                                        <div className="w-full bg-white/10 h-1 rounded-full overflow-hidden mb-4">
                                            <div
                                                className={`h-full ${outlet.batting_average >= 70 ? 'bg-primary' : 'bg-red-500'}`}
                                                style={{ width: `${outlet.batting_average ?? 0}%` }}
                                            ></div>
                                        </div>

                                        <div className="flex justify-between items-center text-[10px] font-mono border-t border-white/10 pt-3">
                                            <span className="text-white/60">{outlet.article_count ?? 0} INTERCEPTS ANALYZED</span>
                                            {outlet.batting_average >= 90 && (
                                                <span className="flex items-center gap-1 text-primary">
                                                    <span className="material-symbols-outlined text-[12px]">verified</span>
                                                    TRUSTED
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </div>
                )}
            </main>

            {/* Mobile Nav */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-md h-16 glass-card rounded-full flex items-center justify-around px-6 z-50 shadow-2xl border border-white/10 md:hidden" style={{ background: 'rgba(35, 32, 15, 0.9)', backdropFilter: 'blur(12px)' }}>
                <Link href="/dashboard" className="text-white/40"><span className="material-symbols-outlined text-2xl">home</span></Link>
                <Link href="/outlets" className="text-primary"><span className="material-symbols-outlined text-2xl">radar</span></Link>
                <div className="size-12 bg-primary rounded-full flex items-center justify-center -translate-y-6 shadow-[0_8px_20px_rgba(249,212,6,0.4)]">
                    <span className="material-symbols-outlined text-black font-bold">add</span>
                </div>
                <Link href="/admin/omission" className="text-white/40"><span className="material-symbols-outlined text-2xl">newspaper</span></Link>
                <Link href="/settings" className="text-white/40"><span className="material-symbols-outlined text-2xl">person</span></Link>
            </div>
        </div>
    );
}
