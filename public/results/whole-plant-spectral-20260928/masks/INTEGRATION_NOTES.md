# How to present the full-scene spectral result

The meaningful advance is **access to every recorded image location**, not a claim of complete three-dimensional fusion or a calibrated physiological map. The full spectral images let the audience recognise the recorded plants, their leaves, pots and reference board. Clicking a location retrieves that exact camera pixel's 224 recorded values. The coloured wavelength image is only a display; numerical spectra are exported losslessly and do not come from reading colours back out of a JPEG or PNG.

The scan has two spatial image directions and one wavelength direction. Rotated presentation coordinates are x = native scan line and y = detector width minus 1 minus native detector column. R1–R5 are useful broad browsing windows. They are not precise leaf masks or an operator-certified identity assignment; leaning foliage can cross a boundary, and plant surfaces hidden from the cameras were not recorded.

## Optional tissue highlighting

Keep the full image as the default. The optional colour overlay estimates visible tissue using spectral appearance learned from the earlier selected patches and explicit background examples. Its colours identify scan regions; yellow means ambiguous appearance. It misses much of R1's dry narrow foliage, and it can include background or shadows incorrectly. A pixel remains inspectable with the mask disabled. The 371,859 FX10 and 202,687 FX17 candidate pixels are broader selections, not a count of leaves or verified physical plant coverage.

Candidate-region mean curves are **raw detector-signal averages over an appearance-selected set**, not calibrated whole-plant reflectance. Curves depend on tissue selection, exposure, illumination, viewing angle and sensor response. They must not be used to rank plant health or compare absolute detector values across FX10 and FX17. The mean that excludes suspected clipping also changes which pixels contribute from one band to the next; show counts and identify that choice explicitly.

## Quality findings to show rather than hide

Using the established suspected-clipping screen DN >= 65520, approximately 29.7%, 48.1%, 28.7%, 36.9% and 37.6% of FX10 candidate pixels in R1–R5 have at least one affected band. FX17 corresponding fractions are about 1.4%, 17.8%, 5.8%, 9.0% and 1.5%. These are conditional on the optional mask, not percentages of whole physical plants. Clipping is wavelength-specific; it does not make every band of such a pixel useless, but affected values cannot be recovered from these recordings.

In R5, about 26.2% of FX10 and 27.7% of FX17 candidate pixels are outside the reviewed white-reference detector columns. Their raw readings are still inspectable. Reference-relative values must not be silently extrapolated there. The dark-tail assumption and unknown white-panel reflectance remain distinct radiometric limitations, even where spatial identity is visually obvious.

## Suggested explanation

“We now show the complete recorded spectral scenes rather than isolated exported patches. We can browse every recorded location in either camera and inspect its full spectrum. RGB photographs help recognise the plant and approximate region, while exact spectral-to-RGB links are shown only where supported. Optional tissue highlighting summarises candidate visible foliage, with clipping and reference gaps reported separately. This is full-scene spectral inspection and exploratory tissue analysis; calibrated whole-plant physiological results and complete 3D spectral correspondence are still separate goals.”

## Verification boundary

`verification.json` and `quality_audit.json` establish label storage, source-window containment, arithmetic and legitimate count/range handling. `export_integration_verification.json` passed an independent audit of 10 complete lines per camera (3,727,360 exact DN values), 1,800 sampled source-to-display positions, whole-image JPEG orientation, 600 native-mask coordinates, and all copied reference arrays and flags. The six audited band JPEGs differ from uncompressed display intensities by a mean 0.62–2.88 levels on the 0–255 scale; they are explicitly previews rather than a source for numerical measurements. None of these is anatomical segmentation ground truth or independent physical calibration.
