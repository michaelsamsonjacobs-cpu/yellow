'use client';

import { Card } from '@/components/ui/Card';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export default function HowItWorksPage() {
    return (
        <div className="container" style={{ padding: '4rem 1rem' }}>

            {/* Header */}
            <div style={{ textAlign: 'center', maxWidth: '800px', margin: '0 auto 4rem' }}>
                <h1 style={{ fontSize: '3rem', marginBottom: '1.5rem' }}>The Yellow Standard</h1>
                <p style={{ fontSize: '1.25rem' }}>
                    We don't just guess. We trained an AI editor on the
                    <a href="https://www.spj.org/ethicscode.asp" target="_blank" className="highlight" style={{ margin: '0 0.5rem' }}>SPJ Code of Ethics</a>
                    to hold every article accountable to the same standard.
                </p>
            </div>

            {/* The Rubric */}
            <section style={{ marginBottom: '6rem' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '3rem' }}>The Scoring Rubric</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>

                    <Card className="p-6" style={{ padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
                        <h3>1. Verification (40%)</h3>
                        <p>Does the story rely on single sources? Are official narratives challenged? We deduct points for anonymous sourcing without explanation and unverified claims.</p>
                    </Card>

                    <Card className="p-6" style={{ padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚖️</div>
                        <h3>2. Neutrality (30%)</h3>
                        <p>We flag "loaded language"—words chosen to evoke emotion rather than inform (e.g., "blasts," "scheme," "disastrous"). Facts should speak for themselves.</p>
                    </Card>

                    <Card className="p-6" style={{ padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤝</div>
                        <h3>3. Fairness (30%)</h3>
                        <p>Are opposing views represented? Is there a right of reply? Does the headline match the story? We ensure the reporting is complete and honest.</p>
                    </Card>

                    <Card className="p-6" style={{ padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤫</div>
                        <h3>4. Bias by Omission</h3>
                        <p>It’s not just about what they write; it’s about what they <em>don’t</em> write. Our <strong>Silence Detector</strong> flags stories that the world is talking about but mainstream outlets are ignoring.</p>
                    </Card>

                    <Card className="p-6" style={{ padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🌍</div>
                        <h3>5. The UN Factor (Manual Skew)</h3>
                        <p>We penalize "Selective Neutrality." A source that is neutral on sports and weather but carries extreme bias on foreign policy or elections is dinged with a <strong>Skew Penalty</strong>. We calculate variance across 20+ specific topics to find hidden agendas.</p>
                    </Card>

                </div>
            </section>

            {/* The Process */}
            <section style={{ backgroundColor: 'var(--color-black)', color: 'white', padding: '4rem', marginLeft: '-1rem', marginRight: '-1rem', borderRadius: '8px' }}>
                <h2 style={{ color: 'var(--color-yellow)', textAlign: 'center', marginBottom: '3rem' }}>How It Works</h2>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '700px', margin: '0 auto' }}>
                    <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                        <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--color-yellow)' }}>01</div>
                        <div>
                            <h3 style={{ color: 'white' }}>Daily Scan</h3>
                            <p style={{ color: '#ccc' }}>Every morning at 6 AM, we scan the top 25+ news outlets (NYT, Fox, CNN, Politico, WSJ, etc.) for the biggest stories of the day.</p>
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                        <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--color-yellow)' }}>02</div>
                        <div>
                            <h3 style={{ color: 'white' }}>AI Analysis</h3>
                            <p style={{ color: '#ccc' }}>Our engine reads every article, comparing it against wire services (AP/Reuters) and checking for 15+ types of bias.</p>
                        </div>
                    </div>

                    <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                        <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--color-yellow)' }}>03</div>
                        <div>
                            <h3 style={{ color: 'white' }}>The Fair Redraft</h3>
                            <p style={{ color: '#ccc' }}>If a score drops below 70, we rewrite it. We keep 100% of the facts and quotes but strip the spin.</p>
                        </div>
                    </div>
                </div>

                <div style={{ textAlign: 'center', marginTop: '3rem' }}>
                    <Link href="/dashboard">
                        <Button size="lg" style={{ backgroundColor: 'var(--color-yellow)', color: 'black' }}>See It In Action</Button>
                    </Link>
                </div>
            </section>

        </div>
    );
}
