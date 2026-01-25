'use client';

import { useAuth } from '@/components/auth/AuthContext';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { api } from '@/lib/api';
import { useState } from 'react';

export default function SettingsPage() {
    const { user, loading, logout } = useAuth();
    const [portalLoading, setPortalLoading] = useState(false);

    async function handlePortal() {
        setPortalLoading(true);
        try {
            const res = await api.createPortalSession();
            window.location.href = res.portal_url;
        } catch (err) {
            alert('Failed to load billing portal');
        } finally {
            setPortalLoading(false);
        }
    }

    if (loading) return <div>Loading...</div>;

    return (
        <div className="container" style={{ maxWidth: '600px' }}>
            <h1 className="mb-6">Account Settings</h1>

            <Card className="p-6 mb-6" style={{ padding: '2rem' }}>
                <h3 className="mb-4">Subscription</h3>
                <p className="mb-4">Status: <strong>{user?.subscription_status === 'active' ? 'Active' : 'Inactive'}</strong></p>

                {user?.subscription_status === 'active' ? (
                    <Button onClick={handlePortal} isLoading={portalLoading}>
                        Manage Subscription
                    </Button>
                ) : (
                    <Button onClick={handlePortal} isLoading={portalLoading}>
                        Subscribe Now
                    </Button>
                )}
            </Card>

            <Card className="p-6" style={{ padding: '2rem' }}>
                <h3 className="mb-4">Profile</h3>
                <p className="mb-4">Email: {user?.email}</p>
                <Button variant="outline" onClick={() => logout()}>
                    Sign Out
                </Button>
            </Card>
        </div>
    );
}
