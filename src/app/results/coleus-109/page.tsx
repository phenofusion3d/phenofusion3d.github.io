import type { Metadata } from "next";
import Link from "next/link";
import ResultsNavigation from "@/components/ResultsNavigation";

export const metadata: Metadata = {
  title: "Coleus 109: reconstruction recovery | PhenoFusion3D",
  description: "Explore the recovered Coleus scan, compare the earlier result, and understand the remaining gaps and next capture plan.",
};

const base = `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/results/coleus-109/viewer`;
const section = "mx-auto max-w-5xl px-6 py-12 border-b border-green-900/40";
const heading = "mb-5 text-2xl font-semibold text-white sm:text-3xl";
const prose = "space-y-4 text-base leading-8 text-green-100/75";

export default function ColeusRecovery() {
  return <main className="min-h-screen bg-[#050a0a]">
    <ResultsNavigation current="/results/coleus-109/" />
    <header className={section}>
      <Link href="/" className="text-sm text-lime-300 hover:underline">← PhenoFusion3D home</Link>
      <p className="mt-10 text-xs font-semibold uppercase tracking-widest text-lime-400">Reconstruction study · 6 September 2026 · Dataset 20260901122109</p>
      <h1 className="mt-4 max-w-4xl text-4xl font-semibold leading-tight text-white sm:text-6xl">A clearer plant.<br />A view of the remaining gaps.</h1>
      <p className="mt-6 max-w-3xl text-lg leading-8 text-green-100/75">The recovered Coleus model reveals curved leaves and branch connections much more clearly. Explore the full result below, compare the earlier reconstruction, and see what a better capture needs to provide.</p>
      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[['1,143,251', 'reconstructed points'], ['20', 'fused reference views'], ['3 minimum / 7 median', 'supporting camera views per point']].map(([value,label]) => <div key={label} className="rounded-xl border border-green-700/30 bg-green-950/30 p-5"><p className="text-2xl font-semibold text-lime-300">{value}</p><p className="mt-2 text-sm text-green-100/60">{label}</p></div>)}
      </div>
      <p className="mt-6 rounded-xl border border-amber-400/25 bg-amber-950/20 p-5 leading-7 text-amber-100/90">This is an improved reconstruction, not a fully observed, gap-free 360° plant. Hidden surfaces remain incomplete. The visible pot is included, and physical trait accuracy has not yet been validated.</p>
    </header>

    <section className="mx-auto max-w-[1500px] px-3 py-10 sm:px-6" aria-labelledby="viewer-title">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-4"><h2 id="viewer-title" className="text-2xl font-semibold">Explore the complete comparison</h2><a href={`${base}/index.html`} className="rounded-full bg-lime-400 px-5 py-3 text-sm font-semibold text-black">Open full-page viewer ↗</a></div>
      <p className="mb-5 text-sm leading-7 text-green-100/65">The original viewer is preserved unchanged, including both models, source photograph, camera views, rotation, brightness, point size and downloads. Drag to rotate, or select Front, Back, Left, Right, Top and Below. The embedded data is approximately 36 MB, so the first load may take a moment.</p>
      <iframe src={`${base}/index.html`} title="Original Coleus reconstruction comparison viewer" className="h-[950px] w-full rounded-xl border border-green-700/30 sm:h-[850px]" allowFullScreen />
    </section>

    <section className={section}><h2 className={heading}>The older plant's reconstruction was much better</h2><div className={prose}>
      <p>The older test plant ending in 659 and this capture were observed at very different distances. In representative frames, automatically selected coloured-leaf pixels had these depth distributions:</p>
      <div className="overflow-x-auto"><table className="w-full min-w-[450px] text-left text-sm"><thead><tr className="border-b border-green-800"><th className="py-3">Capture</th><th>5th percentile</th><th>Median</th><th>95th percentile</th></tr></thead><tbody><tr className="border-b border-green-900"><td className="py-3">Older plant …659</td><td>13.29 cm</td><td>16.88 cm</td><td>24.88 cm</td></tr><tr><td className="py-3">Coleus …109</td><td>42.06 cm</td><td>45.32 cm</td><td>66.43 cm</td></tr></tbody></table></div>
      <p>31.9% of the selected pixels in the new frame were beyond 50 cm. The <a className="text-lime-300 underline" href="https://www.realsenseai.com/products/stereo-depth-camera-d405/">D405 specification gives an ideal range of 7–50 cm</a>. This is consistent with poorer depth around lower foliage, but does not prove that range caused every error. These diagnostics assume 10,000 raw depth units per metre for both captures; they are not manually verified measurements.</p>
      <p>Stretched depth surfaces were already present in individual frames. Aligning and accumulating those frames preserved or thickened the errors. A previous filter also rejected new surfaces absent from one reference frame, and several reconstruction scripts ignored saved colour-camera distortion. The upside-down preview was a separate display problem.</p>
    </div></section>

    <section className={section}><h2 className={heading}>What recovered the structure</h2><div className={prose}>
      <p>We reconstructed depth from calibrated colour photographs, then applied coloured ICP and 3D surface fusion. This result is not simply the previous sensor-depth ICP with a new threshold.</p>
      <ol className="list-decimal space-y-3 pl-6"><li>Correct lens distortion and jointly refine 44 camera poses and 5,370 scene landmarks using 66,234 image observations. Encoder motion constrains scale.</li><li>Estimate depth from multiple RGB stereo baselines, checking left/right correspondence and repeated depth agreement.</li><li>Align 20 dense clouds with coloured ICP and fuse them in a 3D volume at 0.6 mm voxel spacing and 3.0 mm truncation distance.</li><li>Keep points supported by at least three camera views, reject inconsistent empty-space evidence and background, and remove small isolated noise components.</li><li>Export an upright model using a rigid coordinate transform that preserves distances.</li></ol>
      <p>No generative model or invented leaves and stems were used. Stereo and fusion still estimate surfaces numerically; they are not direct measurements of every surface.</p>
    </div></section>

    <section className={section}><h2 className={heading}>Why gaps remain in a 360° view</h2><div className={prose}>
      <p>An overhead trajectory cannot reveal every leaf underside, overlapping leaf or hidden branch. Repeating alignment cannot recover evidence that no image contains.</p>
      <p>Some visible gaps may also come from difficult image texture, stereo matching or conservative filtering. We have not individually proven the cause of every missing patch. Filling every hole would make a visually closed model, but could invent geometry and bias leaf area or volume.</p>
      <p>All 20 ICP alignments were accepted, with 96.27–99.62% overlap and 0.891–1.361 mm residuals. Median image reprojection error was 0.236 pixels. These numbers describe internal agreement, not millimetre physical accuracy or complete coverage. Supporting views share imagery and are not statistically independent measurements. The 0.6 mm voxel spacing is a processing setting, not an accuracy claim.</p>
    </div></section>

    <section className={section}><h2 className={heading}>A practical plan for a better recording</h2><div className={prose}>
      <ol className="list-decimal space-y-4 pl-6"><li><strong className="text-white">Bring the foliage into useful depth range.</strong> Check the nearest and farthest leaves, including the lower canopy. A closer camera sees a smaller footprint, so use overlapping passes to cover the whole plant.</li><li><strong className="text-white">Record the missing viewpoints.</strong> Add angled passes around the sides and views that expose lower leaves and undersides. If rotating the pot, stop it for each capture and estimate the plant-relative poses; the fixed background should not drive plant alignment.</li><li><strong className="text-white">Keep the scene stable.</strong> Let leaves settle after motion and use steady, diffuse illumination. Inspect RGB and depth during a short pilot scan before recording the complete sequence.</li><li><strong className="text-white">Save the accepted camera settings.</strong> Record calibration, depth scale, timestamps, encoder positions and the preset actually applied. The old code comment mislabels preset 4: the installed SDK identifies 4 as High Density and 3 as High Accuracy. The historical recording does not confirm which preset was accepted.</li><li><strong className="text-white">Verify coverage and scale before committing to a full run.</strong> Reconstruct the pilot, inspect it from all sides, and compare a known-size target and a few manual leaf dimensions. Add views where surfaces remain unsupported.</li></ol>
      <p>These changes should improve the available evidence, but a living plant can still contain surfaces hidden from every accessible angle. A perfect closed surface is not a guaranteed outcome of re-recording.</p>
    </div></section>

    <section className={section}><h2 className={heading}>Files, evidence and the next step</h2><div className={prose}><p>The model is ready for visual review and experimental segmentation. Separate the pot and identify leaves and stems before extracting traits. Validate dimensions against manual measurements; incomplete surfaces cannot support an assumed complete leaf area or volume.</p></div>
      <div className="mt-6 flex flex-wrap gap-3">{[['plant_upright.ply','Upright point cloud · 31 MB'],['plant_rgb_icp.ply','Camera-coordinate cloud · 31 MB'],['RECONSTRUCTION_REPORT.md','Complete technical report'],['summary.json','Result summary'],['icp_diagnostics.json','ICP diagnostics'],['point_evidence.npz','Per-point support evidence']].map(([file,label]) => <a key={file} href={`${base}/${file}`} className="rounded-lg border border-green-700/40 px-4 py-3 text-sm text-lime-300 hover:bg-green-900/30">{label} ↗</a>)}</div>
      <p className="mt-8 text-sm leading-7 text-green-100/50">Methods: <a href="https://open3d.org/html/tutorial/pipelines/colored_pointcloud_registration.html" className="underline">Open3D coloured ICP</a> · <a href="https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html" className="underline">OpenCV calibration and stereo reconstruction</a></p>
      <Link href="/" className="mt-8 inline-block text-lime-300 hover:underline">← Back to the project</Link>
    </section>
  </main>;
}
