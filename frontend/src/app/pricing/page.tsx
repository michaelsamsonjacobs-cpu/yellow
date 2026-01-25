'use client';

import { useState } from 'react';
import { useAuth } from '@/components/auth/AuthContext';
import { createCheckoutSession } from '@/lib/stripe';
import { Loader2 } from 'lucide-react';

export default function PricingPage() {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);

    // Replace with your actual Stripe Price ID
    const PRICE_ID = 'price_1Q5x...'; // Placeholder

    async function handleSubscribe() {
        if (!user) {
            window.location.href = '/login';
            return;
        }

        setLoading(true);
        try {
            // Note: This requires the "Run Payments with Stripe" Firebase extension to be installed
            // configured with the "users" collection.
            const url = await createCheckoutSession(user.id, PRICE_ID);
            window.location.href = url;
        } catch (error) {
            console.error(error);
            alert('Failed to start checkout. Ensure Firebase Stripe Extension is configured.');
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-background-dark font-display text-white flex flex-col items-center justify-center p-4">
            {/* Decorative Top Bar */}
            <div className="fixed top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50"></div>

            <div className="text-center mb-12">
                <h1 className="text-4xl font-black uppercase tracking-tighter mb-4 text-primary">Upgrade Clearance</h1>
                <p className="text-white/60 font-mono text-sm uppercase tracking-widest">Access Level 5: Real-Time Intelligence</p>
            </div>

            <div className="w-full max-w-sm bg-[#1a180b] border border-primary rounded-xl p-8 relative shadow-[0_0_50px_rgba(249,212,6,0.1)]">
                <div className="absolute top-0 right-0 p-4">
                    <div className="size-2 bg-primary rounded-full animate-pulse"></div>
                </div>

                <div className="mb-8">
                    <span className="text-5xl font-black text-white">$19</span>
                    <span className="text-white/40 font-mono text-sm ml-2">/ month</span>
                </div>

                <ul className="space-y-4 mb-8 font-mono text-xs text-white/80">
                    <li className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-sm">check</span>
                        Unlimited Source Analysis
                    </li>
                    <li className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-sm">check</span>
                        Real-time Bias Radar
                    </li>
                    <li className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-sm">check</span>
                        Full Diff Engine Access
                    </li>
                    <li className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-sm">check</span>
                        Export to PDF Dossier
                    </li>
                </ul>

                <button
                    onClick={handleSubscribe}
                    disabled={loading}
                    className="w-full h-14 bg-primary text-black font-bold uppercase tracking-widest rounded hover:brightness-110 transition-all shadow-lg shadow-primary/20 flex items-center justify-center gap-2"
                >
                    {loading ? <Loader2 className="animate-spin" /> : 'Initialize Uplink'}
                </button>
            </div>

            <p className="mt-8 text-[10px] text-white/20 font-mono uppercase">
                Secure transaction via Stripe 256-bit encryption
            </p>
        </div>
    );
}
