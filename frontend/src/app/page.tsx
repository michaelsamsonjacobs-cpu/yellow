'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function LandingPage() {
    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-charcoal dark:text-white min-h-screen relative">
            <div className="fixed inset-0 pointer-events-none z-50 opacity-5" style={{ backgroundImage: 'url(https://lh3.googleusercontent.com/aida-public/AB6AXuBoDPx2hinQuKcewp83ofQV7CiPP-YPz8aGsBbvvXoPg9DLWwTlrl-LocvyDy3kbXRQlr-lcXgo40aX2wp9u9bGpMlaMYMpqIy8gCByzsLGe-t9waJtcsICXZT69mKyC-mOnlInANpm2BsIDMRtTg6Qtb8rpOTXPeFG4xBGwcnpvsUOYbsbSlGLYDwtiJaL1cLeqF9b3j8MB3qv3rwWjPQG5v0FG7yPcfidzPE9RYZLilW5Ar9LGDRPlDpiXnwDlFYlzenCy7fg279f)' }}></div>

            <main className="max-w-md mx-auto pb-20 pt-10">
                {/* Hero Section */}
                <section className="relative px-6 pt-12 pb-8 border-b border-black dark:border-white/20">
                    <div className="space-y-6">
                        <div className="inline-block px-2 py-1 bg-primary text-background-dark font-mono text-[10px] font-bold tracking-widest uppercase">
                            Classified Document #772-B
                        </div>
                        <h1 className="text-5xl font-extrabold leading-[0.9] tracking-tighter">
                            The News,<br />Redacted.
                        </h1>
                        <p className="font-mono text-sm opacity-70 leading-relaxed max-w-[280px]">
                            Stripping bias from global media using high-fidelity intelligence protocols.
                        </p>
                        <div className="pt-4">
                            <Link href="/dashboard">
                                <button className="w-full bg-primary hover:bg-yellow-400 text-background-dark font-mono font-bold py-4 px-6 border-b-4 border-r-4 border-black/30 flex items-center justify-between group">
                                    <span>ACCESS INTEL HUB</span>
                                    <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform">arrow_forward</span>
                                </button>
                            </Link>
                        </div>
                    </div>
                </section>

                {/* Live Integrity Ticker */}
                <div className="bg-primary overflow-hidden whitespace-nowrap py-3 border-y border-black">
                    <div className="inline-block animate-[marquee_20s_linear_infinite] font-mono text-background-dark font-bold text-xs uppercase tracking-tighter" style={{ animation: 'marquee 20s linear infinite' }}>
                        <span className="mx-4">● NYT: <span className="underline">92</span></span>
                        <span className="mx-4">● FOX: <span className="underline">65</span></span>
                        <span className="mx-4">● BBC: <span className="underline">88</span></span>
                        <span className="mx-4">● AP: <span className="underline">94</span></span>
                        <span className="mx-4">● WSJ: <span className="underline">89</span></span>
                        <span className="mx-4">● REUTERS: <span className="underline">96</span></span>
                        <span className="mx-4">● NYT: 92</span>
                        <span className="mx-4">● FOX: 65</span>
                    </div>
                </div>

                <style jsx>{`
                    @keyframes marquee {
                        0% { transform: translateX(0); }
                        100% { transform: translateX(-50%); }
                    }
                `}</style>

                {/* Section Header */}
                <div className="px-6 pt-10 pb-4">
                    <h3 className="font-mono text-[10px] font-black tracking-[0.3em] uppercase opacity-50 flex items-center gap-2">
                        <span className="h-px w-8 bg-current"></span>
                        Core Methodology
                    </h3>
                </div>

                {/* Classified Grid */}
                <section className="px-4 space-y-8 pb-12">
                    {/* Folder 1: Verification */}
                    <Link href="/how-it-works" className="block relative group cursor-pointer hover:-translate-y-1 transition-transform">
                        <div className="absolute -top-4 left-0 w-24 h-4 bg-manila dark:bg-manila/90 border-t border-l border-r border-black/20" style={{ clipPath: 'polygon(0 0, 70% 0, 100% 100%, 0% 100%)' }}></div>
                        <div className="bg-manila dark:bg-manila/90 text-background-dark p-6 border border-black/20 shadow-sm relative z-10">
                            <div className="absolute top-4 right-4 border-2 border-red-700/40 text-red-700/40 font-mono text-[10px] font-black p-1 rotate-12 select-none pointer-events-none">TOP SECRET</div>
                            <div className="flex items-start justify-between mb-8">
                                <span className="material-symbols-outlined text-4xl">fact_check</span>
                                <span className="font-mono text-xs opacity-60">REF: VER-01</span>
                            </div>
                            <h4 className="text-2xl font-bold mb-2 tracking-tight">Verification</h4>
                            <p className="font-mono text-xs leading-relaxed opacity-80">Cross-referencing 10,000+ data points per second to validate source authenticity.</p>
                        </div>
                    </Link>

                    {/* Folder 2: Neutrality */}
                    <div className="relative group">
                        <div className="absolute -top-4 left-0 w-24 h-4 bg-manila dark:bg-manila/90 border-t border-l border-r border-black/20" style={{ clipPath: 'polygon(0 0, 70% 0, 100% 100%, 0% 100%)' }}></div>
                        <div className="bg-manila dark:bg-manila/90 text-background-dark p-6 border border-black/20 shadow-sm relative z-10">
                            <div className="flex items-start justify-between mb-8">
                                <span className="material-symbols-outlined text-4xl">balance</span>
                                <span className="font-mono text-xs opacity-60">REF: NEU-44</span>
                            </div>
                            <h4 className="text-2xl font-bold mb-2 tracking-tight">Neutrality</h4>
                            <p className="font-mono text-xs leading-relaxed opacity-80">Linguistic fingerprinting to identify subjective adjectives and manipulative framing.</p>
                        </div>
                    </div>

                    {/* Folder 3: Omission Analysis */}
                    <Link href="/admin/omission" className="block relative group cursor-pointer hover:-translate-y-1 transition-transform">
                        <div className="absolute -top-4 left-0 w-24 h-4 bg-manila dark:bg-manila/90 border-t border-l border-r border-black/20" style={{ clipPath: 'polygon(0 0, 70% 0, 100% 100%, 0% 100%)' }}></div>
                        <div className="bg-manila dark:bg-manila/90 text-background-dark p-6 border border-black/20 shadow-sm relative z-10">
                            <div className="absolute top-4 right-8 border-2 border-red-700/40 text-red-700/40 font-mono text-[10px] font-black p-1 rotate-3 select-none pointer-events-none uppercase">High Priority</div>
                            <div className="flex items-start justify-between mb-8">
                                <span className="material-symbols-outlined text-4xl">visibility_off</span>
                                <span className="font-mono text-xs opacity-60">REF: OMI-99</span>
                            </div>
                            <h4 className="text-2xl font-bold mb-2 tracking-tight">Silence Detection</h4>
                            <p className="font-mono text-xs leading-relaxed opacity-80">
                                <strong>Bias by Omission:</strong> Comparing Reddit/Google trends vs. Corporate Media to find what they <em>aren't</em> telling you.
                            </p>
                            <div className="mt-6 pt-4 border-t border-black/10 flex justify-between items-center font-mono text-[10px] font-bold">
                                <span>STATUS: ACTIVE</span>
                                <span className="text-primary-700">GAP ANALYSIS ON</span>
                            </div>
                        </div>
                    </Link>
                </section>
            </main>
        </div>
    );
}
