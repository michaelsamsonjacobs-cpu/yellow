'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
    User as FirebaseUser,
    onAuthStateChanged,
    signOut,
    signInWithPopup,
    sendSignInLinkToEmail,
    isSignInWithEmailLink,
    signInWithEmailLink
} from 'firebase/auth';
import { auth, googleProvider, actionCodeSettings, app } from '@/lib/firebase';

interface User {
    id: string;
    email: string | null;
    displayName: string | null;
    photoURL: string | null;
    subscription_status: 'active' | 'inactive' | 'cancelled' | 'past_due' | 'trialing';
    newsletter_opt_in: boolean;
}

interface AuthContextType {
    user: User | null;
    firebaseUser: FirebaseUser | null;
    loading: boolean;
    loginWithGoogle: () => Promise<void>;
    loginWithEmail: (email: string) => Promise<void>;
    verifyEmailLink: () => Promise<void>;
    logout: () => Promise<void>;
    checkSubscription: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

import { doc, getDoc, getFirestore } from 'firebase/firestore';

const db = getFirestore(app);

async function checkWhitelist(email: string | null): Promise<boolean> {
    if (!email) return false;
    try {
        // Check 'allowed_users' collection using email as ID
        const docRef = doc(db, 'allowed_users', email.toLowerCase());
        const docSnap = await getDoc(docRef);
        return docSnap.exists();
    } catch (e) {
        console.error("Whitelist check failed", e);
        return false;
    }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, async (fbUser) => {
            if (fbUser) {
                setFirebaseUser(fbUser);
                const isWhitelisted = await checkWhitelist(fbUser.email);

                setUser(mapFirebaseUser(fbUser, isWhitelisted));
            } else {
                setFirebaseUser(null);
                setUser(null);
            }
            setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    async function loginWithGoogle() {
        try {
            const result = await signInWithPopup(auth, googleProvider);
            // State update handled by onAuthStateChanged
            router.push('/dashboard');
        } catch (error) {
            console.error('Google sign-in error:', error);
            throw error;
        }
    }

    async function loginWithEmail(email: string) {
        try {
            await sendSignInLinkToEmail(auth, email, actionCodeSettings);
            // Save email for verification page
            if (typeof window !== 'undefined') {
                window.localStorage.setItem('emailForSignIn', email);
            }
        } catch (error) {
            console.error('Email link error:', error);
            throw error;
        }
    }

    async function verifyEmailLink() {
        if (typeof window === 'undefined') return;

        if (isSignInWithEmailLink(auth, window.location.href)) {
            let email = window.localStorage.getItem('emailForSignIn');

            if (!email) {
                // User opened the link on a different device
                email = window.prompt('Please provide your email for confirmation');
            }

            if (email) {
                try {
                    const result = await signInWithEmailLink(auth, email, window.location.href);
                    window.localStorage.removeItem('emailForSignIn');
                    setUser(mapFirebaseUser(result.user));
                    router.push('/dashboard');
                } catch (error) {
                    console.error('Email verification error:', error);
                    throw error;
                }
            }
        }
    }

    async function logout() {
        await signOut(auth);
        setUser(null);
        setFirebaseUser(null);
        router.push('/');
    }

    function checkSubscription() {
        if (!user) return false;
        return user.subscription_status === 'active' || user.subscription_status === 'trialing';
    }

    return (
        <AuthContext.Provider value={{
            user,
            firebaseUser,
            loading,
            loginWithGoogle,
            loginWithEmail,
            verifyEmailLink,
            logout,
            checkSubscription
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
