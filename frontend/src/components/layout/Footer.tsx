'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { api } from '@/lib/api';

export function Footer() {
    const [email, setEmail] = useState('');
    const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

    async function handleSubscribe(e: React.FormEvent) {
        e.preventDefault();
        setStatus('loading');
        try {
            // In a real app we'd call the API, but for static demo we'll just simulate
            // await api.subscribeToNewsletter(email); 
            await new Promise(resolve => setTimeout(resolve, 1000));
            setStatus('success');
            setEmail('');
        } catch (err) {
            setStatus('error');
        }
    }

    return (
        <footer style={{ backgroundColor: 'var(--color-black)', color: 'white', padding: '4rem 0', marginTop: 'auto' }}>
            <div className="container">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '3rem', marginBottom: '3rem' }}>

                    {/* Brand */}
                    <div>
                        <h3 style={{ fontFamily: 'var(--font-headline)', fontSize: '1.5rem', color: 'var(--color-yellow)', marginBottom: '1rem' }}>YELLOW</h3>
                        <p style={{ color: '#aaa', lineHeight: '1.6' }}>
                            The world's first AI Editor trained on the SPJ Code of Ethics. Hold the press accountable.
                        </p>
                    </div>

                    {/* Links */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <h4 style={{ color: 'var(--color-yellow)', marginBottom: '0.5rem' }}>Company</h4>
                        <Link href="/how-it-works" className="hover:text-[var(--color-yellow)]">How It Works</Link>
                        <Link href="/pricing" className="hover:text-[var(--color-yellow)]">Pricing</Link>
                        <Link href="/outlets" className="hover:text-[var(--color-yellow)]">Outlet Rankings</Link>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <h4 style={{ color: 'var(--color-yellow)', marginBottom: '0.5rem' }}>Legal</h4>
                        <Link href="/privacy" className="hover:text-[var(--color-yellow)]">Privacy Policy</Link>
                        <Link href="/terms" className="hover:text-[var(--color-yellow)]">Terms of Service</Link>
                    </div>

                    {/* Newsletter */}
                    <div>
                        <h4 style={{ color: 'var(--color-yellow)', marginBottom: '1rem' }}>The Daily Briefing</h4>
                        <p style={{ color: '#aaa', marginBottom: '1rem', fontSize: '0.9rem' }}>
                            Get the top stories (and their bias scores) in your inbox. Free.
                        </p>

                        {status === 'success' ? (
                            <div style={{ color: 'var(--color-green)', fontWeight: 'bold' }}>You're in! Check your inbox.</div>
                        ) : (
                            <form onSubmit={handleSubscribe} style={{ display: 'flex', gap: '0.5rem' }}>
                                <input
                                    type="email"
                                    placeholder="woodward@post.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    style={{ flex: 1, padding: '0.5rem', borderRadius: '4px', border: 'none', color: 'black' }}
                                />
                                <Button type="submit" size="sm" isLoading={status === 'loading'} style={{ backgroundColor: 'var(--color-yellow)', color: 'black' }}>
                                    Subscribe
                                </Button>
                            </form>
                        )}
                    </div>

                </div>

                <div style={{ borderTop: '1px solid #333', paddingTop: '2rem', textAlign: 'center', color: '#666', fontSize: '0.9rem' }}>
                    &copy; {new Date().getFullYear()} Yellow. All rights reserved.
                </div>
            </div>
        </footer>
    );
}
