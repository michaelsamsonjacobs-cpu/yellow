
import {
    collection,
    doc,
    getDoc,
    getDocs,
    query,
    where,
    orderBy,
    limit,
    Timestamp,
    DocumentData
} from 'firebase/firestore';
import { db } from './firebase';

// Collection references
export const topicsRef = collection(db, 'topics');
export const articlesRef = collection(db, 'articles');
export const outletsRef = collection(db, 'outlets');
export const usersRef = collection(db, 'users');

// Type definitions matching the old API structure
export interface Topic {
    id: string;
    name: string;
    article_count: number;
    region: 'us' | 'international';
    created_at: Date;
}

export interface Article {
    id: string;
    topic_id: string;
    outlet_id: string;
    outlet_name: string;
    title: string;
    original_text: string;
    redrafted_text: string;
    diff_html: string;
    integrity_score: number;
    published_at: Date;
    scraped_at: Date;
}

export interface Outlet {
    id: string;
    name: string;
    slug: string;
    integrity_score: number;
    article_count: number;
    bias_label: string;
    last_updated: Date;
}

// Helper to convert Firestore doc to typed object
function docToTopic(doc: DocumentData): Topic {
    const data = doc.data();
    return {
        id: doc.id,
        name: data.name,
        article_count: data.article_count || 0,
        region: data.region || 'us',
        created_at: data.created_at?.toDate() || new Date(),
    };
}

function docToArticle(doc: DocumentData): Article {
    const data = doc.data();
    return {
        id: doc.id,
        topic_id: data.topic_id,
        outlet_id: data.outlet_id,
        outlet_name: data.outlet_name,
        title: data.title,
        original_text: data.original_text,
        redrafted_text: data.redrafted_text,
        diff_html: data.diff_html,
        integrity_score: data.integrity_score,
        published_at: data.published_at?.toDate() || new Date(),
        scraped_at: data.scraped_at?.toDate() || new Date(),
    };
}

function docToOutlet(doc: DocumentData): Outlet {
    const data = doc.data();
    return {
        id: doc.id,
        name: data.name,
        slug: data.slug,
        integrity_score: data.integrity_score || 0,
        article_count: data.article_count || 0,
        bias_label: data.bias_label || 'Unknown',
        last_updated: data.last_updated?.toDate() || new Date(),
    };
}

// API functions (matching old api.ts interface)
export const firestoreApi = {
    // Topics
    async getTopics(): Promise<{ us_topics: Topic[]; intl_topics: Topic[]; date: string }> {
        const usQuery = query(topicsRef, where('region', '==', 'us'), orderBy('article_count', 'desc'), limit(20));
        const intlQuery = query(topicsRef, where('region', '==', 'international'), orderBy('article_count', 'desc'), limit(20));

        const [usSnapshot, intlSnapshot] = await Promise.all([
            getDocs(usQuery),
            getDocs(intlQuery)
        ]);

        return {
            us_topics: usSnapshot.docs.map(docToTopic),
            intl_topics: intlSnapshot.docs.map(docToTopic),
            date: new Date().toISOString().split('T')[0]
        };
    },

    async getTopicArticles(topicId: string): Promise<Article[]> {
        const q = query(articlesRef, where('topic_id', '==', topicId), orderBy('scraped_at', 'desc'));
        const snapshot = await getDocs(q);
        return snapshot.docs.map(docToArticle);
    },

    // Recent Articles (Global Feed)
    async getRecentArticles(limitCount = 20): Promise<Article[]> {
        const q = query(articlesRef, orderBy('scraped_at', 'desc'), limit(limitCount));
        const snapshot = await getDocs(q);
        return snapshot.docs.map(docToArticle);
    },

    // Articles
    async getArticle(articleId: string): Promise<Article | null> {
        const docRef = doc(articlesRef, articleId);
        const snapshot = await getDoc(docRef);
        if (!snapshot.exists()) return null;
        return docToArticle(snapshot);
    },

    // Outlets
    async getOutlets(): Promise<Outlet[]> {
        const q = query(outletsRef, orderBy('integrity_score', 'desc'));
        const snapshot = await getDocs(q);
        return snapshot.docs.map(docToOutlet);
    },

    async getOutlet(outletId: string): Promise<Outlet | null> {
        const docRef = doc(outletsRef, outletId);
        const snapshot = await getDoc(docRef);
        if (!snapshot.exists()) return null;
        return docToOutlet(snapshot);
    },

    async getOutletHistory(outletId: string): Promise<any[]> {
        return [];
    }
};
