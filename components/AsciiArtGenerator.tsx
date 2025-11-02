'use client';
import { useState } from 'react';

export default function AsciiArtGenerator() {
    const [art, setArt] = useState<string>('');
    const [file, setFile] = useState<File | null>(null);
    const [scale, setScale] = useState(0.08);
    const [charWidth, setCharWidth] = useState(10);
    const [charHeight, setCharHeight] = useState(18);
    const [fontSize, setFontSize] = useState(14);
    const [preset, setPreset] = useState('dense');
    const [diversity, setDiversity] = useState(0.0);
    const [dither, setDither] = useState(false);
    const [invert, setInvert] = useState(false);
    const [brightness, setBrightness] = useState(1.0);
    const [contrast, setContrast] = useState(1.0);
    const [seed, setSeed] = useState<number | null>(null);
    const [style, setStyle] = useState<string | null>(null); // For procedural: waves, radial, noise, terrain
    const [targetWidth, setTargetWidth] = useState(80);
    const [targetHeight, setTargetHeight] = useState(20);
    const [outputMode, setOutputMode] = useState('image'); // image or text
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
            setStyle(null); // Reset style if file selected (image mode)
        }
    };

    const generate = async () => {
        setIsLoading(true);
        const formData = new FormData();
        if (file) {
            formData.append('file', file);
        } else if (style) {
            formData.append('style', style);
            formData.append('target_width', targetWidth.toString());
            formData.append('target_height', targetHeight.toString());
        } else {
            alert('Please upload a file or select a procedural style.');
            setIsLoading(false);
            return;
        }

        formData.append('scale', scale.toString());
        formData.append('char_width', charWidth.toString());
        formData.append('char_height', charHeight.toString());
        formData.append('font_size', fontSize.toString());
        formData.append('preset', preset);
        formData.append('diversity', diversity.toString());
        formData.append('dither', dither.toString());
        formData.append('invert', invert.toString());
        formData.append('brightness', brightness.toString());
        formData.append('contrast', contrast.toString());
        if (seed !== null) formData.append('seed', seed.toString());
        formData.append('output_mode', outputMode);

        try {
            const res = await fetch('/api/ascii_service', { // Adjust endpoint if different in your Vercel setup
                method: 'POST',
                body: formData,
            });

            if (outputMode === 'text') {
                const text = await res.text();
                setArt(text);
            } else {
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                setArt(url); // Display as image
            }
        } catch (error) {
            console.error('Error generating art:', error);
            alert('Failed to generate art.');
        } finally {
            setIsLoading(false);
        }
    };
