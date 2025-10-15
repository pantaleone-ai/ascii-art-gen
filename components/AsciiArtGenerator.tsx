'use client';

import { useEffect, useState } from 'react';
import art from 'ascii-art';

export default function AsciiArtGenerator() {
  const [asciiArt, setAsciiArt] = useState<string>('');

  useEffect(() => {
    const generateArt = async () => {
      try {
        const fonts = ['doom', 'block', 'slant', 'starwars', 'banner', 'drpepper'];
        const selectedFont = fonts[Math.floor(Math.random() * fonts.length)];
        const rendered = await art.font('Hello, ASCII World!', selectedFont).completed();
        setAsciiArt(rendered);
      } catch (err) {
        console.error('Error generating ASCII art:', err);
      }
    };

    generateArt();
  }, []);

  return (
    <pre className="bg-gray-800 p-4 rounded text-green-400 whitespace-pre-wrap w-[480px] h-[320px] overflow-auto">
      {asciiArt}
    </pre>
  );
}