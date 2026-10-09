"use client";

import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

const root = `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/results/final-sprint-20260928/geometry`;
type Model = { id: string; label: string; stage: string; plant: string; file: string; pointCount: number; description: string; download?: string; downloadLabel?: string; bounds: { min: number[]; max: number[] } };
type SceneHandle = { scene: THREE.Scene; camera: THREE.PerspectiveCamera; controls: OrbitControls; renderer: THREE.WebGLRenderer; points: THREE.Points | null; radius: number };

export default function StudyGeometryViewer() {
  const mount = useRef<HTMLDivElement>(null);
  const scene = useRef<SceneHandle | null>(null);
  const [models, setModels] = useState<Model[]>([]);
  const [stage, setStage] = useState("cleaned");
  const [plant, setPlant] = useState("all");
  const [status, setStatus] = useState("Loading model catalogue…");
  const [error, setError] = useState("");
  const [size, setSize] = useState(2);
  const [spin, setSpin] = useState(false);
  const active = models.find(m => m.stage === stage && m.plant === plant);
  function view(direction: string) {
    const s = scene.current;
    if (!s) return;
    const d = s.radius * 2.9 / Math.max(Math.min(1,s.camera.aspect),.15);
    const p: Record<string, number[]> = { Front: [0,.25,1], Back: [0,.25,-1], Left: [-1,.25,0], Right: [1,.25,0], Top: [0,1,.001], Below: [0,-1,.001] };
    s.camera.position.fromArray(p[direction] ?? p.Front).multiplyScalar(d);
    s.controls.target.set(0,0,0);
    s.controls.update();
  }
  useEffect(() => {
    const abort = new AbortController();
    fetch(`${root}/manifest.json`, { signal: abort.signal }).then(r => { if (!r.ok) throw Error(`Catalogue: ${r.status}`); return r.json(); }).then(d => setModels(d.models)).catch(e => { if (e.name !== "AbortError") setError(String(e)); });
    return () => abort.abort();
  }, []);
  useEffect(() => {
    if (!mount.current) return;
    let renderer: THREE.WebGLRenderer;
    try { renderer = new THREE.WebGLRenderer({ antialias: true }); } catch { setError("3D rendering is unavailable in this browser. Use the downloadable point clouds below."); return; }
    const el = mount.current;
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.domElement.setAttribute("aria-label", "Interactive reconstruction: drag to rotate, scroll to zoom");
    el.appendChild(renderer.domElement);
    const world = new THREE.Scene(); world.background = new THREE.Color("#09202a");
    const camera = new THREE.PerspectiveCamera(42, 1, .0001, 100);
    const controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.autoRotateSpeed = .65;
    scene.current = { scene: world, camera, controls, renderer, points: null, radius: 1 };
    const resize = () => { const w = el.clientWidth, h = el.clientHeight; renderer.setSize(w,h,false); const oldFit=Math.max(Math.min(1,camera.aspect),.15); camera.aspect = w / Math.max(h,1); const newFit=Math.max(Math.min(1,camera.aspect),.15); if(scene.current?.points) camera.position.sub(controls.target).multiplyScalar(oldFit/newFit).add(controls.target); camera.updateProjectionMatrix(); };
    const observer = new ResizeObserver(resize); observer.observe(el); resize();
    let frame = 0;
    const draw = () => { controls.update(); renderer.render(world,camera); frame = requestAnimationFrame(draw); }; draw();
    return () => { cancelAnimationFrame(frame); observer.disconnect(); controls.dispose(); const points = scene.current?.points; if (points) { points.geometry.dispose(); (points.material as THREE.Material).dispose(); } renderer.dispose(); renderer.domElement.remove(); scene.current = null; };
  }, []);
  useEffect(() => {
    const s = scene.current;
    if (!s) return;
    if (!active) { if (s.points) { s.scene.remove(s.points); s.points.geometry.dispose(); (s.points.material as THREE.Material).dispose(); s.points=null; } return; }
    const abort = new AbortController();
    setStatus(`Loading ${active.label}…`); setError("");
    // Clear the old object immediately so the caption cannot label a previous model.
    if (s.points) { s.scene.remove(s.points); s.points.geometry.dispose(); (s.points.material as THREE.Material).dispose(); s.points = null; }
    fetch(`${root}/${active.file}`, { signal: abort.signal }).then(r => { if (!r.ok) throw Error(`Point cloud: ${r.status}`); return r.arrayBuffer(); }).then(buffer => {
      if (abort.signal.aborted) return;
      const data = new DataView(buffer);
      if (buffer.byteLength < 8 || data.getUint32(0,false) !== 0x50463344) throw Error("Invalid point-cloud header");
      const n = data.getUint32(4,true);
      if (buffer.byteLength !== 8+n*15 || n !== active.pointCount) throw Error("Point-cloud count does not match its evidence manifest");
      const xyz = new Float32Array(n*3), rgb = new Float32Array(n*3);
      for (let i=0;i<n;i++) { const o=8+i*15; for(let j=0;j<3;j++) { xyz[i*3+j]=data.getFloat32(o+j*4,true); const c=data.getUint8(o+12+j)/255; rgb[i*3+j]=c<=.04045?c/12.92:Math.pow((c+.055)/1.055,2.4); } }
      const g = new THREE.BufferGeometry(); g.setAttribute("position",new THREE.BufferAttribute(xyz,3)); g.setAttribute("color",new THREE.BufferAttribute(rgb,3)); g.computeBoundingBox();
      const center = g.boundingBox!.getCenter(new THREE.Vector3()); g.translate(-center.x,-center.y,-center.z); g.computeBoundingSphere();
      s.radius = Math.max(g.boundingSphere!.radius,.001); s.camera.near=s.radius/1000; s.camera.far=s.radius*100; s.camera.updateProjectionMatrix(); s.controls.minDistance=s.radius*.15; s.controls.maxDistance=s.radius*20;
      const material = new THREE.PointsMaterial({ vertexColors:true, size:2, sizeAttenuation:false });
      s.points = new THREE.Points(g,material); s.scene.add(s.points); view("Front"); setStatus(`${n.toLocaleString()} observed points loaded`);
    }).catch(e => { if (e.name !== "AbortError") { setError(String(e)); setStatus("Model unavailable"); } });
    return () => abort.abort();
  }, [active]);
  useEffect(() => { if (scene.current?.points) (scene.current.points.material as THREE.PointsMaterial).size=size; }, [size,status]);
  useEffect(() => { if (scene.current) scene.current.controls.autoRotate=spin; }, [spin]);
  return <div className="study-viewer">
    <div className="viewer-controls">
      <label>Processing stage<select value={stage} onChange={e=>setStage(e.target.value)}>{[["d405","D405 reconstruction"],["l515","L515 reconstruction"],["fused","D405 + L515 · before cleanup"],["cleaned","Cleaned tissue candidates"]].map(([v,l])=><option key={v} value={v}>{l}</option>)}</select></label>
      <label>Plant or scene<select value={plant} onChange={e=>setPlant(e.target.value)}>{["all","P1","P2","P3","P4","P5"].map(p=><option value={p} key={p}>{p==="all"?"All five · combined scene":`Plant ${p.slice(1)}`}</option>)}</select></label>
      <label>Point size <input type="range" aria-label="Point size" min="1" max="5" step=".25" value={size} onChange={e=>setSize(+e.target.value)}/></label>
      <label className="inline-check"><input type="checkbox" checked={spin} onChange={e=>setSpin(e.target.checked)}/> Rotate</label>
    </div>
    <div className="cloud-stage" ref={mount}/>
    <div className="view-buttons">{["Front","Back","Left","Right","Top","Below"].map(v=><button key={v} onClick={()=>view(v)}>{v}</button>)}</div>
    <div className="viewer-caption"><strong>{active?.label ?? "No saved model for this selection"}</strong><p role="status">{status}</p>{error&&<p role="alert">{error}</p>}<p>{active?.description}</p><p>Drag to rotate · scroll to zoom · right-drag to pan. Rendering preserves points; display centring does not change distances. Raw individual views are spatial crops and can contain nearby context.</p>{active?.download&&<a href={`${root}/${active.download}`} download>{active.downloadLabel ?? "Download point cloud PLY (.gz)"} ↗</a>} · <a href={`${root}/manifest.json`}>Coordinates, counts and provenance ↗</a></div>
  </div>;
}
