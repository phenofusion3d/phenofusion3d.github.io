"""Auditable descriptive diagnostics of preserved, measured camera-space spectra."""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from processing.research_workspace.spectral_viewer import load_spectral_result
from processing.research_workspace.spectral_extract import _indices

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "generated/research_spectral_extension_20261007/full_spectral_review/sensors"
REGIONS = [f"R{i}" for i in range(1, 6)]
COLORS = ["#b26c18", "#157d9c", "#42833d", "#9560a7", "#c5574b"]
WARNING = ("Q=(DN-D)/(W-D) uses an unconfirmed scan-tail offset. Q0=DN/W assumes zero offset. "
           "The board reflectance spectrum is unknown. These are reference-relative signals, not calibrated reflectance. "
           "R1–R5 are independently reviewed scan regions, not operator-confirmed 3D plant identities. "
           "Samples are spatially correlated; distribution ranges are not confidence intervals or biological replicates.")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def stats(values):
    a = np.asarray(values, dtype=np.float64).ravel()
    a = a[np.isfinite(a)]
    if not len(a):
        return {"n": 0, **{k: None for k in ("min", "p05", "p10", "p25", "median", "p75", "p90", "p95", "max", "mean", "sd_population")}}
    qs = np.percentile(a, [0, 5, 10, 25, 50, 75, 90, 95, 100])
    return {"n": int(len(a)), **dict(zip(("min", "p05", "p10", "p25", "median", "p75", "p90", "p95", "max"), map(float, qs))),
            "mean": float(a.mean()), "sd_population": float(a.std())}


def write_csv(name, records):
    keys = list(dict.fromkeys(k for r in records for k in r))
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, keys); w.writeheader()
        for r in records:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in r.items()})


