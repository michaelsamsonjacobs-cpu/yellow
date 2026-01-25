// API client - uses Firestore for data, REST for legacy endpoints
import { firestoreApi } from './firestore';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005';

class ApiError extends Error {
    constructor(public status: number, public message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

async function fetcher(endpoint: string, options: RequestInit = {}) {
    const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        credentials: 'include',
    });

    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new ApiError(res.status, errorData.detail || 'An error occurred');
    }

    return res.json();
}

export const api = {
    // Topics & Articles - Now using Firestore
    getTopics: () => firestoreApi.getTopics(),
    getTopicArticles: (topicId: string) => firestoreApi.getTopicArticles(topicId),
    getRecentArticles: () => firestoreApi.getRecentArticles(),
    getArticle: (articleId: string) => firestoreApi.getArticle(articleId),

    // Outlets - Now using Firestore
    getOutlets: () => firestoreApi.getOutlets(),
    getOutlet: (outletId: string) => firestoreApi.getOutlet(outletId),
    getOutletHistory: (outletId: string) => firestoreApi.getOutletHistory(outletId),

    // Legacy REST endpoints (still needed for Stripe/payments)
    createCheckoutSession: () => fetcher('/user/subscribe', { method: 'POST' }),
    createPortalSession: () => fetcher('/user/portal', { method: 'POST' }),
    toggleNewsletter: () => fetcher('/user/newsletter', { method: 'PATCH' }),
};

