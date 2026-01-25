'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { useAuth } from '@/components/auth/AuthContext';
import { Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Article {
    id: string;
    headline: string;
    outlet_name: string;
    integrity_score: number;
    published_at: string;
    keywords: string[];
    analysis: any;
}

export default function DashboardPage() {
    const { user, loading: authLoading } = useAuth();
    const [articles, setArticles] = useState<Article[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            try {
                const recent = await api.getRecentArticles();
                setArticles(recent as any);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }

        if (user) loadData();
    }, [user]);

    if (authLoading || loading) {
        return (
            <div className="min-h-screen bg-background-light dark:bg-background-dark flex items-center justify-center">
                <Loader2 className="animate-spin text-primary" size={32} />
            </div>
        );
    }

    if (!user) {
        return (
            <div className="min-h-screen bg-background-light dark:bg-background-dark flex flex-col items-center justify-center p-8 text-center font-mono text-white">
                <h2 className="mb-4 text-xl">Clearance Level: UNVERIFIED</h2>
                <Link href="/login" className="text-primary hover:underline">&gt;&gt; AUTHENTICATE &lt;&lt;</Link>
            </div>
        )
    }

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-white overflow-hidden h-screen flex w-full">

            {/* Column 1: Sidebar */}
            <aside className="hidden md:flex flex-col items-center w-16 h-full bg-black/40 border-r border-primary/10 py-6 shrink-0 z-20">
                <div className="mb-8 text-primary">
                    <span className="material-symbols-outlined text-3xl">terminal</span>
                </div>
                <nav className="flex flex-col gap-8 flex-1">
                    <Link href="/dashboard" className="flex flex-col items-center text-primary active-nav-border pl-1 shadow-[-2px_0_0_0_#f9d406]">
                        <span className="material-symbols-outlined">bolt</span>
                    </Link>
                    <Link href="/outlets" className="flex flex-col items-center text-primary/40 hover:text-primary transition-colors">
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

            {/* Main Area */}
            <div className="flex flex-1 overflow-x-auto snap-x snap-mandatory scrollbar-hide">

                {/* Column 2: Main Feed */}
                <main className="w-full md:w-[600px] md:flex-none shrink-0 snap-start flex flex-col h-full relative border-r border-primary/10">
                    {/* Mobile Header */}
                    <header className="flex md:hidden items-center bg-background-dark p-4 justify-between border-b border-primary/10">
                        <h2 className="text-primary text-xs font-bold uppercase">Yellow Intel</h2>
                        <div className="size-2 rounded-full bg-primary animate-pulse"></div>
                    </header>

                    {/* Desktop Header info */}
                    <div className="hidden md:flex items-center bg-background-dark p-4 pb-2 justify-between border-b border-primary/10">
                        <div className="flex flex-col">
                            <h2 className="text-primary text-xs font-bold leading-tight tracking-[0.2em] uppercase">Intelligence Center</h2>
                            <div className="flex items-center gap-1.5">
                                <div className="size-1.5 rounded-full bg-primary status-pulse" style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }}></div>
                                <span className="text-[10px] text-primary/60 uppercase tracking-widest">System Live</span>
                            </div>
                        </div>
                        <div className="flex gap-4">
                            <span className="material-symbols-outlined text-white/40">notifications</span>
                        </div>
                    </div>

                    {/* Feed Header */}
                    <div className="px-4 py-3 bg-background-dark/80 backdrop-blur-md sticky top-0 z-10 border-b border-white/5">
                        <h1 className="text-white text-xl font-bold tracking-tight uppercase">Bias Radar <span className="text-primary/40">/ LIVE</span></h1>
                    </div>

                    {/* Feed Content */}
                    <div className="flex-1 overflow-y-auto px-4 pb-24 space-y-4 pt-4">
                        {articles.length === 0 && (
                            <div className="text-center p-8 opacity-50">
                                <p className="mb-4">No intercepts found.</p>
                                <Link href="/admin/scrape" className="text-primary border border-primary/50 px-4 py-2 rounded text-sm uppercase font-bold hover:bg-primary/10">Initialize Scraper</Link>
                            </div>
                        )}

                        {articles.map((article) => (
                            <div key={article.id} className="glass-card rounded-xl p-4 flex flex-col gap-4 group" style={{ background: 'rgba(35, 32, 15, 0.6)', backdropFilter: 'blur(12px)', border: '1px solid rgba(249, 212, 6, 0.1)' }}>
                                <div className="flex justify-between items-start">
                                    <div className="relative w-16 h-16 shrink-0">
                                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 64 64">
                                            <circle className="text-white/10" cx="32" cy="32" fill="transparent" r="28" stroke="currentColor" strokeWidth="4"></circle>
                                            <circle
                                                className={article.integrity_score >= 80 ? "text-primary" : "text-red-500"}
                                                cx="32" cy="32" fill="transparent" r="28" stroke="currentColor"
                                                strokeDasharray={`${(article.integrity_score / 100) * 175.9} 175.9`}
                                                strokeWidth="4"
                                                style={{ transition: 'stroke-dasharray 1s ease' }}>
                                            </circle>
                                        </svg>
                                        <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-primary">{article.integrity_score}</span>
                                    </div>
                                    <div className="bg-primary/10 text-primary text-[10px] font-bold px-2 py-0.5 rounded border border-primary/20 uppercase">
                                        {article.outlet_name}
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <h3 className="text-white text-lg font-bold leading-tight hover:text-primary transition-colors">
                                        <Link href={`/articles/${article.id}`}>{article.headline}</Link>
                                    </h3>
                                    <p className="text-white/60 text-xs leading-relaxed line-clamp-2">
                                        {article.analysis?.topic ? `Topic: ${article.analysis.topic}` : 'Analyzing vector space...'}
                                    </p>
                                </div>
                                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                                    <div className="flex gap-2">
                                        {article.keywords?.slice(0, 2).map((k, i) => (
                                            <span key={i} className="text-[10px] uppercase text-white/40 tracking-wider bg-white/5 px-1 rounded">{k}</span>
                                        ))}
                                    </div>
                                    <Link href={`/articles/${article.id}`}>
                                        <button className="bg-primary text-black text-xs font-bold py-2 px-4 rounded-lg uppercase tracking-tight active:scale-95 transition-transform">
                                            Redraft
                                        </button>
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                </main>

                {/* Column 3: Silence Scale (Desktop) */}
                <aside className="hidden md:flex w-full md:w-80 shrink-0 snap-start bg-black/60 border-l border-primary/10 flex-col h-full p-6">
                    <h2 className="text-primary text-xs font-bold tracking-[0.2em] uppercase mb-6 flex items-center gap-2">
                        <span className="material-symbols-outlined text-sm">volume_off</span>
                        Silence Scale
                    </h2>

                    <div className="space-y-6">
                        {/* Mock Data for now - connects to Omission visually */}
                        <div className="space-y-2">
                            <div className="flex justify-between text-[10px] uppercase tracking-widest font-medium">
                                <span className="text-white/60">Topic: Supply Chain</span>
                                <span className="text-primary">92% Ignored</span>
                            </div>
                            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-primary w-[92%]"></div>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <div className="flex justify-between text-[10px] uppercase tracking-widest font-medium">
                                <span className="text-white/60">Digital Currency</span>
                                <span className="text-primary">84% Ignored</span>
                            </div>
                            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-primary w-[84%] shadow-[0_0_10px_rgba(249,212,6,0.3)]"></div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-12 glass-card rounded-lg p-4 border-l-4 border-primary" style={{ background: 'rgba(35, 32, 15, 0.6)' }}>
                        <div className="text-[10px] text-primary font-bold uppercase mb-2 tracking-tighter">Executive Briefing</div>
                        <p className="text-xs text-white/80 italic leading-normal">
                            "The mainstream media blackout on the upcoming trade accord is reaching critical levels."
                        </p>
                    </div>
                </aside>
            </div>

            {/* Bottom Nav Mobile */}
            <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-md h-16 glass-card rounded-full flex items-center justify-around px-6 z-50 shadow-2xl border border-white/10 md:hidden" style={{ background: 'rgba(35, 32, 15, 0.9)', backdropFilter: 'blur(12px)' }}>
                <Link href="/dashboard" className="text-primary"><span className="material-symbols-outlined text-2xl">home</span></Link>
                <Link href="/outlets" className="text-white/40"><span className="material-symbols-outlined text-2xl">radar</span></Link>
                <div className="size-12 bg-primary rounded-full flex items-center justify-center -translate-y-6 shadow-[0_8px_20px_rgba(249,212,6,0.4)]">
                    <span className="material-symbols-outlined text-black font-bold">add</span>
                </div>
                <Link href="/admin/omission" className="text-white/40"><span className="material-symbols-outlined text-2xl">newspaper</span></Link>
                <Link href="/settings" className="text-white/40"><span className="material-symbols-outlined text-2xl">person</span></Link>
            </div>
        </div>
    );
}
