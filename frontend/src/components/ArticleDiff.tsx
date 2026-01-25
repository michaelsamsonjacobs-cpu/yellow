import { Fragment } from 'react';

interface DiffSegment {
    type: 'unchanged' | 'removed' | 'added';
    text: string;
}

interface DiffViewerProps {
    headlineDiff: DiffSegment[];
    bodyDiff: DiffSegment[];
}

export function DiffViewer({ headlineDiff, bodyDiff }: DiffViewerProps) {
    return (
        <div className="diff-container">
            {/* Split Header */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '1rem', borderBottom: '2px solid var(--color-black)', paddingBottom: '0.5rem' }}>
                <div style={{ fontFamily: 'var(--font-ui)', fontWeight: 600, color: 'var(--color-gray-800)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Original Report
                </div>
                <div style={{ fontFamily: 'var(--font-ui)', fontWeight: 600, color: 'var(--color-yellow)', textTransform: 'uppercase', letterSpacing: '0.05em', backgroundColor: 'var(--color-black)', display: 'inline-block', padding: '2px 8px', borderRadius: '2px' }}>
                    Yellow Redraft
                </div>
            </div>

            {/* Split Content */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>

                {/* LEFT COLUMN: ORIGINAL (Shows Removed + Unchanged) */}
                <div className="original-view" style={{ color: 'var(--color-gray-800)', fontFamily: 'var(--font-body)' }}>
                    {/* Headline */}
                    <h1 style={{ marginBottom: '1.5rem', lineHeight: '1.3', opacity: 0.8 }}>
                        {headlineDiff.map((segment, i) => (
                            <Fragment key={i}>
                                {segment.type === 'removed' ? (
                                    <span style={{ backgroundColor: 'rgba(185, 28, 28, 0.1)', color: 'var(--color-red)', fontWeight: 600 }}>{segment.text}</span>
                                ) : segment.type === 'unchanged' ? (
                                    <span>{segment.text}</span>
                                ) : null}
                            </Fragment>
                        ))}
                    </h1>
                    {/* Body */}
                    <div style={{ fontSize: '1.125rem', lineHeight: '1.8', whiteSpace: 'pre-wrap' }}>
                        {bodyDiff.map((segment, i) => (
                            <Fragment key={i}>
                                {segment.type === 'removed' ? (
                                    <span style={{ backgroundColor: 'rgba(185, 28, 28, 0.1)', color: 'var(--color-red)', textDecoration: 'line-through' }}>{segment.text}</span>
                                ) : segment.type === 'unchanged' ? (
                                    <span>{segment.text}</span>
                                ) : null}
                            </Fragment>
                        ))}
                    </div>
                </div>

                {/* RIGHT COLUMN: REDRAFT (Shows Added + Unchanged) */}
                <div className="redraft-view" style={{ fontFamily: 'var(--font-body)', position: 'relative' }}>
                    {/* Paper texture overlay for the redraft column specifically? Maybe too complex. Keeping it clean. */}

                    {/* Headline */}
                    <h1 style={{ marginBottom: '1.5rem', lineHeight: '1.3' }}>
                        {headlineDiff.map((segment, i) => (
                            <Fragment key={i}>
                                {segment.type === 'added' ? (
                                    <span style={{ backgroundColor: 'rgba(21, 128, 61, 0.1)', borderBottom: '2px solid var(--color-green)', fontWeight: 600 }}>{segment.text}</span>
                                ) : segment.type === 'unchanged' ? (
                                    <span>{segment.text}</span>
                                ) : null}
                            </Fragment>
                        ))}
                    </h1>
                    {/* Body */}
                    <div style={{ fontSize: '1.125rem', lineHeight: '1.8', whiteSpace: 'pre-wrap' }}>
                        {bodyDiff.map((segment, i) => (
                            <Fragment key={i}>
                                {segment.type === 'added' ? (
                                    <span style={{ backgroundColor: 'rgba(21, 128, 61, 0.1)', borderBottom: '2px solid var(--color-green)' }}>{segment.text}</span>
                                ) : segment.type === 'unchanged' ? (
                                    <span>{segment.text}</span>
                                ) : null}
                            </Fragment>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
}
