# P3.3: second package cache (TSA08)

Task: #20
Status: complete
Release: https://github.com/UBC-FRESH/fresh-cbm/releases/tag/v0.1.0-tsa08

## Build

- dataset: `tsa08-p120-matrix-full`
- package: `tsa08-p120-matrix-package`
- family: untreated + one `CC` event at offsets 0–49
- 3,761 actual track/age states
- 50 years, 26 carbon accounts, float64
- 64 workers

## Results

- build: **7,551.7 s (2h05)**
- size: **2.03 GB**, 53 release assets
- validation: **102 state/offset rows, max absolute error 0**
- package fingerprint: `fdf9bc7df1f5381c29b0b22484204ea94ab8cdfac7242b6a78993693d16ed5ee`
- CBM defaults: `4bd722d8825abeda3c9cf77247bbd4903824259e2fcc046d9a335336c8842155`
- libcbm: 2.10.2

## Verification

- `fresh-cbm-validate`: 0 error
- `fresh-cbm-package`: 53 files, 2.03 GB
- release assets uploaded and public

## Notes

This proves the format and builder are not TSA41-specific. The cache is a
package artifact, not a policy result.
