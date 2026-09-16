import type { Metadata } from "next";
import ResultsNavigation from "@/components/ResultsNavigation";

export const metadata: Metadata = {
  title: "Manual Validation | PhenoFusion3D",
  description:
    "Manual versus RGB-D software trait validation for dataset test_plant_20260828120800_best_lighting.",
};

const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
const validationRoot = `${basePath}/experimental-results/viewer/rgbd_icp/validation`;
const report = `${validationRoot}/validation_report.html`;

const metrics = [
  ["3.31%", "plant-height MAPE", "three plants"],
  ["4.25%", "matched-leaf length MAPE", "nine guided leaf matches"],
  ["5.45%", "matched-leaf width MAPE", "nine guided leaf matches"],
  ["9", "matched leaves", "three per plant"],
];

export default function ManualValidation() {
  return (
    <main className="min-h-screen bg-[#050a0a] text-[#f0fdf4]">
      <ResultsNavigation current="/results/manual-validation/" />
      <header className="border-b border-green-900/40 bg-[radial-gradient(circle_at_80%_10%,rgba(251,191,36,0.12),transparent_32%)]">
        <div className="mx-auto max-w-7xl px-6 pb-14 pt-12">
          <p className="text-xs font-semibold uppercase tracking-[0.24em] text-amber-300">Manual Validation · RGB-D trait evaluation</p>
          <h1 className="mt-4 max-w-5xl text-4xl font-semibold leading-tight text-white sm:text-6xl">
            Manual measurements compared with software-derived plant traits
          </h1>
          <p className="mt-6 max-w-4xl text-lg leading-8 text-green-100/70">
            Physical plant-height and selected leaf measurements were compared with corresponding measurements derived from calibrated D405 RGB-D points for succulent/jade, Coleus and fuzzy kalanchoe.
          </p>

          <div className="mt-9 rounded-2xl border border-amber-300/30 bg-amber-950/20 p-6">
            <p className="text-xs font-semibold uppercase tracking-widest text-amber-300">Validated RGB-D dataset</p>
            <p className="mt-3 break-all font-mono text-xl font-semibold text-white sm:text-2xl">test_plant_20260828120800_best_lighting</p>
            <p className="mt-3 max-w-4xl leading-7 text-green-100/65">Manual annotations were confirmed as millimetres. The analysis covers three plant heights and nine guided leaf correspondences, with separate length and width comparisons and image-level audit evidence.</p>
          </div>

          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {metrics.map(([value, label, note]) => (
              <div key={label} className="rounded-xl border border-amber-300/20 bg-green-950/30 p-5">
                <p className="text-2xl font-semibold text-amber-300">{value}</p>
                <p className="mt-2 text-sm font-semibold text-white">{label}</p>
                <p className="mt-1 text-xs leading-5 text-green-100/55">{note}</p>
              </div>
            ))}
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-7xl border-b border-green-900/40 px-6 py-12">
        <h2 className="text-3xl font-semibold text-white">Validation scope</h2>
        <div className="mt-6 grid gap-5 lg:grid-cols-2">
          <div className="rounded-xl border border-green-700/30 bg-green-950/25 p-6">
            <h3 className="text-xl font-semibold text-lime-300">Evidence included</h3>
            <ul className="mt-4 list-disc space-y-3 pl-5 leading-7 text-green-100/70">
              <li>Plant height for all three specimens, reported separately from leaf dimensions.</li>
              <li>Three matched leaves per plant, each with manual value, software value, signed difference and percentage error.</li>
              <li>Audit images showing the selected RGB-D landmarks for every matched leaf.</li>
              <li>Exploratory automatic leaf-segment results retained separately from the guided comparisons.</li>
            </ul>
          </div>
          <div className="rounded-xl border border-amber-300/25 bg-amber-950/15 p-6">
            <h3 className="text-xl font-semibold text-amber-300">Interpretation limits</h3>
            <ul className="mt-4 list-disc space-y-3 pl-5 leading-7 text-green-100/70">
              <li>The leaf result uses guided correspondence; automatic cross-view leaf identity was not validated.</li>
              <li>The matched-leaf values are calibrated leaf-plane distances, not curved leaf-surface lengths.</li>
              <li>Visible image segments are not guaranteed biological leaf counts.</li>
              <li>These errors describe this three-plant validation set and do not establish universal system accuracy.</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-[1600px] px-3 py-10 sm:px-6" aria-labelledby="validation-report-title">
        <div className="mx-auto mb-6 flex max-w-7xl flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-amber-300">Complete validation evidence</p>
            <h2 id="validation-report-title" className="mt-2 text-3xl font-semibold text-white">Plant and matched-leaf results</h2>
          </div>
          <a href={report} className="rounded-full bg-amber-300 px-5 py-3 text-sm font-semibold text-[#171006] transition hover:bg-amber-200">Open full-page report ↗</a>
        </div>
        <iframe
          src={report}
          title="Manual versus software RGB-D trait validation report"
          className="h-[1400px] w-full rounded-2xl border border-amber-300/25 bg-[#f7f9f7] shadow-2xl shadow-amber-950/20"
          allowFullScreen
        />

        <div className="mx-auto mt-6 flex max-w-7xl flex-wrap gap-3">
          <a href={`${validationRoot}/plant_height_comparison.csv`} className="rounded-lg border border-green-700/40 px-4 py-3 text-sm text-lime-300 hover:bg-green-900/30">Plant-height comparisons · CSV ↗</a>
          <a href={`${validationRoot}/matched_leaf_comparison.csv`} className="rounded-lg border border-green-700/40 px-4 py-3 text-sm text-lime-300 hover:bg-green-900/30">Matched-leaf comparisons · CSV ↗</a>
          <a href={`${validationRoot}/leaf_aggregate_comparison.csv`} className="rounded-lg border border-green-700/40 px-4 py-3 text-sm text-lime-300 hover:bg-green-900/30">Automatic aggregate comparison · CSV ↗</a>
          <a href={`${validationRoot}/validation_results.json`} className="rounded-lg border border-green-700/40 px-4 py-3 text-sm text-lime-300 hover:bg-green-900/30">Complete validation results · JSON ↗</a>
        </div>
      </section>

      <footer className="border-t border-green-900/40 px-6 py-10 text-center text-sm text-green-100/50">
        Use the navigation above to return home or open another results study.
      </footer>
    </main>
  );
}
