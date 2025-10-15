import AsciiArtGenerator from '@/components/AsciiArtGenerator';

export default function Home() {
  return (
    <main className="flex flex-col items-center gap-6 p-8 text-center">
      <h1 className="text-3xl font-bold">🎨 ASCII Art Generator</h1>
      <AsciiArtGenerator />
    </main>
  );
}