def savefig(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=180, bbox_inches="tight")
    fig.savefig(OUT / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def measure_index(sensor, region, name, use, q, q0, flags, flags0):
    valid = use & np.isfinite(q) & (flags == 0)
    valid0 = use & np.isfinite(q0) & (flags0 == 0)
    paired = valid & valid0
    difference = q[paired].astype(np.float64) - q0[paired].astype(np.float64)
    return {"sensor": sensor, "region": region, "descriptor": name, "sample_n": int(use.sum()),
            "valid_q_n": int(valid.sum()), "valid_q0_n": int(valid0.sum()), "paired_n": int(paired.sum()),
            "valid_q_percent": float(100 * valid.sum() / use.sum()),
            "q": stats(q[valid]), "q0": stats(q0[valid0]), "paired_q_minus_q0": stats(difference),
            "paired_absolute_difference": stats(np.abs(difference)),
            "index_flag_sample_counts_q": {str(bit): int(np.sum(use & ((flags & bit) != 0))) for bit in [1, 2, 4, 8, 16]},
            "index_flag_sample_counts_q0": {str(bit): int(np.sum(use & ((flags0 & bit) != 0))) for bit in [1, 2, 4, 8, 16]}}


def main():
    if (OUT / "diagnostics.json").exists():
        raise FileExistsError("Preserve completed diagnostics; use a fresh output folder")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white"})
    hashes, sensors, quality, band_rows, index_rows, verification = {}, {}, [], [], [], []
    for sensor in ["fx10", "fx17"]:
        folder = SOURCE / sensor
        for name in ["measured_spectra.npz", "measured_spectra.metadata.json", "summary.json", "reference_profiles.npz", "input_config.json"]:
            p = folder / name; hashes[p.relative_to(ROOT).as_posix()] = sha(p)
        arrays, summary = load_spectral_result(folder)
        q, q0, flags = arrays["Q_assumed_or_confirmed_dark"], arrays["Q_zero_offset"], arrays["band_quality_flags"]
        wavelengths = arrays["wavelength_nm"]
        patch_region = {p["patch_id"]: p["region_id"] for p in summary["patches"]}
        region_ids = np.array([patch_region[int(p)] for p in arrays["patch_id"]])
        groups = {"all_reviewed_regions": np.ones(len(q), bool), **{r: region_ids == r for r in REGIONS}}
        with np.load(folder / "reference_profiles.npz", allow_pickle=False) as ref:
            W = ref["W_board"][:, arrays["detector_column"]].T
            D = ref["D_dark"][:, arrays["detector_column"]].T
        reproduced_q = np.full_like(q, np.nan); reproduced_q0 = np.full_like(q0, np.nan)
        valid = (flags & 31) == 0
        np.divide(arrays["raw_DN"].astype(np.float32) - D, W - D, out=reproduced_q, where=valid)
        np.divide(arrays["raw_DN"].astype(np.float32), W, out=reproduced_q0, where=valid)
        assert np.array_equal(q, reproduced_q, equal_nan=True)
        assert np.array_equal(q0, reproduced_q0, equal_nan=True)
        verification.append({"sensor": sensor, "measured_npz_metadata_and_canonical_dn_hashes_verified": True,
                             "Q_Q0_exactly_reproduced_from_saved_DN_and_references": True,
                             "sample_count": len(q), "bands": len(wavelengths)})
        sensors[sensor] = dict(arrays=arrays, summary=summary, groups=groups, region_ids=region_ids)
        for region, use in groups.items():
            f, x, z = flags[use], q[use], q0[use]
            pair = np.isfinite(x) & np.isfinite(z)
            strict = pair & (f == 0)
            record = {"sensor": sensor, "region": region, "sample_n": int(use.sum()), "band_n": len(wavelengths),
                      "sample_band_cells": int(x.size), "finite_q_cells": int(np.isfinite(x).sum()),
                      "finite_q0_cells": int(np.isfinite(z).sum()), "paired_finite_cells": int(pair.sum()),
                      "strict_clear_flag_cells": int(strict.sum()),
                      "q_valid_cell_percent": float(100 * np.isfinite(x).mean()),
                      "samples_with_any_Q": int(np.any(np.isfinite(x), axis=1).sum()),
                      "samples_all_bands_Q": int(np.all(np.isfinite(x), axis=1).sum()),
                      "samples_all_bands_strict": int(np.all(strict, axis=1).sum()),
                      "q_minus_q0_all_paired_cells": stats(x[pair].astype(np.float64) - z[pair].astype(np.float64)),
                      "absolute_q_minus_q0_strict_cells": stats(np.abs(x[strict].astype(np.float64) - z[strict].astype(np.float64)))}
            for name, bit in summary["band_flags"].items():
                selected = (f & bit) != 0
                record[name + "_cells"] = int(selected.sum())
                record[name + "_samples"] = int(np.any(selected, axis=1).sum())
            quality.append(record)
            for b, wavelength in enumerate(wavelengths):
                same = pair[:, b]
                delta = x[same, b].astype(np.float64) - z[same, b].astype(np.float64)
                band_rows.append({"sensor": sensor, "region": region, "source_band_zero_based": b,
                                  "wavelength_nm": float(wavelength), "sample_n": int(use.sum()),
                                  "paired_valid_n": int(same.sum()), "paired_valid_percent": float(100 * same.mean()),
                                  "strict_valid_n": int(strict[:, b].sum()),
                                  "q": stats(x[same, b]), "q0": stats(z[same, b]),
                                  "q_minus_q0": stats(delta), "absolute_q_minus_q0": stats(abs(delta))})

        # Each sensor spectrum uses paired finite sample IDs at every wavelength;
        # the accepted sample set can still change between wavelengths.
        fig, axes = plt.subplots(5, 1, figsize=(10, 14), sharex=True, constrained_layout=True)
        for r, color, ax in zip(REGIONS, COLORS, axes):
            rows = [b for b in band_rows if b["sensor"] == sensor and b["region"] == r]
            xs = [b["wavelength_nm"] for b in rows]
            for mode, style, label in [("q", "-", "Q: assumed tail offset"), ("q0", "--", "Q0: zero offset")]:
                ax.plot(xs, [b[mode]["median"] for b in rows], style, color=color if mode == "q" else "#444444", lw=1.5, label=label)
                ax.fill_between(xs, [b[mode]["p10"] for b in rows], [b[mode]["p90"] for b in rows], color=color if mode == "q" else "#666666", alpha=.13)
            n = int(groups[r].sum()); ax.set_title(f"{r}: {n:,} measured samples", loc="left", fontsize=11)
            ax.set_ylabel("Reference-relative signal")
            ax.grid(alpha=.18)
        axes[0].legend(fontsize=9, ncol=2); axes[-1].set_xlabel("Recorded wavelength (nm)")
        fig.suptitle(f"{sensor.upper()} Q and Q0 sensitivity by scan region\nMedians and 10th–90th percentile ranges; not confidence intervals", fontsize=14)
        savefig(fig, f"{sensor}_q_q0_spectra")

    a10 = sensors["fx10"]["arrays"]; s10 = sensors["fx10"]["summary"]
    index_names = list(s10["index_specs_applied"])
    # Verify saved descriptors including exact masks, not only aggregate medians.
    rebuilt = {k: v.copy() for k, v in a10.items()}
    config = json.loads((SOURCE / "fx10/input_config.json").read_text())
    _indices(rebuilt, SimpleNamespace(wavelength_nm=a10["wavelength_nm"]), config, s10["normalization"])
    for name in ["indices_dark", "indices_zero", "index_flags_dark", "index_flags_zero"]:
        assert np.array_equal(rebuilt[name], a10[name], equal_nan=True)
    verification.append({"FX10_six_saved_descriptors_and_flags_reproduced_exactly": True})
    for region, use in sensors["fx10"]["groups"].items():
        for j, name in enumerate(index_names):
            index_rows.append(measure_index("fx10", region, name, use, a10["indices_dark"][:, j], a10["indices_zero"][:, j],
                                            a10["index_flags_dark"][:, j], a10["index_flags_zero"][:, j]))

    # New, bounded FX17 diagnostic: only two recorded in-range bands, no new
    # reflectance/physiological claim and no change to prior extraction products.
    a17 = sensors["fx17"]["arrays"]; s17 = sensors["fx17"]["summary"]
    b17 = [int(np.argmin(abs(a17["wavelength_nm"] - target))) for target in [1300, 1450]]
    actual = a17["wavelength_nm"][b17]
    assert len(set(b17)) == 2 and np.max(abs(actual - [1300, 1450])) <= 2
    ratio_arrays = {}
    for q_name, mode in [("Q_assumed_or_confirmed_dark", "q"), ("Q_zero_offset", "q0")]:
        parts = a17[q_name][:, b17].astype(np.float64)
        ff = a17["band_quality_flags"][:, b17]
        flags = np.zeros(len(parts), np.uint8)
        value = np.full(len(parts), np.nan)
        stable = parts[:, 1] > .01
        np.divide(parts[:, 0], parts[:, 1], out=value, where=stable)
        reference_rows = np.zeros(len(parts), bool)
        for key in ["white_roi", "dark_roi"]:
            lo, hi, _, _ = s17["normalization"][key]
            reference_rows |= (a17["scan_line"] >= lo) & (a17["scan_line"] < hi)
        for bit, mask in [(1, np.any((ff & 31) != 0, axis=1)), (2, np.any((ff & 32) != 0, axis=1)),
                          (4, ~stable), (8, reference_rows), (16, ~np.isfinite(value))]:
            flags[mask] |= bit
        value[flags != 0] = np.nan
        ratio_arrays[mode] = value; ratio_arrays["flags_" + mode] = flags
    ratio_rows = [measure_index("fx17", r, "SR_1300_1450_provisional", use, ratio_arrays["q"], ratio_arrays["q0"],
                                ratio_arrays["flags_q"], ratio_arrays["flags_q0"])
                  for r, use in sensors["fx17"]["groups"].items()]
    np.savez_compressed(OUT / "fx17_ratio_samples.npz", warning=np.array(WARNING), source_measured_npz_sha256=np.array(sha(SOURCE / "fx17/measured_spectra.npz")),
                        sample_id=np.arange(len(a17["raw_DN"]), dtype=np.int32), scan_line=a17["scan_line"], detector_column=a17["detector_column"],
                        patch_id=a17["patch_id"], source_band_zero_based=np.array(b17), actual_wavelength_nm=actual, **ratio_arrays)
    sample_rows = [{"sample_id": i, "scan_line": int(a17["scan_line"][i]), "detector_column": int(a17["detector_column"][i]),
                    "patch_id": int(a17["patch_id"][i]), "region": str(sensors["fx17"]["region_ids"][i]),
                    "Q1301_56_div_Q1449_68": float(ratio_arrays["q"][i]) if np.isfinite(ratio_arrays["q"][i]) else None,
                    "Q0_1301_56_div_Q0_1449_68": float(ratio_arrays["q0"][i]) if np.isfinite(ratio_arrays["q0"][i]) else None,
                    "flags_q": int(ratio_arrays["flags_q"][i]), "flags_q0": int(ratio_arrays["flags_q0"][i])}
                   for i in range(len(a17["raw_DN"]))]
    write_csv("fx17_ratio_samples.csv", sample_rows)

    fig, axes = plt.subplots(2, 1, figsize=(11, 6), constrained_layout=True)
    for sensor, ax in zip(["fx10", "fx17"], axes):
        matrix = np.array([[r["paired_valid_percent"] for r in band_rows if r["sensor"] == sensor and r["region"] == region] for region in REGIONS])
        waves = sensors[sensor]["arrays"]["wavelength_nm"]
        im = ax.imshow(matrix, aspect="auto", origin="upper", extent=[waves[0], waves[-1], 5.5, .5], cmap="viridis", vmin=0, vmax=100)
        ax.set_yticks(range(1, 6), REGIONS); ax.set_xlabel("Recorded wavelength (nm)"); ax.set_title(sensor.upper(), loc="left")
    fig.colorbar(im, ax=axes, label="Paired finite Q/Q0 samples (%)", shrink=.9)
    fig.suptitle("Accepted spectral coverage is wavelength-dependent\nDenominator: all saved samples in the selected scan region", fontsize=13)
    savefig(fig, "valid_band_coverage")

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), constrained_layout=True)
    for sensor, ax in zip(["fx10", "fx17"], axes):
        rows = [r for r in quality if r["sensor"] == sensor and r["region"] in REGIONS]
        kinds = [("samples_all_bands_Q", "All 224 bands Q-valid"), ("outside_reviewed_reference_support_samples", "Outside reference"),
                 ("sample_suspected_clipping_samples", "Any suspected clipping"), ("low_signal_above_dark_advisory_samples", "Any low signal")]
        x = np.arange(5)
        for j, (key, label) in enumerate(kinds):
            ax.bar(x + (j - 1.5) * .19, [100 * r[key] / r["sample_n"] for r in rows], .18, label=label)
        ax.set_xticks(x, REGIONS); ax.set_ylim(0, 105); ax.set_ylabel("Samples (%)"); ax.set_title(sensor.upper(), loc="left"); ax.grid(axis="y", alpha=.18)
    axes[0].legend(ncol=2, fontsize=9)
    fig.suptitle("Quality coverage by scan region\nFlag categories overlap; all-band validity is stricter than one-band validity", fontsize=13)
    savefig(fig, "quality_flags_by_region")

    def distribution_panel(ax, rows, title, ylabel):
        x = np.arange(5)
        for mode, shift, color in [("q", -.10, "#167ca6"), ("q0", .10, "#ba5e22")]:
            med = np.array([r[mode]["median"] for r in rows], float)
            lo = np.array([r[mode]["p10"] for r in rows], float)
            hi = np.array([r[mode]["p90"] for r in rows], float)
            ax.errorbar(x + shift, med, yerr=[med - lo, hi - med], fmt="o", capsize=3, color=color, label=mode.upper())
        ax.set_xticks(x, REGIONS); ax.set_title(title, fontsize=10, loc="left"); ax.set_ylabel(ylabel); ax.grid(axis="y", alpha=.18)

    fig, axes = plt.subplots(3, 2, figsize=(12, 11), constrained_layout=True)
    for name, ax in zip(index_names, axes.ravel()):
        rows = [r for r in index_rows if r["descriptor"] == name and r["region"] in REGIONS]
        distribution_panel(ax, rows, name.replace("_", " "), "Signal descriptor")
    axes[0, 0].legend(); fig.suptitle("FX10: six existing descriptors, Q versus Q0\nMedians with 10th–90th sample percentiles; no plant-health inference", fontsize=14)
    savefig(fig, "fx10_six_index_distributions")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    j = index_names.index("NDVI_800_680")
    for region, color in zip(REGIONS, COLORS):
        use = sensors["fx10"]["groups"][region]
        q = a10["indices_dark"][:, j]; q0 = a10["indices_zero"][:, j]
        both = use & np.isfinite(q) & np.isfinite(q0)
        delta = q[both].astype(np.float64) - q0[both].astype(np.float64)
        axes[0].hist(delta, bins=35, histtype="step", color=color, label=f"{region} (n={len(delta)})")
        axes[1].scatter(q0[both], q[both], s=3, alpha=.3, color=color, rasterized=True)
    axes[0].set_xlabel("NDVI(Q) − NDVI(Q0)"); axes[0].set_ylabel("Measured samples"); axes[0].legend(fontsize=8)
    lo, hi = axes[1].get_xlim(); axes[1].plot([lo, hi], [lo, hi], "k--", lw=.8)
    axes[1].set_xlabel("NDVI(Q0), zero offset"); axes[1].set_ylabel("NDVI(Q), assumed tail offset")
    fig.suptitle("FX10 NDVI sensitivity on identical accepted sample IDs\nA change caused by the offset assumption is not a biological change", fontsize=13)
    savefig(fig, "fx10_ndvi_offset_sensitivity")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)
    distribution_panel(axes[0], [r for r in ratio_rows if r["region"] in REGIONS], "FX17: Q1301.56 / Q1449.68", "Provisional signal ratio")
    axes[0].legend()
    for region, color in zip(REGIONS, COLORS):
        both = sensors["fx17"]["groups"][region] & np.isfinite(ratio_arrays["q"]) & np.isfinite(ratio_arrays["q0"])
        axes[1].scatter(ratio_arrays["q0"][both], ratio_arrays["q"][both], s=3, alpha=.3, color=color, rasterized=True, label=region)
    lo, hi = axes[1].get_xlim(); axes[1].plot([lo, hi], [lo, hi], "k--", lw=.8)
    axes[1].set_xlabel("Ratio using Q0"); axes[1].set_ylabel("Ratio using Q"); axes[1].legend(fontsize=8)
    fig.suptitle("FX17: an in-range two-band descriptor\nBased on the R1300/R1450 formula; Q is not calibrated reflectance or water content", fontsize=13)
    savefig(fig, "fx17_supported_ratio_sensitivity")

    method = {"warning": WARNING,
              "all_saved_samples_included": True, "all_raw_scene_pixels_included": False,
              "sampling": "Existing assistant-reviewed patch interiors sampled every second line and column; no new segmentation or sampling.",
              "region_policy": "R1–R5 independently describe each sensor's scan-order regions. Never assert Rn equals Pn or cross-camera matched pixels.",
              "statistics": "Unweighted empirical distributions over saved samples; pooled results are influenced by patch size. SD is population descriptive SD. No SEM, p-values or confidence intervals; samples are spatially correlated.",
              "Q_policy": "Q and Q0 use the same conservative saved band eligibility (bits 1–16 invalidate; bit 32 is advisory only for Q). No fill, clipping-to-range, extrapolation or NaN-to-zero conversion.",
              "index_policy": "All required bands must have zero quality flags; the original index masks are preserved. Q denominator floor 0.01 is exploratory, not a calibrated noise bound.",
              "offset_difference_policy": "Differences are paired by identical sensor, source pixel and wavelength/descriptor; changes in validity are reported separately.",
              "fx17_ratio": {"name": "SR_1300_1450_provisional", "published_reflectance_formula": "R1300/R1450", "diagnostic_formula": "Q1301.56/Q1449.68; separately Q0_1301.56/Q0_1449.68",
                             "requested_nm": [1300, 1450], "actual_nm": actual.tolist(), "source_band_zero_based": b17,
                             "nearest_band_tolerance_nm": 2, "denominator_floor_Q_units": .01,
                             "scope": "One new reference-relative signal descriptor, inspired by a published leaf reflectance ratio. No inference of LWT, EWT, RWC, plant stress, health or inter-species ranking.",
                             "normalization_limit": "Unknown white-board spectral reflectance, lighting geometry, atmospheric/optical path, and unconfirmed tail offset affect this ratio. The literature's reflectance-to-water relationship is not transferred to these Q measurements."},
              "fx17_excluded_formulas": {"NDVI": "800 and 680 nm absent", "NDRE": "790 and 720 nm absent", "GNDVI": "800 and 550 nm absent", "PRI": "531 and 570 nm absent", "PSRI": "678, 500 and 750 nm absent", "SIPI": "800, 445 and 680 nm absent", "WI_900_970": "900 nm absent; measured range begins at 935.61 nm", "NDWI_860_1240": "860 nm absent", "MSI_1600_820": "820 nm absent"},
              "primary_source": {"authors": "Seelig et al.", "year": 2008, "title": "Relations of remote sensing leaf water indices to leaf water thickness in cowpea, bean, and sugarbeet plants",
                                 "journal": "Remote Sensing of Environment", "volume": 112, "pages": "445–455", "doi": "10.1016/j.rse.2007.05.002",
                                 "url": "https://doi.org/10.1016/j.rse.2007.05.002", "publisher_url": "https://www.sciencedirect.com/science/article/pii/S0034425707002015",
                                 "checked": "2026-10-07", "support": "Primary study explicitly evaluates reflected R1300/R1450. Accessed indexed publisher abstract and formula description; direct publisher open returned 403. Used only to justify formula selection, not a biological calibration of this dataset."}}
    product = {"schema_version": 1, "date": "2026-10-07", "dataset": "2026-09-28 run003", "warning": WARNING,
               "sample_count_total": sum(len(s["arrays"]["raw_DN"]) for s in sensors.values()),
               "sensor_ranges_nm": {k: [float(v["arrays"]["wavelength_nm"][0]), float(v["arrays"]["wavelength_nm"][-1])] for k, v in sensors.items()},
               "methods": method, "region_quality": quality, "band_sensitivity": band_rows,
               "fx10_index_distributions": index_rows, "fx17_ratio_distributions": ratio_rows,
               "fx10_index_specs": s10["index_specs_applied"], "band_flags": s10["band_flags"], "index_flags": s10["index_quality_flags"],
               "source_hashes": hashes, "verification": verification,
               "independent_of_board_size_and_geometry": True, "existing_sources_or_outputs_modified": False}
    dump("diagnostics.json", product); dump("methods_and_sources.json", method)
    write_csv("region_quality.csv", quality); write_csv("band_q_q0_sensitivity.csv", band_rows)
    write_csv("fx10_index_distributions.csv", index_rows); write_csv("fx17_ratio_distributions.csv", ratio_rows)

    def fmt(x):
        return "Unavailable" if x is None else f"{x:.5g}"
    def table(headers, rows):
        return '<div class="scroll"><table><tr>' + ''.join(f'<th>{html.escape(str(h))}</th>' for h in headers) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{html.escape(str(v))}</td>' for v in row) + '</tr>' for row in rows) + '</table></div>'
    qrows = [[r["sensor"].upper(), r["region"], r["sample_n"], r["samples_with_any_Q"], r["samples_all_bands_Q"],
              r["outside_reviewed_reference_support_samples"], r["sample_suspected_clipping_samples"], r["low_signal_above_dark_advisory_samples"]] for r in quality if r["region"] in REGIONS]
    irows = [[r["region"], r["descriptor"], r["valid_q_n"], r["valid_q0_n"], fmt(r["q"]["median"]), fmt(r["q0"]["median"]), fmt(r["paired_q_minus_q0"]["median"])] for r in index_rows]
    rrows = [[r["region"], r["sample_n"], r["paired_n"], fmt(r["q"]["median"]), fmt(r["q0"]["median"]), fmt(r["paired_q_minus_q0"]["median"])] for r in ratio_rows]
    images = [("fx10_q_q0_spectra", "FX10 spectra"), ("fx17_q_q0_spectra", "FX17 spectra"), ("valid_band_coverage", "Accepted spectral coverage"),
              ("quality_flags_by_region", "Quality flags"), ("fx10_six_index_distributions", "Six FX10 descriptors"),
              ("fx10_ndvi_offset_sensitivity", "NDVI sensitivity"), ("fx17_supported_ratio_sensitivity", "FX17 in-range ratio")]
    markup = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>September spectral diagnostics</title><style>body{font:16px/1.65 system-ui;margin:auto;max-width:1250px;padding:28px;color:#172d35;background:#f2f6f7}h1,h2{line-height:1.2}section{padding:24px;background:white;border:1px solid #c8d7dc;border-radius:12px;margin:22px 0}.note{padding:18px;background:#fff4d7;border-left:4px solid #bc7a13}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:9px;text-align:left;border-bottom:1px solid #d5e1e5}th{background:#e7eff2}a{color:#09617c}img{width:100%;height:auto}figure{margin:20px 0}code{word-break:break-word}</style>'
    markup += '<h1>Measured spectral diagnostics: FX10 and FX17</h1><p>28 September capture · 7 October analysis · 13,343 existing measured samples × 224 bands per sensor. This audit covers all saved reviewed samples, not every raw scene pixel.</p>'
    markup += '<p class="note">' + html.escape(WARNING) + '</p>'
    markup += '<p>The newly confirmed checkerboard dimensions do not change these camera-space spectral calculations. Physical spatial registration and trait rescaling are separate deliverables.</p>'
    markup += '<p><a href="diagnostics.json">Full JSON</a> · <a href="region_quality.csv">Quality CSV</a> · <a href="band_q_q0_sensitivity.csv">Every-band CSV</a> · <a href="fx10_index_distributions.csv">Six-index CSV</a> · <a href="fx17_ratio_distributions.csv">FX17 ratio CSV</a> · <a href="fx17_ratio_samples.csv">FX17 per-sample CSV</a> · <a href="fx17_ratio_samples.npz">FX17 per-sample NPZ</a> · <a href="methods_and_sources.json">Methods and source</a></p>'
    markup += '<section><h2>What is accepted in each region?</h2><p>Flags overlap: a sample can be both outside reference coverage and suspected clipped. “All bands” requires all 224 Q values to be finite; a single index only needs its own required bands. Low-signal bands remain advisory for spectra but are excluded from descriptors. No missing value was filled.</p>' + table(["Camera", "Region", "Samples", "Any Q", "All 224 Q", "Outside reference", "Any suspected clipping", "Any low signal"], qrows) + '</section>'
    markup += '<section><h2>Q versus Q0 is a sensitivity analysis</h2><p>Q assumes the final scan tail provides an offset; shutter closure was not confirmed. Q0 instead assumes zero offset. Both retain identical conservative spatial/reference support. Neither is ground truth. Every reported difference compares the same measured sample IDs. All ranges are empirical sample distributions, not confidence intervals.</p>'
    for name, caption in images[:4]:
        markup += f'<figure><a href="{name}.svg"><img src="{name}.png" alt="{caption}"></a><figcaption>{caption} · click for vector SVG.</figcaption></figure>'
    markup += '</section><section><h2>FX10: six existing descriptors</h2><p>NDVI, NDRE, GNDVI, PRI, PSRI and SIPI are computed only from FX10 recorded wavelengths and saved valid bands. Values are exploratory signal descriptors. The region names do not authorize five biological-plant health rankings, and the sample count does not provide independent biological replication.</p>'
    markup += table(["Region", "Descriptor", "Valid Q n", "Valid Q0 n", "Median Q", "Median Q0", "Median paired difference"], irows)
    for name, caption in images[4:6]:
        markup += f'<figure><a href="{name}.svg"><img src="{name}.png" alt="{caption}"></a></figure>'
    markup += '</section><section><h2>FX17: a supported two-band signal ratio</h2><p>The recorded FX17 range is 935.61–1720.23 nm. Standard NDVI, NDRE, GNDVI, PRI, PSRI and SIPI lack their required bands; WI900/970, NDWI860/1240 and MSI1600/820 are likewise unsupported. No visible band is borrowed from FX10.</p>'
    markup += '<p><a href="https://doi.org/10.1016/j.rse.2007.05.002">Seelig et al. (2008)</a> studied the reflected-light ratio R1300/R1450. The corresponding measured FX17 wavelengths are 1301.56 and 1449.68 nm (bands 105 and 147). Here we report Q1301.56/Q1449.68 and the Q0 counterpart only as provisional signal ratios. Unknown board reflectance, assumed offset and acquisition geometry prevent interpreting them as calibrated leaf-water indices or water content.</p>'
    markup += '<p>Both required bands must have clear quality flags; the denominator must exceed 0.01 Q units. This guard is exploratory, not a calibrated physical uncertainty. Rejected samples stay NaN in NPZ and blank in CSV.</p>'
    markup += table(["Region", "Samples", "Paired valid n", "Median ratio Q", "Median ratio Q0", "Median paired difference"], rrows)
    markup += '<figure><a href="fx17_supported_ratio_sensitivity.svg"><img src="fx17_supported_ratio_sensitivity.png" alt="FX17 supported ratio sensitivity"></a></figure></section>'
    markup += '<section><h2>Verification and remaining evidence</h2><p>Saved measured-spectrum metadata and canonical raw-DN hashes passed validation. All Q and Q0 values were reproduced exactly from saved raw samples and reference profiles, including NaNs. Six FX10 descriptor arrays and quality masks were reproduced exactly. All input files were rehashed after analysis and remain unchanged. No source cloud, raw cube, extraction output or application code was edited.</p><p>Reliable physical interpretation still needs a documented panel spectrum, confirmed dark reference at matching settings, and suitable independent biological/reference measurements. Dense 3D assignment requires its own spatial model and visibility validation. The separate pixel-to-3D and per-plant coverage problem is not solved by these spectral summaries.</p><p><a href="verification.json">Verification record</a></p></section></html>'
    (OUT / "index.html").write_text(markup, encoding="utf-8")
    after = {name: sha(ROOT / name) for name in hashes}
    assert hashes == after
    assert all(np.isnan(ratio_arrays[mode][ratio_arrays["flags_" + mode] != 0]).all() for mode in ["q", "q0"])
    assert len(sample_rows) == 5361
    dump("verification.json", {"source_hashes_before": hashes, "source_hashes_after": after, "all_sources_unchanged": True,
                               "checks": verification, "fx17_ratio_invalid_samples_preserve_nan": True,
                               "fx17_source_pixel_coordinates_preserved": True, "new_diagnostic_sample_count": 5361,
                               "figure_count": len(images), "figure_formats": ["PNG", "SVG"], "no_new_spatial_or_physical_claim": True})
    print(json.dumps({"report": (OUT / 'index.html').relative_to(ROOT).as_posix(), "samples": product["sample_count_total"],
                      "FX10_all_region_quality": quality[0], "FX17_all_region_quality": quality[6],
                      "FX10_NDVI": index_rows[0], "FX17_ratio": ratio_rows[0]}, indent=2))


if __name__ == "__main__":
    main()
