"""Lift frozen upper-leaf registration hypotheses onto unchanged measured geometry.

This is exploratory spatial association, not certified pixel correspondence.
No fitting is performed here, and no coordinates or source spectra are altered.
"""
from pathlib import Path
import sys, json, hashlib
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'venv/Lib/site-packages'), str(ROOT)]
import cv2
import numpy as np
import open3d as o3d
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
OUT = HERE/'partial_surface'
OUT.mkdir(exist_ok=True)
REGIONS = ['green_upper', 'red_upper']
frozen_path = HERE/'learned_registration/frozen_candidates.json'
frozen = json.loads(frozen_path.read_text())
cloud_path = ROOT/'generated/research_confirmed_board_20261007/cleanup_v1/result/P5_reference.ply'
cloud = o3d.io.read_point_cloud(str(cloud_path))
xyz = np.asarray(cloud.points)
tree = cKDTree(xyz)
d = ROOT/'generated/research_20260928_improvement_20261007/short_dense_v3'
profile = json.loads((d/'profile.json').read_text())
K, dist = np.array(profile['K']), np.array(profile['dist'])
poses = json.loads((d/'result/icp_diagnostics.json').read_text())
scale = 1.0288746669066682
frames = [1055904, 1215512, 1445026]
views = []
inputs = [frozen_path, cloud_path, d/'profile.json', d/'result/icp_diagnostics.json']
for frame in frames:
    row = next(x for x in poses if x['frame'] == frame)
    assert row['icp_accepted']
    T = np.array(row['transform']); T[:3, 3] *= scale
    path = d/f'rgb/depth_{frame}.npz'; inputs.append(path)
    dep = np.load(path)
    views.append((T, dep['depth']*scale, dep['votes']))
hsi_path = ROOT/'generated/research_followthrough_20261007/spectral/fx10_display_rgb.npy'
rgb_path = ROOT/f'data/main/test_plant_10-7/test_plant_20260928162354/rgb_{frames[0]}.png'
inputs += [hsi_path, rgb_path]
hsi = np.rot90(np.load(hsi_path))
rgb = cv2.cvtColor(cv2.imread(str(rgb_path)), cv2.COLOR_BGR2RGB)/255.

def tissue(a, name):
    r,g,b = np.moveaxis(a, -1, 0)
    if name.startswith('green'):
        return (g > 1.1*r) & (g > 1.05*b) & (g > .15)
    return (r > 1.3*g) & (r > 1.2*b) & (r > .15)

rows = []; summaries = []; model_ids = []
for region_id, name in enumerate(REGIONS, 1):
    entry = next(e for e in frozen['candidates'] if e['region'] == name and e['smoothing'] is None)
    mp = HERE/'learned_registration'/entry['map_npz']; inputs.append(mp)
    data = np.load(mp); origin = data['hsi_origin']; uv = data['rgb_xy']
    domain = cv2.erode(data['supported_hull'].astype('uint8'), np.ones((3,3), np.uint8)).astype(bool)
    yy, xx = np.nonzero(domain)
    lines = xx+origin[0]; cols = 1023-(yy+origin[1]); native_rgb = uv[yy,xx]
    sel = tissue(hsi[yy+origin[1],xx+origin[0]], name)
    ru = np.rint(native_rgb).astype(int)
    valid_bounds = (ru[:,0]>=0)&(ru[:,0]<1280)&(ru[:,1]>=0)&(ru[:,1]<720)
    sel &= valid_bounds
    ids = np.flatnonzero(sel)
    sel[ids] &= tissue(rgb[ru[ids,1],ru[ids,0]], name)
    ids = np.flatnonzero(sel)
    lines,cols,native_rgb = lines[ids],cols[ids],native_rgb[ids]
    n_tissue = len(ids)
    und = cv2.undistortPoints(native_rgb.reshape(-1,1,2),K,dist,P=K)[:,0]
    pix = np.rint(und).astype(int)
    T,z,votes = views[0]
    ok = (pix[:,0]>=0)&(pix[:,0]<z.shape[1])&(pix[:,1]>=0)&(pix[:,1]<z.shape[0])
    ids = np.flatnonzero(ok); u,v = pix[ids].T
    ok[ids] &= np.isfinite(z[v,u])&(z[v,u]>0)&(votes[v,u]>=2)
    ids = np.flatnonzero(ok); u,v = pix[ids].T
    cam = (np.c_[u,v,np.ones(len(u))]@np.linalg.inv(K).T)*z[v,u,None]
    X = cam@T[:3,:3].T+T[:3,3]
    dd, pointids = tree.query(X)
    point_cam = (xyz[pointids]-T[:3,3])@T[:3,:3]
    projected = cv2.projectPoints(point_cam,np.zeros(3),np.zeros(3),K,dist)[0][:,0]
    repro = np.linalg.norm(projected-native_rgb[ids],axis=1)
    support = np.ones(len(ids),np.uint8)
    for T2,z2,v2 in views[1:]:
        X2 = (xyz[pointids]-T2[:3,3])@T2[:3,:3]
        uv2 = X2@K.T; uv2 = np.rint(uv2[:,:2]/uv2[:,2,None]).astype(int)
        good = (X2[:,2]>0)&(uv2[:,0]>=0)&(uv2[:,0]<z2.shape[1])&(uv2[:,1]>=0)&(uv2[:,1]<z2.shape[0])
        ii = np.flatnonzero(good); uu,vv = uv2[ii].T
        good[ii] &= (v2[vv,uu]>=2)&np.isfinite(z2[vv,uu])&(np.abs(X2[ii,2]-z2[vv,uu])<=.012)
        support += good
    keep = (dd<=.003)&(repro<=1.5)&(support>=2)
    for j in np.flatnonzero(keep):
        i = ids[j]
        rows.append((region_id,int(cols[i]),int(lines[i]),int(pointids[j]),float(dd[j]),float(repro[j]),int(support[j]),*map(float,native_rgb[i])))
    summaries.append({'region':name,'region_id':region_id,'model_id':entry['id'],'learned_hull_pixels_after_1px_erosion':int(domain.sum()),'both_images_colour_mask_pixels':n_tissue,'geometry_supported_before_dedup':int(keep.sum()),'model':entry['map_npz']})
    model_ids.append(entry['id'])
