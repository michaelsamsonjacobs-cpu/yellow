export default function TermsPage() {
    return (
        <div className="container" style={{ padding: '4rem 1rem', maxWidth: '800px' }}>
            <h1 style={{ marginBottom: '2rem' }}>Terms of Service</h1>
            <p>Last updated: January 20, 2026</p>

            <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <section>
                    <h3>1. Acceptance of Terms</h3>
                    <p>By accessing and using Yellow, you accept and agree to be bound by the terms and provision of this agreement.</p>
                </section>

                <section>
                    <h3>2. Description of Service</h3>
                    <p>Yellow provides AI-powered news analysis and scoring services. We do not claim this analysis is infallible.</p>
                </section>

                <section>
                    <h3>3. User Conduct</h3>
                    <p>You agree to use the service only for lawful purposes and properly attribute our analysis when sharing.</p>
                </section>

                <section>
                    <h3>4. Disclaimer</h3>
                    <p>The service is provided "as is". Our integrity scores are based on our proprietary algorithm and should be used for informational purposes only.</p>
                </section>
            </div>
        </div>
    );
}
