export default function PrivacyPage() {
    return (
        <div className="container" style={{ padding: '4rem 1rem', maxWidth: '800px' }}>
            <h1 style={{ marginBottom: '2rem' }}>Privacy Policy</h1>
            <p>Last updated: January 20, 2026</p>

            <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <section>
                    <h3>1. Introduction</h3>
                    <p>Welcome to Yellow. We respect your privacy and are committed to protecting your personal data.</p>
                </section>

                <section>
                    <h3>2. Data We Collect</h3>
                    <p>We collect your email address when you sign up or subscribe to our newsletter. We do not track your browsing activity across other sites.</p>
                </section>

                <section>
                    <h3>3. How We Use Your Data</h3>
                    <p>We use your data solely to provide the Yellow service, including sending daily briefings and managing your subscription.</p>
                </section>

                <section>
                    <h3>4. Data Security</h3>
                    <p>We use industry-standard security measures including passwordless magic links to protect your account.</p>
                </section>
            </div>
        </div>
    );
}
