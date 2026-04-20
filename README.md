# segmentation-analysis

## Day 1

### Microbenchmark of segmentation file formats in R 

- Starting from one segmentation mask in three different file formats (json/geojson, h5ad, parquet)
- Measure time and memory usage of a simple task: read the file, subset to a small region, and plot

Prelminary steps:

- Create parquet file from geojson using duckdb
- Explore existing approaches:
    - https://github.com/waldronlab/HistoImagePlot
    - https://cran.r-project.org/web/packages/geojsonsf/index.html


