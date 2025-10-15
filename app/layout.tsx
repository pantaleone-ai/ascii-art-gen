import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ASCII Art Generator',
  description: 'Convert your text into ASCII art instantly.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100 min-h-screen flex items-center justify-center">
        {children}
      </body>
    </html>
  );
}
