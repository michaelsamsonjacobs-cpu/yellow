'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/components/auth/AuthContext';
import { Button } from '@/components/ui/Button';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [sent, setSent] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { loginWithGoogle, loginWithEmail } = useAuth();

    async function handleEmailSubmit(e: React.FormEvent) {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await loginWithEmail(email);
            setSent(true);
        } catch (err: any) {
            setError(err.message || 'Failed to send magic link. Please try again.');
        } finally {
            setLoading(false);
        }
    }

    async function handleGoogleSignIn() {
        setLoading(true);
        setError('');
        try {
            await loginWithGoogle();
        } catch (err: any) {
            setError(err.message || 'Failed to sign in with Google.');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-background-dark flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-[#1a180b] border border-primary/20 rounded-lg p-8 shadow-2xl relative overflow-hidden">
                {/* Decorative Top Bar */}
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50"></div>

                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center size-12 bg-primary/10 rounded-full mb-4 border border-primary/20">
                        <span className="material-symbols-outlined text-primary">lock_open</span>
                    </div>
                    <h1 className="text-2xl font-bold text-white uppercase tracking-widest">Identify Yourself</h1>
                    <p className="text-white/40 text-xs font-mono mt-2 uppercase tracking-wider">Clearance Level 4 Required</p>
                </div>

                {sent ? (
                    <div className="text-center animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="size-16 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4 border border-green-500/30">
                            <span className="material-symbols-outlined text-3xl">mail</span>
                        </div>
                        <h3 className="text-white text-lg font-bold mb-2">Check your comms</h3>
                        <p className="text-white/60 text-sm mb-6">Secure link dispatched to <strong className="text-white">{email}</strong></p>
                        <button
                            onClick={() => setSent(false)}
                            className="text-primary text-xs uppercase tracking-widest hover:underline hover:text-primary/80 transition-colors"
                        >
                            Use different coordinates
                        </button>
                    </div>
                ) : (
                    <>
                        <button
                            onClick={handleGoogleSignIn}
                            disabled={loading}
                            className="w-full h-12 bg-white text-black font-bold uppercase tracking-wide rounded flex items-center justify-center gap-3 hover:bg-gray-200 transition-colors mb-6 text-sm"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24">
                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                            </svg>
                            Authenticate with Google
                        </button>

                        <div className="flex items-center gap-4 mb-6">
                            <div className="flex-1 h-px bg-white/10"></div>
                            <span className="text-[10px] text-white/30 uppercase tracking-widest">Or via encrypted link</span>
                            <div className="flex-1 h-px bg-white/10"></div>
                        </div>

                        <form onSubmit={handleEmailSubmit} className="space-y-4">
                            <div>
                                <label htmlFor="email" className="sr-only">Email Address</label>
                                <input
                                    type="email"
                                    id="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="operative@yellow.intel"
                                    required
                                    className="w-full bg-black/40 border border-white/10 rounded px-4 py-3 text-white placeholder:text-white/20 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all font-mono text-sm"
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full h-12 bg-primary text-black font-bold uppercase tracking-widest rounded hover:brightness-110 transition-all shadow-[0_0_20px_rgba(249,212,6,0.1)] hover:shadow-[0_0_30px_rgba(249,212,6,0.3)] disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Transmitting...' : 'Send Magic Link'}
                            </button>
                        </form>

                        {error && (
                            <div className="mt-6 p-3 bg-red-500/10 border border-red-500/20 rounded text-red-500 text-xs text-center flex items-center justify-center gap-2">
                                <span className="material-symbols-outlined text-sm">warning</span>
                                {error}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
