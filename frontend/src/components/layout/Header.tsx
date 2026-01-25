'use client';

import Link from 'next/link';
import { useAuth } from '@/components/auth/AuthContext';
import { Button } from '@/components/ui/Button';
import { usePathname } from 'next/navigation';

export function Header() {
    const { user, logout } = useAuth();
    const pathname = usePathname();

    // Hide global header on app pages (they have their own sidebar/layout)
    if (pathname?.startsWith('/dashboard') || pathname?.startsWith('/outlets') || pathname?.startsWith('/articles') || pathname?.startsWith('/admin')) {
        return null;
    }

    return (
        <header style={{
            borderBottom: '1px solid var(--color-black)',
            padding: '1.25rem 0',
            marginBottom: '2rem',
            backgroundColor: 'var(--color-off-white)',
            position: 'sticky',
            top: 0,
            zIndex: 50,
            boxShadow: 'var(--shadow-sm)'
        }}>
            <div className="container" style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <Link href={user ? "/dashboard" : "/"} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    textDecoration: 'none'
                }}>
                    <div className="font-display font-black text-3xl tracking-tighter bg-primary text-black px-2 py-0 border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                        YELLOW
                    </div>
                </Link>

                <nav style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                    {user ? (
                        <>
                            <Link href="/dashboard" className="ui-text hover-underline">Dashboard</Link>
                            <Link href="/outlets" className="ui-text hover-underline">Outlets</Link>
                            <Link href="/settings" className="ui-text hover-underline">Settings</Link>
                            <Button variant="outline" size="sm" onClick={() => logout()}>
                                LOGOUT
                            </Button>
                        </>
                    ) : (
                        <Link href="/login">
                            <Button variant="primary" size="sm">BECOME A MEMBER</Button>
                        </Link>
                    )}
                </nav>
            </div>

        </header>
    );
}
