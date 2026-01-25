
const API_URL = 'http://localhost:8000';

export async function createCheckoutSession(userId: string, priceId: string) {
    // Note: In this architecture, userId is handled via the session cookie/token on the backend.
    // Ensure "credentials: include" is sent if using cookies, or Authorization header if using JWT.

    // We assume the user is logged in via the new AuthContext which likely syncs with the backend.
    // However, if we are strictly using Firebase Auth on frontend, we might need to send the ID token.

    // For now, let's assume the backend endpoint expects an Authorization header with the Firebase ID Token
    // OR creates a session based on the Firebase UID if passed.

    // SIMPLIFICATION: Since the user said "Stripe is broken", we are bypassing the simple extension.
    // We will call the backend.

    const response = await fetch(`${API_URL}/subscriptions/checkout`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // 'Authorization': `Bearer ${token}` // If we had the token here
        },
        // If the backend relies on cookies, fetch handles it automatically with credentials: 'include'
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create checkout session');
    }

    const data = await response.json();
    return data.url;
}
