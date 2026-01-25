'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Article } from '@/lib/firestore'; // Import Shared Type
import { Card } from '@/components/ui/Card';
import { Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function TopicPage({ params }: { params: { id: string } }) {
    const [articles, setArticles] = useState<Article[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (params.id) {
            api.getTopicArticles(params.id)
                .then((res) => setArticles(res))
                .catch(console.error)
                .finally(() => setLoading(false));
        }
    }, [params.id]);

    if (loading) return <div className="container p-8 text-center"><Loader2 className="animate-spin mx-auto" /></div>;

    return (
        <div className="container">
            <Link href="/dashboard" className="mb-4 inline-block ui-text">← Back to Dashboard</Link>
            <h1 className="mb-6">Topic Coverage</h1>

            <div style={{ display: 'grid', gap: '1rem' }}>
                {articles.map((article) => (
                    <Card key={article.id} className="p-4" style={{ padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.25rem' }}>
                                {article.outlet_name} • {formatDistanceToNow(new Date(article.published_at))} ago
                            </div>
                            <Link href={`/articles/${article.id}`} style={{ fontSize: '1.2rem', fontWeight: 'bold', fontFamily: 'var(--font-headline)' }}>
                                {article.headline}
                            </Link>
                        </div>

                        <div style={{ textAlign: 'right', minWidth: '100px' }}>
                            <div
                                className={`score-badge ${article.score >= 90 ? 'score-high' :
                                    article.score >= 70 ? 'score-med' : 'score-low'
                                    }`}
                            >
                                {article.score}
                            </div>
                            {article.has_redraft && (
                                <div style={{ fontSize: '0.8rem', color: 'var(--color-red)', fontWeight: 'bold', marginTop: '0.25rem' }}>
                                    Violations Found
                                </div>
                            )}
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
}
