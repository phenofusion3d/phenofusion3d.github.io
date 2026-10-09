# Combined cached-pair probe: conditional decision

**Preserving useful old pair evidence is justified; replacing it wholesale with the nearest six pairs is not.** The generated v2 candidate preserves every old image-domain accepted depth exactly and adds only conservative hole candidates. It is ready for a controlled comparison, not a claim that thin P1/P4 geometry or the whole reconstruction is solved.

No stereo matching was rerun. Each old and short stack has six pairs, but four target frames are shared: the union contains **eight distinct pairs**, not twelve independent votes. Shared pair maps were verified equal, including missing values. All original cache and application files remain unchanged.

## Rule and checks

Old accepted depths retain the original two-pair agreement gate and their exact values. Previously empty pixels may be added only with at least three distinct pairs in a depth window no wider than the existing 10 mm tolerance and no competing two-pair mode more than 10 mm away. No spatial growth, smoothing, near-depth preference, sensor filling, range change or annotation-based tuning is used. Existing conflicting legacy hypotheses are explicitly flagged; preserving them does not make them correct.

The first prototype had a peer-identified tie-mode bug: it measured competitors from the midpoint of tied modes instead of the selected mode. Version 2 fixes that. The 0.200×3 versus 0.216×3 adversarial case and three controls pass; v1 is retained and labelled superseded. `integrity_checks.json` confirms unique pair IDs, exact legacy values, stricter new-fill evidence, pair-bit counts and safe missing values for every probe.

| Anchor | Old image-domain candidates | New conservative hole candidates | Combined candidates |
| --- | ---: | ---: | ---: |
| 275384 | 135,599 | 10,748 | 146,347 |
| 487431 | 151,633 | 13,255 | 164,888 |
| 799028 | 157,651 | 12,991 | 170,642 |
| 1055904 | 133,408 | 29,219 | 162,627 |
| 1420709 | 161,872 | 9,163 | 171,035 |

These are whole-image pixel counts, including background. They are not biological coverage or accuracy scores.

## Why the P4 bud was lost

At the isolated hanging bud in anchor 1055904, native/undistorted pixel (637,342), the old pairs include depths 0.1943758 m from target 1107591 and 0.1938676 m from target **1160788**. The latter target is dropped by the short-pair selection. Its nearer replacements, 1030829 and 1081749, both have missing depth at this pixel. Target 1003470 instead supplies a discrepant 0.2268590 m observation.

The old centre, retained unchanged in v2, is **0.1941217 m**. The independently selected RGB landmark gives a conditional 0.1941786 m reference, with a pixel-only 95% interval of 0.1891149–0.1994144 m. This supports retaining the older pair evidence here; it does not validate all old depths. Requiring three pairs everywhere would erase this useful two-pair observation, which is why stricter support applies only to new hole fills.

The frozen P1 dry-strip sample gains just **five** pixels: 168 to 173 of 242 sampled pixels. Their depths range approximately 0.611–0.705 m, with median 0.6994 m. This is closer to the camera than the neighboring board sample (about 0.873 m), but farther than the old strip-candidate median (about 0.614 m). No unambiguous independent depth landmark exists on that strip, so these additions do not establish recovery of the missing thin structure.

The independent fixed-mask comparison in `../../../stage_audit/combined_probe_comparison.json` and `.md` passed 37 integrity checks. The P4 bud retains its centre and all 28 of 28 local candidates within the conditional depth interval (the short-only probe had 9 of 18). Other sampled candidate coverage changes include P1 ear 552→632/704, P2 upper stem 189→220/239, P4 arch 116→149/275 and P4 upright stalk 81→120/156. P3 stem receives no additions, avoiding the short-only far-depth tail; the P1 green attachment remains at zero. These are local candidate-coverage comparisons, not proof of complete structures or metric accuracy.

## Near-depth bound

The existing 0.15 m near bound cannot explain the accepted P4 landmark losses: the bud and two flower junctions have conditional central depths 0.1942, 0.2058 and 0.2524 m; their pixel-only lower 95% bounds are about 0.1891, 0.2002 and 0.2438 m. The marked bud failure is directly explained by pair replacement despite being inside the processing range.

This does not rule out range-related losses elsewhere. The cached stereo stacks were already clipped to 0.15–1.00 m, so missing values alone cannot reveal whether an unseen surface was too near, mismatched or occluded. No depth is inferred from manual plant height, and no range expansion is justified by these checks.

## Before any scene fusion

Use the explicitly saved `fusion_depth` and `fusion_votes` arrays with `mask` if this candidate is evaluated in fusion. Outside accepted pixels these are NaN and zero. A false mask alone is insufficient: the existing fusion code can still use finite two-vote depth for free-space contradictions or TSDF integration near a dilated mask. Legacy status 3/4 hypotheses are deliberately retained and flagged; excluding any of them later requires clearing their depth/votes as well.

Keep one coherent depth map per anchor and retain independent multi-anchor visibility/conflict checks. Pair support shares one source image and is not equivalent to independent surface support. A complete combined scene has not been fused or validated by this probe. The practical outcome is preservation of the corroborated P4 bud observation and carefully bounded extra candidates, with **P1 thin-structure recovery still unresolved**.