rows.sort(key=lambda r:(r[4],r[5],r[0],r[2],r[1]))
seen_points=set();seen_pixels=set();unique=[]
for row in rows:
    if row[3] in seen_points or row[1:3] in seen_pixels:continue
    seen_points.add(row[3]);seen_pixels.add(row[1:3]);unique.append(row)
a=np.array(unique)
assert len(a)
for s in summaries:s['retained_unique_vertices']=int(np.sum(a[:,0]==s['region_id']))
np.savez_compressed(OUT/'projection_hypothesis.npz',region_id=a[:,0].astype('uint16'),fx10_column_line=a[:,1:3].astype('int32'),current_P5_point_index=a[:,3].astype('int64'),reference_xyz=xyz[a[:,3].astype(int)],vertex_distance_m=a[:,4],point_reprojection_px=a[:,5],supporting_rgb_pairs=a[:,6].astype('uint8'),native_rgb_xy=a[:,7:9],mapping_error_rgb_px=np.full(len(a),np.nan))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
evidence={'status':'EXPLORATORY_PARTIAL_UPPER_LEAF_SURFACE','accepted_for_measurement':False,'physical_registration_validated':False,'dense_fusion_complete':False,'calibrated_reflectance':False,'regions':summaries,'total_geometry_supported_before_dedup':len(rows),'retained_source_vertices':len(a),'geometry_method':'Frozen learned image map inside its eroded inlier convex hull, same colour-class tissue in both images; integer native FX10 pixel -> native RGB -> undistorted >=2-vote recovered depth -> unchanged P5 vertex within3mm and1.5px; >=2 of3 supporting stereo views within12mm. Geometry support is not verification of spectral material identity.','model_selection':'Previously frozen base affine/projective candidate ranked only by learned inlier count, spatial spread and fit residual. Upper red/green regions selected for this exploratory illustration after validation evidence was available. No map refitted to checks; demonstration-region selection is post hoc.','mask_policy':'Heuristic green/red colour masks omit pale tissue and leaf boundaries; no full-leaf coverage claim.','rgb_frames':frames,'mapping_error_per_point':'Unknown. Annotation disagreements are sparse, uncertain and not per-point error bounds.','spectral_method':'Read exact native measured pixel; no filled, averaged or interpolated spectrum. Upper leaves may lie outside reference-panel detector columns, so normalized values must remain invalid there.','source_geometry_modified':False,'inputs_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs}}
(OUT/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
print(json.dumps({'regions':summaries,'vertices':len(a)},indent=2),flush=True)
