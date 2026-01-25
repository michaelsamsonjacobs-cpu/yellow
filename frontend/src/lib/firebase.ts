
import { initializeApp, getApps } from 'firebase/app';
import { getAuth, GoogleAuthProvider, EmailAuthProvider } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getAnalytics, isSupported } from 'firebase/analytics';

const firebaseConfig = {
    apiKey: "AIzaSyAe75_b9dMcAOke0Hpr0a5C382QrrFDAwk",
    authDomain: "yellow-news.firebaseapp.com",
    projectId: "yellow-news",
    storageBucket: "yellow-news.firebasestorage.app",
    messagingSenderId: "438717274441",
    appId: "1:438717274441:web:4e7d2ab55cb3b34f796298",
    measurementId: "G-FYV6MXMXDR"
};

// Initialize Firebase (prevent duplicate initialization)
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

// Auth
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
export const emailProvider = new EmailAuthProvider();

// Firestore
export const db = getFirestore(app);

// Analytics (only on client)
export const initAnalytics = async () => {
    if (typeof window !== 'undefined' && await isSupported()) {
        return getAnalytics(app);
    }
    return null;
};

// Action code settings for email link auth
export const actionCodeSettings = {
    url: typeof window !== 'undefined'
        ? `${window.location.origin}/auth/verify`
        : 'http://localhost:3000/auth/verify',
    handleCodeInApp: true,
};

export { app };
export default app;
