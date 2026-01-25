'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Loader2 } from 'lucide-react';

interface Article {
    id: string;
    headline: string;
    original_text: string;
    integrity_score: number;
    analysis: any;
}

export default function ArticlePage() {
    const params = useParams();
    const [article, setArticle] = useState<Article | null>(null);

    useEffect(() => {
        if (params?.id) {
            api.getArticle(params.id as string).then((res) => setArticle(res as any)).catch(console.error);
        }
    }, [params]);

    if (!article) return <div className="h-screen flex items-center justify-center bg-background-dark text-primary"><Loader2 className="animate-spin" /></div>;

    const redraftPlaceholder = article.analysis?.topic
        ? `[AUTO-REDRAFT GENERATED]\n\nAnalysis indicates bias in original reporting regarding ${article.analysis.topic}.\n\nNeutralized summary:\n\nThe event described involves complex status updates from verified sources. Unlike the original text which used phrases like "radical departure", the objective reality is a legislative change proposed on Tuesday...`
        : "Generating neutral redraft based on SPJ Code of Ethics...";

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-white min-h-screen">
            {/* Top Navigation Bar */}
            <div className="sticky top-0 z-50 flex items-center bg-background-dark/95 backdrop-blur-md p-4 pb-2 justify-between border-b border-[#4a4421]">
                <Link href="/dashboard" className="text-white flex size-10 shrink-0 items-center justify-center rounded-full hover:bg-white/10">
                    <span className="material-symbols-outlined">arrow_back</span>
                </Link>
                <div className="flex flex-col items-center">
                    <h2 className="text-white text-sm font-bold leading-tight tracking-tight">The Diff Engine</h2>
                    <p className="text-[10px] text-[#ccc38e] uppercase tracking-[0.2em]">Watergate Modern Intelligence</p>
                </div>
                <div className="flex w-10 items-center justify-end">
                    <span className="material-symbols-outlined text-primary">analytics</span>
                </div>
            </div>

            {/* Floating Integrity Badge Section */}
            <div className="flex items-center justify-between p-4 gap-4">
                <div className="flex min-w-[140px] flex-1 items-center gap-3 rounded-xl p-4 bg-[#353018] border border-[#4a4421]">
                    <div className="flex flex-col">
                        <p className="text-[#ccc38e] text-[10px] font-bold uppercase tracking-wider">Integrity Score</p>
                        <p className="text-primary text-2xl font-bold leading-tight">{article.integrity_score}/100</p>
                    </div>
                    <div className="h-8 w-[1px] bg-[#4a4421]"></div>
                    <div className="flex flex-col">
                        <p className="text-[#0bda20] text-xs font-bold leading-none">+12%</p>
                        <p className="text-[#ccc38e] text-[10px]">vs Average</p>
                    </div>
                </div>
                <button className="bg-primary text-background-dark px-4 py-3 rounded-xl font-bold text-sm shadow-lg shadow-primary/10 flex items-center gap-2">
                    <span className="material-symbols-outlined text-lg">description</span>
                    Methodology
                </button>
            </div>

            {/* Split Screen Document Viewer */}
            <div className="relative flex flex-col mt-4">
                {/* Headers */}
                <div className="flex px-4 py-2 bg-background-dark sticky top-[60px] z-40 border-b border-[#4a4421]">
                    <div className="w-[48%] flex items-center gap-2">
                        <span className="material-symbols-outlined text-red-500 text-sm">error</span>
                        <span className="text-[10px] font-bold uppercase text-[#ccc38e]">Original Article</span>
                    </div>
                    <div className="w-[4%]"></div>
                    <div className="w-[48%] flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary text-sm">verified</span>
                        <span className="text-[10px] font-bold uppercase text-[#ccc38e]">Yellow Redraft</span>
                    </div>
                </div>

                <div className="flex px-2 pt-4 relative">
                    {/* Left Pane: Original Article */}
                    <div className="w-[48%] rounded-lg p-3 bg-[#2a2715] border border-[#4a4421] shadow-inner" style={{ backgroundImage: 'radial-gradient(#3a3620 0.5px, transparent 0.5px)', backgroundSize: '4px 4px' }}>
                        <div className="font-serif-article text-xs leading-relaxed text-[#d1d1c1] whitespace-pre-wrap">
                            <h1 className="text-lg font-bold mb-4 text-white">{article.headline}</h1>
                            {article.original_text}
                        </div>
                    </div>

                    {/* Center Gutter */}
                    <div className="w-[4%] flex flex-col items-center pt-2 relative">
                        <div className="absolute inset-y-0 w-[1px] left-1/2 -translate-x-1/2" style={{ background: 'linear-gradient(to bottom, #f9d406 0%, #f9d406 20%, transparent 20%, transparent 100%)', backgroundSize: '1px 10px' }}></div>
                        <div className="z-10 bg-[#f9d406] text-background-dark text-[8px] font-bold rounded-full w-5 h-5 flex items-center justify-center mb-16 border-2 border-background-dark">2</div>
                    </div>

                    {/* Right Pane: Yellow Redraft */}
                    <div className="w-[48%] rounded-lg p-3 bg-[#1a180b] border border-[#4a4421]">
                        <div className="font-display text-xs leading-relaxed text-white whitespace-pre-wrap">
                            {redraftPlaceholder}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
