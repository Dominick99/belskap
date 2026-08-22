"use client";

import Link from "next/link";
import { useState } from "react";

const ratios = [
  { label: "Square", value: "1 / 1", icon: "□" },
  { label: "Portrait", value: "4 / 5", icon: "▯" },
  { label: "Landscape", value: "16 / 9", icon: "▭" },
];

const palettes = [
  "linear-gradient(145deg, #291d35 0%, #9d4f6c 48%, #e6a15b 100%)",
  "linear-gradient(145deg, #081d2b 0%, #17636c 48%, #e8b86d 100%)",
  "linear-gradient(145deg, #241714 0%, #6c2e29 52%, #d89755 100%)",
  "linear-gradient(145deg, #0b1525 0%, #3c3672 48%, #d4667d 100%)",
];

export function ImageGenerator() {
  const [prompt, setPrompt] = useState("");
  const [ratio, setRatio] = useState("4 / 5");
  const [count, setCount] = useState(2);
  const [generating, setGenerating] = useState(false);
  const [results, setResults] = useState<number[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  function generate() {
    if (!prompt.trim() || generating) return;
    setGenerating(true);
    setResults([]);
    setSelected(null);
    window.setTimeout(() => {
      setResults(Array.from({ length: count }, (_, index) => index));
      setGenerating(false);
    }, 1100);
  }

  return (
    <main className="generator-page">
      <header className="generator-header">
        <div>
          <Link className="back-link generator-back" href="/dashboard/tools">← All tools</Link>
          <h1>Image generator</h1>
        </div>
        <span className="prototype-badge">Prototype mode</span>
      </header>

      <div className="generator-workspace">
        <aside className="generator-controls">
          <div className="control-heading">
            <span>01</span>
            <div><strong>Describe your image</strong><small>Be specific for better results.</small></div>
          </div>
          <label className="sr-only" htmlFor="image-prompt">Image prompt</label>
          <textarea
            id="image-prompt"
            className="generator-prompt"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="A cinematic fashion portrait at golden hour, editorial lighting, rich warm tones..."
            maxLength={800}
          />
          <div className="prompt-meta"><button type="button" onClick={() => setPrompt("A cinematic fashion portrait at golden hour, editorial lighting, rich warm tones")}>Try an example</button><span>{prompt.length}/800</span></div>

          <div className="control-divider" />
          <div className="control-heading compact">
            <span>02</span>
            <div><strong>Choose a format</strong></div>
          </div>
          <div className="ratio-options">
            {ratios.map((item) => (
              <button className={ratio === item.value ? "active" : ""} key={item.label} type="button" onClick={() => setRatio(item.value)}>
                <b aria-hidden="true">{item.icon}</b><span>{item.label}</span><small>{item.value.replace(" / ", ":")}</small>
              </button>
            ))}
          </div>

          <div className="control-row">
            <div><strong>Number of images</strong><small>Generate up to four options.</small></div>
            <div className="count-picker" aria-label="Number of images">
              {[1, 2, 4].map((number) => <button className={count === number ? "active" : ""} type="button" key={number} onClick={() => setCount(number)}>{number}</button>)}
            </div>
          </div>

          <button className="generate-button" type="button" onClick={generate} disabled={!prompt.trim() || generating}>
            <span>{generating ? "Generating" : "Generate images"}</span><b aria-hidden="true">{generating ? "•••" : "✦"}</b>
          </button>
          <p className="dummy-note">Demo only — no credits will be used.</p>
        </aside>

        <section className="generator-results" aria-live="polite">
          {generating ? (
            <div className="generating-state"><div className="generation-orbit"><span>✦</span></div><h2>Creating your images</h2><p>Turning your idea into something visual...</p></div>
          ) : results.length ? (
            <div className="results-content">
              <div className="results-heading"><div><p className="eyebrow">Latest generation</p><h2>{results.length} new {results.length === 1 ? "image" : "images"}</h2></div><button type="button" onClick={generate}>↻ Regenerate</button></div>
              <div className={`dummy-result-grid count-${results.length}`}>
                {results.map((result) => (
                  <button className={`dummy-result ${selected === result ? "selected" : ""}`} style={{ aspectRatio: ratio, background: palettes[result] }} key={result} type="button" onClick={() => setSelected(result)} aria-label={`Select generated image ${result + 1}`}>
                    <span className="dummy-scene"><i /><b /><em /></span>
                    <span className="result-number">0{result + 1}</span>
                    {selected === result && <span className="selected-check">✓</span>}
                  </button>
                ))}
              </div>
              <div className={`result-actions ${selected === null ? "hidden" : ""}`}><span>Image selected</span><button type="button">Save to library</button><button type="button">Download</button></div>
            </div>
          ) : (
            <div className="generator-empty">
              <div className="empty-canvas"><span>✦</span><i /><b /></div>
              <h2>Your ideas show up here.</h2>
              <p>Describe an image, choose a format, and hit generate.</p>
              <div className="empty-tip"><span>Tip</span> Mention lighting, mood, and camera style for stronger results.</div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
