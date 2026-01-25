import type { Metadata } from 'next';
import { Playfair_Display, Source_Serif_4, Inter } from 'next/font/google';
import './globals.css';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';
import { AuthProvider } from '@/components/auth/AuthContext';

const playfair = Playfair_Display({
    subsets: ['latin'],
    variable: '--font-playfair'
});

const sourceSerif = Source_Serif_4({
    subsets: ['latin'],
    variable: '--font-source-serif'
});

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter'
});

export const metadata: Metadata = {
    title: 'Yellow - News Integrity Platform',
    description: 'The world\'s first AI Editor trained on the SPJ Code of Ethics.',
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <head>
                <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
                <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%23f9d406%22/></svg>" />
                <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Noto+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet" />
                <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
                <script dangerouslySetInnerHTML={{
                    __html: `
                        tailwind.config = {
                            darkMode: "class",
                            theme: {
                                extend: {
                                    colors: {
                                        "primary": "#f9d406",
                                        "background-light": "#f8f8f5",
                                        "background-dark": "#0d0d0d",
                                        "paper-white": "#f5f5f0",
                                        "deep-charcoal": "#1a1a1a",
                                        "signal-yellow": "#ffd700",
                                        "card-dark": "rgba(35, 32, 15, 0.7)",
                                    },
                                    fontFamily: {
                                        "display": ["Space Grotesk", "sans-serif"],
                                        "mono": ["'JetBrains Mono'", "monospace"],
                                        "serif-article": ["Noto Serif", "serif"]
                                    },
                                    borderRadius: {
                                        "DEFAULT": "0.25rem",
                                        "lg": "0.5rem",
                                        "xl": "0.75rem",
                                        "full": "9999px"
                                    },
                                },
                            },
                        }
                    `
                }} />
            </head>
            <body className={`${playfair.variable} ${sourceSerif.variable} ${inter.variable}`}>
                <AuthProvider>
                    <div className="layout-wrapper" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
                        <Header />
                        <main className="main-content" style={{ flex: 1 }}>
                            {children}
                        </main>
                        <Footer />
                    </div>
                </AuthProvider>
            </body>
        </html>
    );
}
