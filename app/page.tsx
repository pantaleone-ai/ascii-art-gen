'use client';

import { useState } from 'react';

const ASCII_CHARS = ['@', '#', '$', '%', '&', '*', '+', '=', '-', ':', '.', ' '];

export default function Home() {
  const [width, setWidth] = useState(60);
  const [height, setHeight] = useState(20);
  const [output, setOutput] = useState('');

  const generateAscii = () => {
    let ascii = '';
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const char = ASCII_CHARS[Math.floor(Math.random() * ASCII_CHARS.length)];
        ascii += char;
      }
      ascii += '\n';
    }
    setOutput(ascii);
  };

  return (
    <main className="flex flex-col items-center gap-6 p-8 text-center">
      <h1 className="text-3xl font-bold">🎨 Random ASCII Art Generator</h1>

      <div className="flex gap-4">
        <label>
          Width:
          <input
            type="number"
            className="ml-2 w-16 p-1 rounded text-black"
            value={width}
            onChange={(e) => setWidth(Number(e.target.value))}
          />
        </label>
        <label>
          Height:
          <input
            type="number"
            className="ml-2 w-16 p-1 rounded text-black"
            value={height}
            onChange={(e) => setHeight(Number(e.target.value))}
          />
        </label>
      </div>

      <button
        onClick={generateAscii}
        className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-500"
      >
        Generate
      </button>

      {output && (
        <pre className="bg-gray-800 p-4 rounded text-green-400 whitespace-pre-wrap w-[480px] h-[320px] overflow-auto">
          {output}
        </pre>
      )}
    </main>
  );
}
