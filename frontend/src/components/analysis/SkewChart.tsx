'use client';

import { useMemo } from 'react';

interface SkewStats {
    score: number;
    count: number;
    deviation: number;
}

interface SkewData {
    global_score: number;
    category_scores: Record<string, SkewStats>;
    skew_penalty: number;
    high_skew_categories: Array<{ category: string; deviation: number }>;
}

export function SkewChart({ data }: { data: SkewData }) {
    // Transform data for the radar chart
    // We want at least 3-4 categories for a polygon, ideally more
    const categories = Object.entries(data.category_scores)
        .sort((a, b) => b[1].count - a[1].count) // Sort by most articles
        .slice(0, 8); // Top 8 categories

    const radius = 100;
    const center = 120;

    // Calculate points for the polygon
    const points = useMemo(() => {
        const total = categories.length;
        if (total < 3) return null;

        return categories.map(([label, stats], i) => {
            const angle = (Math.PI * 2 * i) / total - Math.PI / 2;
            const value = stats.score; // 0-100

            // Map 0-100 to radius distance
            const r = (value / 100) * radius;

            const x = center + Math.cos(angle) * r;
            const y = center + Math.sin(angle) * r;

            return { x, y, value, label, angle };
        });
    }, [categories]);

    if (!points) {
        return <div className="text-center p-4 text-xs font-mono opacity-50">Not enough data for Topography Map</div>;
    }

    const polygonPath = points.map(p => `${p.x},${p.y}`).join(' ');

    return (
        <div className="bg-background-light dark:bg-card-dark border border-black dark:border-white/10 p-4 rounded-sm">
            <h4 className="font-mono text-xs font-bold uppercase tracking-widest mb-4 border-b border-black/10 pb-2 flex justify-between">
                <span>Bias Topography</span>
                {data.skew_penalty > 0 && <span className="text-red-600">SKEW PENALTY: -{data.skew_penalty}</span>}
            </h4>

            <div className="flex flex-col md:flex-row gap-6 items-center">

                {/* Radar Chart */}
                <div className="relative w-[240px] h-[240px]">
                    <svg width="240" height="240" viewBox="0 0 240 240">
                        {/* Background Circles */}
                        {[25, 50, 75, 100].map(r => (
                            <circle
                                key={r}
                                cx={center}
                                cy={center}
                                r={r}
                                fill="none"
                                stroke="currentColor"
                                strokeOpacity="0.1"
                                strokeDasharray="2 2"
                            />
                        ))}

                        {/* Axes */}
                        {points.map((p, i) => (
                            <line
                                key={i}
                                x1={center}
                                y1={center}
                                x2={center + Math.cos(p.angle) * radius}
                                y2={center + Math.sin(p.angle) * radius}
                                stroke="currentColor"
                                strokeOpacity="0.1"
                            />
                        ))}

                        {/* Global Average Reference (Circle) */}
                        <circle
                            cx={center}
                            cy={center}
                            r={(data.global_score / 100) * radius}
                            fill="none"
                            stroke="var(--color-primary)" // Yellow
                            strokeWidth="2"
                            strokeOpacity="0.5"
                            strokeDasharray="4 4"
                        />

                        {/* The Blob */}
                        <polygon
                            points={polygonPath}
                            fill="rgba(0,0,0,0.1)"
                            stroke="currentColor"
                            strokeWidth="2"
                            className="dark:fill-white/10 dark:stroke-white"
                        />

                        {/* Points */}
                        {points.map((p, i) => (
                            <circle
                                key={i}
                                cx={p.x}
                                cy={p.y}
                                r="3"
                                fill={Math.abs(p.value - data.global_score) > 15 ? 'red' : 'currentColor'}
                            />
                        ))}

                        {/* Labels */}
                        {points.map((p, i) => {
                            const isRight = p.x > center;
                            const isBottom = p.y > center;
                            return (
                                <text
                                    key={i}
                                    x={p.x + (isRight ? 10 : -10)}
                                    y={p.y + (isBottom ? 10 : -5)}
                                    textAnchor={isRight ? 'start' : 'end'}
                                    fontSize="9"
                                    fill="currentColor"
                                    className="font-mono"
                                    opacity="0.7"
                                >
                                    {p.label}
                                </text>
                            );
                        })}
                    </svg>
                </div>

                {/* Stats */}
                <div className="flex-1 space-y-3">
                    <div className="text-xs font-mono">
                        <div className="flex justify-between mb-1">
                            <span className="opacity-50">Global Baseline</span>
                            <span className="font-bold">{data.global_score}/100</span>
                        </div>
                        <div className="w-full bg-black/10 h-1">
                            <div className="bg-primary h-1" style={{ width: `${data.global_score}%` }}></div>
                        </div>
                    </div>

                    {data.high_skew_categories.length > 0 ? (
                        <div className="bg-red-50 dark:bg-red-900/10 p-3 border border-red-200 dark:border-red-900/30">
                            <h5 className="text-red-700 dark:text-red-400 font-bold text-xs mb-2 flex items-center gap-2">
                                <span className="material-symbols-outlined text-sm">warning</span>
                                ACTIVE DISTORTION
                            </h5>
                            <ul className="space-y-1">
                                {data.high_skew_categories.map(cat => (
                                    <li key={cat.category} className="text-[10px] font-mono flex justify-between text-red-600/80 dark:text-red-300/80">
                                        <span className="uppercase">{cat.category}</span>
                                        <span>{cat.deviation > 0 ? '+' : ''}{cat.deviation} deviation</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ) : (
                        <div className="bg-green-50 dark:bg-green-900/10 p-3 border border-green-200 dark:border-green-900/30">
                            <div className="flex items-center gap-2 text-green-700 dark:text-green-400 text-xs font-bold">
                                <span className="material-symbols-outlined text-sm">check_circle</span>
                                CONSISTENT REPORTING
                            </div>
                            <p className="text-[10px] opacity-70 mt-1">
                                Bias variance is within acceptable limits across all topics.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
