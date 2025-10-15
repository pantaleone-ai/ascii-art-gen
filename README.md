# ASCII Art Generator (Next.js + FastAPI)

This repo contains a Next.js 15 frontend and a FastAPI backend function intended for deployment on Vercel.
The Python API function is at `api/ascii_service` and exposes a single POST endpoint that accepts an image
and returns a PNG of the ASCII-ified output.

## Deploying to Vercel

1. Push this repository to GitHub.
2. Connect the repo to Vercel.
3. Vercel will detect the Node app and the Python serverless function automatically.
4. The frontend is served by Next.js; the backend function is available at `/api/ascii_service`.

## Local testing

- Frontend:
  ```bash
  npm install
  npm run dev
  ```
- Backend (for local development you can run FastAPI directly):
  ```bash
  pip install -r requirements.txt
  uvicorn api.ascii_service:app --reload --port 8000
  ```
  Then point the frontend fetch to `http://localhost:8000/generate` if testing locally.

