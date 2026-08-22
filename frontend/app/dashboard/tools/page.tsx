import Link from "next/link";

const tools = [
  { kind: "image", name: "Image generator", copy: "Create images from text, images, or both.", category: "Image", available: true, href: "/dashboard/tools/image-generator" },
  { kind: "edit", name: "Image editor", copy: "Replace, restyle, or refine part of an image.", category: "Image", available: false },
  { kind: "upscale", name: "Image upscaler", copy: "Enhance resolution and recover fine detail.", category: "Image", available: false },
  { kind: "motion", name: "Image to video", copy: "Turn a still image into a short motion clip.", category: "Video", available: false },
  { kind: "video", name: "Video generator", copy: "Generate original video from a description.", category: "Video", available: false },
  { kind: "caption", name: "Caption writer", copy: "Write platform-ready captions in any style.", category: "Writing", available: false },
];

export default function ToolsPage() {
  return (
    <main className="tools-page">
      <header className="tools-heading">
        <div>
          <p className="eyebrow">Creative suite</p>
          <h1>Make something.</h1>
          <p>AI-powered tools for creating and transforming content.</p>
        </div>
        <span className="tool-count">{tools.length} tools</span>
      </header>

      <section aria-labelledby="all-tools">
        <div className="section-title-row">
          <h2 id="all-tools">Explore tools</h2>
          <span>Choose what you want to make</span>
        </div>
        <div className="tools-market-grid">
          {tools.map((tool) => {
            const content = (
              <>
                <div className={`market-tool-art ${tool.kind}`} aria-hidden="true"><i /><b /><em /></div>
                <div className="market-tool-copy">
                  <div className="market-tool-meta"><span>{tool.category}</span><span className={tool.available ? "available" : ""}>{tool.available ? "Available" : "Coming soon"}</span></div>
                  <h2>{tool.name}</h2>
                  <p>{tool.copy}</p>
                  <strong>{tool.available ? "Open tool →" : "Preview"}</strong>
                </div>
              </>
            );
            return tool.available ? <Link className="market-tool-card" href={tool.href!} key={tool.name}>{content}</Link> : <article className="market-tool-card disabled" key={tool.name}>{content}</article>;
          })}
        </div>
      </section>
    </main>
  );
}
