'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/components/auth/AuthContext';
import { Card } from '@/components/ui/Card';
import { Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function VerifyPage() {
    const { verifyEmailLink } = useAuth();
    const [error, setError] = useState('');
    const [verifying, setVerifying] = useState(true);

    useEffect(() => {
        async function verify() {
            try {
                await verifyEmailLink();
            } catch (err: any) {
                setError(err.message || 'Failed to verify email link.');
            } finally {
                setVerifying(false);
            }
        }
        verify();
    }, [verifyEmailLink]);

    if (verifying) {
        return (
            <div className="container" style={{ maxWidth: '500px', marginTop: '4rem' }}>
                <Card variant="paper" style={{ padding: '2rem', textAlign: 'center' }}>
                    <Loader2 className="animate-spin" style={{ margin: '0 auto', width: '48px', height: '48px' }} />
                    <p style={{ marginTop: '1rem' }}>Verifying your sign-in link...</p>
                </Card>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container" style={{ maxWidth: '500px', marginTop: '4rem' }}>
                <Card variant="paper" style={{ padding: '2rem', textAlign: 'center' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>
                    <h2>Verification Failed</h2>
                    <p style={{ color: 'var(--color-red)', marginTop: '1rem' }}>{error}</p>
                    <Link href="/login" style={{
                        display: 'inline-block',
                        marginTop: '1.5rem',
                        color: 'var(--color-yellow)',
                        textDecoration: 'underline'
                    }}>
                        Try signing in again
                    </Link>
                </Card>
            </div>
        );
    }

    // Success - user will be redirected by AuthContext
    return (
        <div className="container" style={{ maxWidth: '500px', marginTop: '4rem' }}>
            <Card variant="paper" style={{ padding: '2rem', textAlign: 'center' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
                <h2>Signed In!</h2>
                <p>Redirecting to your dashboard...</p>
            </Card>
        </div>
    );
}
