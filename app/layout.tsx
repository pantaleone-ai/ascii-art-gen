import './globals.css';
import React from 'react';

export const metadata = {
  title: 'ASCII Art Generator',
  description: 'Generate diverse ASCII art styles dynamically!',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}