'use client';

import { useState } from 'react';

export default function Home() {
  const [input, setInput] = useState('Hello, ASCII!');
  const [output, setOutput] = useState('');

  const generateAscii = () => {
    const ascii = input
      .split('')
      .map((char) => char.charCodeAt(0).toString(16))
      .join(' ');
    setOutput(ascii);
  };

  return (
    <main className="flex flex-col items-center gap-6 p-8 text-center">
      <h1 className="text-3xl font-bold">🎨 ASCII Art Generator</h1>
      <textarea
        className="w-80 h-32 p-2 text-black rounded"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button
        onClick={generateAscii}
        className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-500"
      >
        Generate
      </button>
      {output && (
        <pre className="bg-gray-800 p-4 rounded text-green-400 whitespace-pre-wrap w-80 break-words">
          {output}
        </pre>
      )}
    </main>
  );
}
