from pathlib import Path
p=Path('generated/research_sprint_review_20261008/traits_audit');s=(p/'probe_endpoints.py').read_text()
a=s.index('specs=[');b=s.index('def projection',a)
s=s[:a]+"specs=load(OUT/'batch_frozen_endpoint_specs.json')\n"+s[b:]
s=s.replace("(OUT/'additional_endpoint_probes.json')","(OUT/'batch_endpoint_probes.json')").replace("(OUT/'additional_endpoint_candidates.npz'","(OUT/'batch_endpoint_candidates.npz'")
s=s.replace("result.append(a);print", "result.append(a);print")
# Require consistency with measured supporting stereo, rather than a single nearest projected cloud point.
s=s.replace("chosen=int(near[np.argmin(d[near])]);ep.append", """original_near=near.copy()
  checks=[]
  for fr in [a['frame']]+a['secondary']:
   pu,pcand=projection(p[near],fr);uvideal=pcand[:,:2]/pcand[:,2,None]*[K[0,0],K[1,1]]+[K[0,2],K[1,2]];ijc=np.rint(uvideal).astype(int);ok=(ijc[:,0]>=0)&(ijc[:,0]<1280)&(ijc[:,1]>=0)&(ijc[:,1]<720);support=np.zeros(len(near),bool)
   with np.load(D/f'rgb/depth_{fr}.npz') as de:
    iok=np.flatnonzero(ok);zs=de['depth'][ijc[iok,1],ijc[iok,0]]*SCALE;vs=de['votes'][ijc[iok,1],ijc[iok,0]];support[iok]=np.isfinite(zs)&(zs>0)&(vs>=2)&(np.abs(zs-pcand[iok,2])<=.012)
   checks.append(support)
  support_counts=np.sum(checks,axis=0);near=near[support_counts>=2];arrays[key]=near
  if not len(near):ep.append(dict(role=a['roles'][i],source_pixel_xy=click,candidate_count=0,projected_candidates_before_two_view_depth_check=len(original_near),rejection='No candidate consistent with stereo depth in at least two of three inspected views.'));continue
  chosen=int(near[np.argmin(d[near])]);ep.append""")
(p/'batch_endpoints.py').write_text(s)
