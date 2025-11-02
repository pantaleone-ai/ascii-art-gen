# ASCII Art Generator

A web app for generating abstract ASCII art, either from uploaded images or procedurally (e.g., waves, noise patterns). Built with Next.js (frontend) and FastAPI (backend), deployed on Vercel.

## Features
- Image-to-ASCII conversion with customizable scale, charset, dithering, brightness/contrast.
- Procedural abstract art generation (no image needed): Styles like waves, radial, noise, terrain.
- Output as PNG image or plain text ASCII.
- Supports diversity for character variation, inversion, seeding for reproducibility.

## Tech Stack
- Frontend: Next.js, React, Tailwind CSS, TypeScript
- Backend: FastAPI (Python), PIL for image processing, NumPy for arrays
- Deployment: Vercel

## Setup
1. Clone the repo: `git clone https://github.com/pantaleone-ai/ascii-art-gen`
2. Install Node deps: `npm install`
3. Install Python deps: `pip install -r requirements.txt`
4. Run dev: `npm run dev` (frontend at http://localhost:3000; backend auto-handled by Vercel in prod)

## Usage
- Upload an image or select a procedural style.
- Adjust parameters and generate.
- View or copy the output.

Deployed at: https://ascii-aiart-gen.vercel.app/
