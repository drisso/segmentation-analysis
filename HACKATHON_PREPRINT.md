# Scalable Spatial Analysis of Single-Cell Segmentation in R

**GitHub Repository:** [https://github.com/davide-risso/segmentation-analysis](https://github.com/davide-risso/segmentation-analysis)

## 1. Introduction and Problem Statement
The field of spatial omics and digital pathology has transitioned from low-plex imaging to gigapixel-scale, whole-slide datasets. While high-plex spatial transcriptomics technologies like Xenium and MERSCOPE are at the forefront, classical **pathology (e.g., H&E)** and **cytology** images remain foundational for clinical and biological research. These datasets often comprise multi-gigabyte WSIs paired with segmentation masks that identify hundreds of thousands to millions of individual nuclei or cell boundaries.

While the Python ecosystem has established powerful frameworks for image processing (e.g., **SpatialData** [10.1038/s41592-024-02212-x]), the R/Bioconductor ecosystem possesses a uniquely mature and sophisticated suite of **geostatistical and geographical analysis tools** (e.g., **terra** [10.32614/CRAN.package.terra], **sf** [10.32614/RJ-2018-009], and **spatstat** [10.18637/jss.v012.i06]). Historically, a major hurdle for R users has been the "Raster-Polygon Bottleneck": the inability to efficiently extract image features from massive rasters and intersect them with millions of polygons without exceeding system memory.

The core problem we address is enabling **scalable image feature extraction** in R. By bridging the gap between cloud-optimized image formats (Zarr) and high-performance spatial databases (GeoParquet), we aim to unlock R’s specialized spatial statistics for the digital pathology community.

## 2. Methodology: The Chunk-Aligned Strategy
We developed a pipeline that prioritizes memory efficiency by never materializing more data than is required for a single processing window. Our solution leverages **GeoParquet** for polygon storage and **OME-Zarr** for image storage.

### 2.1 Technical Stack: Leveraging R's Geographical Excellence
Our implementation capitalizes on the efficiency of modern R geographical packages:
- **terra** [10.32614/CRAN.package.terra]: Originally developed for satellite imagery and global-scale geographical data, `terra` provides the high-performance engine required for lazy raster loading and optimized raster-vector intersections in histology.
- **DuckDB & duckspatial** [10.32614/CRAN.package.duckspatial]: Used for out-of-memory spatial filtering, allowing R to query million-row polygon files as if they were local databases.
- **ZarrArray** [10.18129/B9.bioc.ZarrArray]: Provides the `DelayedArray` backend for native Zarr access within the Bioconductor framework.

### 2.2 Algorithm: Strategy 3
Instead of iterating over polygons (the "vector-first" approach), our algorithm iterates over the **intrinsic Zarr chunks** of the image (the "raster-first" approach). For each chunk $C_{i,j}$:
1.  **Spatial Fetch**: A SQL query is pushed to the Parquet file to retrieve only polygons $P$ where $BBox(P) \cap BBox(C_{i,j}) \neq \emptyset$.
2.  **Lazy Read**: The image data for $C_{i,j}$ is read into memory.
3.  **Incremental Compute**: Pixel statistics (e.g., mean intensity per channel) are computed for each $P$ and stored in an accumulator.

## 3. Results and Benchmarking
Our benchmarks demonstrate that pushing spatial queries to the database layer significantly outperforms traditional GeoJSON-based workflows, enabling the analysis of whole-slide images on standard workstations.

Table 1: Performance comparison of polygon subsetting (500 polygons from 300,000).
| Format | Tool | Retrieval Time (s) | Memory Peak |
| :--- | :--- | :--- | :--- |
| GeoJSON | `sf::st_read` | ~45.0 | High |
| GeoParquet | `duckspatial` | < 1.0 | Low |
| GeoParquet | `arrow` | ~2.5 | Low |

We successfully visualized the intersection of these high-speed queries with high-resolution pathology crops (Figure 1).

![**Figure 1: Overlay of Segmentation Polygons on H&E Image Crop.** This figure demonstrates the successful intersection of a lazily loaded Zarr image and polygons retrieved via a spatial query from GeoParquet. The crop represents a small region of a TCGA H&E whole-slide image. High-resolution version available at `figures/figure1_overlay_high_res.png`.](img/overlay.png)

## 4. Discussion: Downstream Geostatistical Analysis
By providing a scalable bridge for feature extraction, we enable the use of R's superior geostatistical infrastructure for downstream analysis. Once features (e.g., nuclear morphology, mean intensity, texture) are extracted, researchers can immediately apply tools for:
- **Point Pattern Analysis**: Using `spatstat` to model the clustering or dispersion of specific cell types.
- **Spatial Autocorrelation**: Applying Moran’s I or Geary’s C to identify regional patterns of marker expression.
- **Geographically Weighted Regression (GWR)**: Modeling how the relationship between cell types changes across the tissue architecture.

### 4.1 The Border Effect
A primary technical outcome of our work is the characterization of the "Border Effect" (Figure 2). Accurate feature extraction across chunk boundaries is critical for ensuring that downstream geostatistical models are not biased by artificial chunking artifacts.

![**Figure 2: Schematic of the Border Effect and Pixel Accumulation Strategy.** (A) The spatial overlap problem where a polygon (cell) spans across the boundary of two Zarr chunks. (B) The two-step accumulation solution: when Chunk A is processed, partial pixel values for the polygon are stored in a memory buffer. When Chunk B is subsequently read, its corresponding pixels are combined with the buffered data to compute the final global statistic (e.g., mean intensity) without data loss. High-resolution version available at `figures/figure2_border_effect_high_res.png`.](img/border_effect_schematic.png)

## 5. References
- [10.1038/s41592-024-02212-x] Marconato et al., "SpatialData: an open and universal data framework for spatial omics," *Nature Methods*, 2024.
- [10.18637/jss.v012.i06] Baddeley & Turner, "Spatstat: An R Package for Analyzing Point Patterns," *Journal of Statistical Software*, 2005.
- [10.32614/CRAN.package.terra] Hijmans, "terra: Spatial Data Analysis," 2026.
- [10.32614/RJ-2018-009] Pebesma, "Simple Features for R," *The R Journal*, 2018.
- [10.18129/B9.bioc.ZarrArray] Pagès et al., "ZarrArray: Bring Zarr datasets in R as DelayedArray objects," 2026.
