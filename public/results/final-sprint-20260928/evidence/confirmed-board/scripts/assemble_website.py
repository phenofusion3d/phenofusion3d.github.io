"""Assemble the confirmed-board edition without overwriting historical results.

Scientific arrays and provenance are produced by the stage-specific builders.
This script copies selected evidence, computes publication inventory and checks
laboratory source preservation. It does not publish or commit the website.
"""
from pathlib import Path
import argparse,hashlib,json,shutil

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
OUT=BASE/'website'
EVIDENCE=OUT/'evidence/confirmed-board'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def copy(p,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,target)
    assert sha(p)==sha(target)
    return dict(source=p.relative_to(ROOT).as_posix(),destination=target.relative_to(OUT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)

def main():
    selection=read(BASE/'cross_camera/selection.json')
    fusion=read(BASE/'fusion_v1/summary.json')
    clean=read(BASE/'cleanup_v1/result/summary.json')
    manifest=read(OUT/'geometry/manifest.json')
    assert len(manifest['models'])==24
    traits=read(OUT/'traits/website_tables.json')
    assert len(traits['plants'])==5 and sum(len(p['dimensions']) for p in traits['plants'])==47
    for p in ['spectral/index.html','spectral/fusion/index.html','spectral/samples/index.html']:
        assert (OUT/p).exists(),p
    copies=[]
    for p in BASE.glob('*.json'):
        if p.name!='RECHECK_STATUS.json':copies.append(copy(p,EVIDENCE/p.name))
    for p in BASE.glob('*.py'):copies.append(copy(p,EVIDENCE/'scripts'/p.name))
    for p in BASE.glob('*.md'):copies.append(copy(p,EVIDENCE/p.name))
    for dirname in ['cross_camera','l515','hsi_geometry','rgb_run_transfer_paper_v2','independent_numeric_audit','marker_ratio_check']:
        for p in (BASE/dirname).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix.lower() in ['.json','.csv','.npz','.txt','.md','.html','.png','.jpg','.pdf','.svg','.py']:
                copies.append(copy(p,EVIDENCE/p.relative_to(BASE)))
    for name in ['d405_metric/summary.json','l515_metric_v1/result/summary.json','l515_metric_boardgain_v1/result/summary.json']:
        copies.append(copy(BASE/name,EVIDENCE/name))
    copies.append(copy(BASE/'fusion_v1/summary.json',EVIDENCE/'fusion/summary.json'))
    copies.append(copy(BASE/'cleanup_v1/result/summary.json',EVIDENCE/'cleanup/result/summary.json'))
    for p in (ROOT/'generated/final_sprint_website_20261007/spectral_diagnostics').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:
            copies.append(copy(p,OUT/'spectral/diagnostics'/p.relative_to(ROOT/'generated/final_sprint_website_20261007/spectral_diagnostics')))
    geo_validation=BASE/'geometry_asset_validation.json'
    assert geo_validation.exists(),'Geometry builder must save validation at confirmed-board root'
    copies.append(copy(geo_validation,OUT/'evidence/geometry_asset_validation.json'))
    protected=read(ROOT/'generated/research_followthrough_20261007/integration_audit/protected_source_hashes.json')
    checks=[dict(path=r['path'],expected_sha256=r['sha256'],actual_sha256=sha(ROOT/r['path']),unchanged=sha(ROOT/r['path'])==r['sha256']) for r in protected]
    assert all(r['unchanged'] for r in checks),'Protected lab source changed; review before release'
    save(OUT/'evidence/protected_source_verification.json',dict(status='pass',files=len(checks),scope='Source-byte preservation only; no physical laboratory hardware test performed.',checks=checks))
    comparison=selection['comparisons']
    soil=comparison['fixed_soil.median_mm']
    page_data=dict(cleanedPoints=clean['counts']['plants_cleaned'],d405Points=fusion['d405_points'],fusedPoints=fusion['fused_points'],addedL515Points=fusion['l515_added_points'],
        selectedL515Label='board-derived empirical depth correction',
        alignmentSummary=f"On the same 62 fixed matched-soil observations, the corrected-depth candidate reduced median disagreement from {soil['native']:.2f} mm to {soil['boardgain']:.2f} mm compared with the newly metric native-depth candidate. The selected 90th percentile is 10.33 mm and maximum 26.04 mm; P4 remains less consistent than P2. These checks also informed candidate selection and are not a final untouched accuracy test. The historical 3.41 mm result used the earlier conditional geometry, so this is not a claim that every old residual improved.",
        heightMappingSummary='We tested a bounded height-dependent model after recovering metric board and scan alignment. Fitting two leaf controls and predicting the third gave errors of 10.08, 14.48 and 174.70 pixels for FX10, and 7.24, 12.28 and 123.43 pixels for FX17. The poorly conditioned case is sensitive to millimetre-scale coordinate changes. This diagnostic failed and is not used for dense spectral assignment. The table-plane result remains useful; the six existing source-supported associations remain provisional.')
    save(BASE/'site_src/study-data.json',page_data)
    requirements=dict(edition='confirmed-board 25 mm, rechecked 7-8 October 2026',overall='reviewed research outputs with explicit unresolved scientific limits',
        completed=['Confirmed board specification saved and metric poses recomputed','D405 metric re-expression and independent full-cloud audit','Two fresh L515 raw-depth reconstructions with raw-frame support verification','Fixed-region rigid camera comparison and frozen matched-soil comparison','Selected fusion and source-mask cleanup recomputed with source indices','24 full-resolution geometry selections and download/provenance','Five-plant descriptors and all 47 manual-reference dimensions reviewed','Both-camera measured spectral samples and six provisional associations at three P5 vertices','Metric HSI table calibration, scan transfer and failed elevated-height generalization test','Both-camera quality and index sensitivity diagnostics'],
        unresolved=[dict(item='Traceable dimensional accuracy',reason='No independent print tolerance, session-certified depth unit and external measurement target.'),dict(item='Gap-free 360 degree plant geometry',reason='Missing coverage, fine tips, occlusion and motion remain.'),dict(item='Physical trait accuracy statistics',reason='No accepted anatomical/reference pairs; confirmed scale alone is insufficient.'),dict(item='Dense 3D spectral fusion across five plants',reason='Only three P5 material controls; height model fails heldout predictions.'),dict(item='Calibrated reflectance and physiological scores',reason='Unknown white-board reflectance and unconfirmed shutter-dark capture.'),dict(item='Generalisation to arbitrary datasets and lab operation',reason='Single reviewed study; no new hardware or independent-dataset validation.')],
        prior_results_preserved=True,pushed=False,live_publication_verified=False,lab_source_changed=False)
    save(OUT/'study_requirements.json',requirements)
    save(OUT/'study-data.json',page_data)
    inventory=[]
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.name not in ['website_provenance.json']:
            inventory.append(dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
    assert max(r['bytes'] for r in inventory)<100_000_000,'GitHub per-file size limit exceeded'
    save(OUT/'website_provenance.json',dict(schema='phenofusion.confirmed-board.website.v1',source_root='PhenoFusion3D',asset_files=len(inventory),total_bytes=sum(r['bytes'] for r in inventory),files=inventory,exact_evidence_copies=copies,
        transformations=['Geometry display rotates board Z-up to Three.js Y-up; position is rounded to float32 only for the display file.','PLY downloads retain full selected source records and roundtrip-verified gzip compression.','Spectral spatial IDs remapped by original camera and source-point identity; measured spectra retained.'],
        publication='Prepared locally for the requested static website; no push or remote publication performed.'))
    print(json.dumps(dict(files=len(inventory),bytes=sum(r['bytes'] for r in inventory),protected_sources=len(checks),page_data=page_data),indent=2))

if __name__=='__main__':main()
