'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Outlet } from '@/lib/firestore'; // Import Shared Type
import { Card } from '@/components/ui/Card';
import { Loader2 } from 'lucide-react';

export default function OutletDetailPage({ params }: { params: { id: string } }) {
    const [outlet, setOutlet] = useState<Outlet | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (params.id) {
            api.getOutlet(params.id)
                .then(setOutlet)
                .catch(console.error)
                .finally(() => setLoading(false));
        }
    }, [params.id]);

    if (loading) return <div className="p-8 text-center"><Loader2 className="animate-spin mx-auto" /></div>;
    if (!outlet) return <div className="p-8 text-center">Outlet not found</div>;

    return (
        <div className="container">
            <Link href="/outlets" className="mb-4 inline-block ui-text">← Back to Rankings</Link>

            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                <Card variant="paper" style={{ padding: '3rem', border: '4px solid var(--color-black)' }}>

                    <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                        <div style={{ fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '2px', marginBottom: '0.5rem' }}>INTEGRITY REPORT CARD</div>
                        <h1 style={{ fontSize: '3rem', marginBottom: '2rem' }}>{outlet.name}</h1>

                        <div style={{ display: 'flex', justifyContent: 'center', gap: '3rem' }}>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '4rem', fontWeight: 'bold' }}>{outlet.batting_average}</div>
                                <div style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>BATTING AVG</div>
                            </div>

                            <div style={{ textAlign: 'center' }}>
                                {/* Simple Bias Gauge */}
                                <div style={{ fontSize: '4rem', fontWeight: 'bold' }}>
                                    {outlet.bias_tilt > 0.2 ? 'R' : outlet.bias_tilt < -0.2 ? 'L' : 'C'}
                                </div>
                                <div style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>BIAS LEAN</div>
                            </div>
                        </div>
                    </div>

                    {outlet.top_violations && outlet.top_violations.length > 0 && (
                        <div>
                            <h3 style={{ borderBottom: '2px solid black', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
                                Frequent Violations
                            </h3>
                            <div style={{ display: 'grid', gap: '1rem' }}>
                                {outlet.top_violations.map((v, i) => (
                                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <span style={{ fontSize: '1.1rem' }}>{v.type}</span>
                                        <div style={{ flex: 1, margin: '0 1rem', height: '10px', backgroundColor: '#eee', borderRadius: '5px' }}>
                                            <div style={{ width: `${v.percentage}%`, height: '100%', backgroundColor: 'var(--color-red)', borderRadius: '5px' }}></div>
                                        </div>
                                        <span style={{ fontWeight: 'bold' }}>{v.percentage}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                </Card>
            </div>
        </div>
    );
}
