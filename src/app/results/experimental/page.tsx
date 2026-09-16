import type { Metadata } from "next";
import ResultsNavigation from "@/components/ResultsNavigation";

export const metadata: Metadata = {
  title: "Experimental Results | PhenoFusion3D",
  description:
    "Experimental hyperspectral and RGB-D fusion results for the 20260828 and test_plant_20260828120800_best_lighting datasets.",
};

const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
const report = `${basePath}/experimental-results/viewer/index.html`;

const metrics = [
  ["427", "calibrated wavelength bands", "approximately 398–1720 nm"],
  ["10,485", "measured spectral 3D points", "across three plants"],
  ["44,430,791", "legacy ICP scene points", "95 RGB-D frames processed"],
  ["3.31%", "plant-height MAPE", "three manually measured plants"],
];

export default function ExperimentalResults() {
  return (
    <main className="min-h-screen bg-[#050a0a] text-[#f0fdf4]">
      <ResultsNavigation current="/results/experimental/" />
      <header className="border-b border-green-900/40 bg-[radial-gradient(circle_at_80%_10%,rgba(34,211,238,0.14),transparent_32%)]">
        <div className="mx-auto max-w-7xl px-6 pb-14 pt-12">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">
            Experimental Results · FX10 + FX17 + RGB-D ICP
          </p>
          <h1 className="mt-4 max-w-5xl text-4xl font-semibold leading-tight text-white sm:text-6xl">
            Hyperspectral measurements fused with three-dimensional plant geometry
          </h1>
          <p className="mt-6 max-w-4xl text-lg leading-8 text-green-100/70">
            Calibrated hyperspectral measurements, RGB-D trait evidence, point-level spectral inspection and candidate global placement for the same three-plant acquisition.
          </p>

          <div className="mt-9 grid gap-4 lg:grid-cols-2" aria-label="Source datasets">
            <div className="rounded-2xl border border-cyan-300/30 bg-cyan-950/20 p-6">
              <p className="text-xs font-semibold uppercase tracking-widest text-cyan-300">Hyperspectral dataset</p>
              <p className="mt-3 font-mono text-2xl font-semibold text-white">20260828</p>
              <p className="mt-3 leading-7 text-green-100/65">Paired Specim FX10 and FX17 recordings: <span className="font-mono text-cyan-100">001-specim-fx10</span> and <span className="font-mono text-cyan-100">001-specim-fx17</span>.</p>
            </div>
            <div className="rounded-2xl border border-lime-300/30 bg-green-950/30 p-6">
              <p className="text-xs font-semibold uppercase tracking-widest text-lime-300">RGB-D dataset</p>
              <p className="mt-3 break-all font-mono text-xl font-semibold text-white sm:text-2xl">test_plant_20260828120800_best_lighting</p>
              <p className="mt-3 leading-7 text-green-100/65">945 colour frames, 945 aligned depth frames, saved intrinsics and an existing 95-frame ICP reconstruction.</p>
            </div>
          </div>

          <p className="mt-5 rounded-xl border border-amber-300/20 bg-amber-950/20 px-5 py-4 leading-7 text-amber-100/85">
            The captures contain the same three plants and scene landmarks but were sequential rather than simultaneous, approximately 5 minutes 42 seconds apart. Small leaf movement remains a registration uncertainty.
          </p>

          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {metrics.map(([value, label, note]) => (
              <div key={label} className="rounded-xl border border-green-700/30 bg-green-950/30 p-5">
                <p className="text-2xl font-semibold text-lime-300">{value}</p>
                <p className="mt-2 text-sm font-semibold text-white">{label}</p>
                <p className="mt-1 text-xs leading-5 text-green-100/55">{note}</p>
              </div>
            ))}
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-[1600px] px-3 py-10 sm:px-6" aria-labelledby="report-title">
        <div className="mx-auto mb-6 flex max-w-7xl flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-cyan-300">Complete evidence report</p>
            <h2 id="report-title" className="mt-2 text-3xl font-semibold text-white">Experimental findings and interactive results</h2>
          </div>
          <a href={report} className="rounded-full bg-cyan-300 px-5 py-3 text-sm font-semibold text-[#031615] transition hover:bg-cyan-200">Open full-page report ↗</a>
        </div>
        <p className="mx-auto mb-6 max-w-7xl leading-7 text-green-100/65">
          The embedded report contains calibration evidence, fourteen spectral indices, manual trait comparisons, cross-modal registration, interactive per-point spectra and global-scene placement. Grey geometry is explicitly unmeasured; no spectra are invented for occluded surfaces.
        </p>
        <iframe
          src={report}
          title="Experimental hyperspectral and RGB-D fusion findings"
          className="h-[1200px] w-full rounded-2xl border border-cyan-300/25 bg-[#f5f2e9] shadow-2xl shadow-cyan-950/20"
          allowFullScreen
        />
      </section>

      <footer className="border-t border-green-900/40 px-6 py-10 text-center text-sm text-green-100/50">
        Use the navigation above to return home or open another results study.
      </footer>
    </main>
  );
}
