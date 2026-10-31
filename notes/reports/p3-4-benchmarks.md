# P3.4: cache scale and consumer projection benchmarks

Task: #22
Status: complete

## Published caches

| Cache | States | Accounts | Offsets | Size | Build |
| --- | ---: | ---: | ---: | ---: | ---: |
| TSA41 | 5,273 | 26 | 50 | 2.85 GB | 10,991 s |
| TSA08 | 3,761 | 26 | 50 | 2.03 GB | 7,552 s |

## Consumer projection

`fresh-cbm-bench` with `carbon.system.total` at year 49, all blocks, 100 random
lookups:

| Cache | Blocks | Load | Median lookup | Projection |
| --- | ---: | ---: | ---: | ---: |
| TSA41 | 148,828 | 0.018 s | 0.85 ms | 2.33 s |
| TSA08 | 371,565 | 0.032 s | 1.18 ms | 4.96 s |

Raw records:

- `notes/reports/benchmark-tsa41.json`
- `notes/reports/benchmark-tsa08.json`

## Interpretation

The cache is effective when build cost is amortized. The projection time scales
with the number of fragments/blocks, while state lookup remains sub-millisecond.
Exact WS4 replay is not included in this benchmark.
