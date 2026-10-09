"use client";
import { useState } from "react";
const base = `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/results/final-sprint-20260928`;

export function SpectralInspector() {
  const [tab,setTab]=useState("partial");
  const [loaded,setLoaded]=useState(false);
  const file=tab==="partial"?"fusion-rescue-20261008/partial_surface/result/index.html":tab==="fusion"?"spectral/fusion/index.html":"spectral/samples/index.html";
  return <div className="inspector">
    <p><strong>New partial surface result:</strong> 2,338 FX10 spectra and 862 separate FX17 spectra are projected onto parts of two upper Plant 5 leaves. Wavelength changes colour the existing surface points. This is approximate, exploratory raw-DN fusion; point-wise physical accuracy, full-plant coverage and reflectance remain unvalidated.</p>
    <p><a href={`${base}/fusion-rescue-20261008/index.html`} target="_blank" rel="noreferrer">Open the new experiments, control reassessment and evidence ↗</a></p>
    <div className="tab-buttons" role="group" aria-label="Spectral inspection mode">
      <button aria-pressed={tab==="partial"} onClick={()=>{setTab("partial");setLoaded(true);}}>Partial surface · two leaves · both cameras</button>
      <button aria-pressed={tab==="fusion"} onClick={()=>{setTab("fusion");setLoaded(true);}}>Three-location baseline · both cameras</button>
      <button aria-pressed={tab==="samples"} onClick={()=>{setTab("samples");setLoaded(true);}}>All measured camera pixels</button>
      <a href={`${base}/${file}`} target="_blank" rel="noreferrer">Open full-screen ↗</a>
    </div>
    {!loaded?<div className="inspector-placeholder"><h3>Inspect the actual measured spectra</h3><p>Load the interactive viewer when ready. The new partial surface contains 3,200 separate camera observations. Upper-patch normalization is unsupported, so use raw DN. The original three-location baseline and 13,343-pixel inspector remain available.</p><button onClick={()=>setLoaded(true)}>Load 3D spectral viewer</button></div>:<iframe key={file} src={`${base}/${file}`} title={tab==="partial"?"Partial exploratory FX10 and FX17 spectral surface":tab==="fusion"?"FX10 and FX17 provisional 3D spectral associations":"FX10 and FX17 measured pixel spectra and indices"} allowFullScreen/>}
  </div>;
}

export function ScaleExplorer() {
  const [factor,setFactor]=useState(1.0288746669066682);
  return <div className="scale-explorer"><h3>Understand the scale change</h3><p>The initial setting is the fitted D405 correction, 1.0288747×. Other settings are mathematical sensitivity examples. Lengths and areas of the same selected D405 geometry follow these powers; a volume factor is only a mathematical example, not a measured plant volume.</p>
    <label htmlFor="scale-factor">Scale factor shown: <strong>{factor.toFixed(6)}×</strong></label>
    <input id="scale-factor" type="range" min=".8" max="1.2" step="any" value={factor} onChange={e=>setFactor(+e.target.value)}/><button onClick={()=>setFactor(1.0288746669066682)}>Reset to fitted D405 correction</button>
    <div className="metric-grid">{[["Length",factor],["Area",factor**2],["Volume",factor**3]].map(([name,value])=><div key={name}><strong>{((Number(value)-1)*100).toFixed(2)}%</strong><span>{name} change</span></div>)}</div>
    <p>A 10 cm observed chord would become {(10*factor).toFixed(3)} cm. The number of observed points, missing leaf tips and occluded surfaces are unchanged by this mathematical rescaling. The mixed RGB-stereo/L515 pipeline must be recalculated and checked if its sensor scales disagree; this slider does not alter the saved result.</p>
  </div>;
}
