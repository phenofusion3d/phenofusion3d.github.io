"use client";
import { useEffect, useState } from "react";

const root = `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/results/final-sprint-20260928/traits`;
const followthrough = `${root}/../review-20261008/traits/index.html`;
type Dimension = {
  id: string;
  dimension: string;
  annotation_cm: number | null;
  ruler_cm: number | null;
  estimate_cm: number | null;
  signed_difference_from_operator_annotation_cm?: number | null;
  status: string;
  reason: string;
  minimum_resolution_action?: string;
};
type Plant = {
  id: string;
  points: number;
  observed_span_cm: number[];
  hull_cm2: number;
  manual_height_cm: number | null;
  height_status: string;
  photo: string;
  notes: string | string[];
  dimensions: Dimension[];
  conditional_comparison_count?: number;
};
const val = (v: number | null | undefined) => v == null ? "Unavailable" : Number(v).toFixed(2);
const signed = (v: number | null | undefined) => v == null ? "Not paired" : `${v >= 0 ? "+" : ""}${v.toFixed(2)}`;
const statusLabels: Record<string, string> = {
  conditional_same_organ_chord_comparison: "Conditional same-organ comparison",
  extent_completeness_diagnostic_not_height_accuracy: "Observed extent only; anatomical height unresolved",
  organ_identity_unresolved: "Organ match unresolved",
  organ_identity_and_type_unresolved: "Organ match and leaf/pod identity unresolved",
  partial_observed_length_definition_mismatch: "Partial observed length; different endpoints",
  reference_discrepancy_and_partial_width: "Reference discrepancy; partial width only",
  attempted_missing_supported_endpoint: "Attempted; supported endpoint missing",
  source_point_anatomy_failed_multiview_check: "Attempted; anatomical match failed across views",
  different_cross_section_descriptive_only: "Different width section; descriptive only",
};

export default function StudyTraits() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    fetch(`${root}/website_tables_v3.json`, { signal: controller.signal })
      .then(response => {
        if (!response.ok) throw Error(`Trait table: ${response.status}`);
        return response.json();
      })
      .then(data => setPlants(data.plants))
      .catch(problem => { if (problem.name !== "AbortError") setError(String(problem)); });
    return () => controller.abort();
  }, []);

  return <div>
    <p><strong>8 October follow-through: 13 conditional comparisons across 8 organs</strong> — 7 lengths and 6 widths from P3 and P5. Each compares a manually reviewed, observed 3D chord with the operator annotation. The table accounts for all 47 manual dimensions, including unsuccessful attempts and unresolved matches.</p>
    <p>User measurements are usable operator references. The remaining qualifications concern matching anatomical endpoints, the width section, and the difference between a naturally curved leaf and a leaf held against a ruler. Signed differences below are conditional comparisons, not independently established model-accuracy scores.</p>
    <p><a href={followthrough} target="_blank" rel="noreferrer">Open the complete trait comparison report, source images and all 47 dispositions</a> · <a href={`${root}/../review-20261008/traits/conditional_comparisons.csv`}>Download the 13 comparisons</a></p>
    {error && <p role="alert">{error}</p>}
    {!plants.length && !error && <p>Loading per-plant measurement evidence…</p>}
    <div className="study-table"><table>
      <caption className="study-fine">Observed geometry at the confirmed-board scale. Z span is retained-cloud extent, not stem-base-to-tip height; canopy hull encloses gaps.</caption>
      <thead><tr><th>Plant</th><th>Cleaned points</th><th>X × Y × Z span (cm*)</th><th>Canopy hull (cm²*)</th><th>Manual height (cm)</th><th>Anatomical height estimate</th></tr></thead>
      <tbody>{plants.map(plant => <tr key={plant.id}>
        <td><a href={`#traits-${plant.id}`}>{plant.id}</a></td>
        <td>{plant.points.toLocaleString()}</td>
        <td>{plant.observed_span_cm.map(value => value.toFixed(2)).join(" × ")}</td>
        <td>{plant.hull_cm2.toFixed(2)}</td>
        <td>{val(plant.manual_height_cm)}<small>operator annotation</small></td>
        <td>Unresolved<small>The actual stem base and very tip are not both identified.</small></td>
      </tr>)}</tbody>
    </table></div>
    <p className="study-fine">The five span-versus-height comparisons in the linked report are retained-extent diagnostics. Their differences are not height accuracy errors or certified completeness percentages. *Centimetres are anchored to the confirmed 25 mm board square. Print tolerance and physical accuracy are not independently established; L515 retains its recorded-depth interpretation limits. Hull area is an observed canopy envelope, not summed leaf area.</p>
    {plants.map(plant => <details id={`traits-${plant.id}`} key={plant.id}>
      <summary>{plant.id} · {plant.dimensions.length} manual dimensions · {plant.conditional_comparison_count ?? 0} conditional comparisons</summary>
      <div className="study-grid">
        <a href={`${root}/${plant.photo}`} target="_blank" rel="noreferrer"><img className="plant-photo" loading="lazy" src={`${root}/${plant.photo}`} alt={`${plant.id} reviewed source image`} /></a>
        <div><h3>Plant {plant.id.slice(1)} measurement status</h3>{(Array.isArray(plant.notes) ? plant.notes : [plant.notes]).map((note, index) => <p key={index}>{note}</p>)}</div>
      </div>
      <div className="study-table"><table>
        <thead><tr><th>Dimension</th><th>Operator (cm)</th><th>Ruler review (cm)</th><th>Observed 3D chord (cm*)</th><th>Signed difference (cm)</th><th>Comparison and remaining gap</th></tr></thead>
        <tbody>{plant.dimensions.map(dimension => <tr key={dimension.id}>
          <td>{dimension.id}</td>
          <td>{val(dimension.annotation_cm)}</td>
          <td>{val(dimension.ruler_cm)}</td>
          <td>{val(dimension.estimate_cm)}</td>
          <td>{signed(dimension.signed_difference_from_operator_annotation_cm)}{dimension.signed_difference_from_operator_annotation_cm != null && <small>3D minus operator; conditional</small>}</td>
          <td>{statusLabels[dimension.status] ?? dimension.status.replaceAll("_", " ")}<small>{dimension.reason}</small>{dimension.minimum_resolution_action && <small>Next: {dimension.minimum_resolution_action}</small>}</td>
        </tr>)}</tbody>
      </table></div>
    </details>)}
  </div>;
}
