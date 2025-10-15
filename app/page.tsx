"use client";
import { useState } from "react";

export default function Page() {
  const [file, setFile] = useState(null);
  const [imgUrl, setImgUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    if (!file) { setError("Choose an image file."); return; }
    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);
    // some example controls
    fd.append("scale", "0.06");
    fd.append("char_width", "8");
    fd.append("char_height", "16");
    fd.append("font_size", "12");
    fd.append("diversity", "0.4");
    fd.append("dither", "true");
    try {
      const res = await fetch("/api/ascii_service", { method: "POST", body: fd });
      if (!res.ok) {
        const txt = await res.text();
        setError("Server error: " + txt);
        setLoading(false);
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setImgUrl(url);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1 style={{fontSize:24, marginBottom:12}}>ASCII Art Generator (Vercel-ready)</h1>
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:12}}>
            <input type="file" accept="image/*" onChange={(e)=>setFile(e.target.files?.[0] ?? null)} />
          </div>
          <div>
            <button type="submit" disabled={loading}>{loading ? "Generating..." : "Generate"}</button>
          </div>
        </form>
        {error && <div style={{color:"salmon", marginTop:12}}>{error}</div>}
        {imgUrl && <img src={imgUrl} alt="ascii output" className="output" />}
      </div>
      <footer style={{marginTop:16, color:"#9aa3b2"}}>Backend: /api/ascii_service (FastAPI)</footer>
    </main>
  );
}
