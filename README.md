# CHIRPS Monthly Precipitation Data Workflow

**Climate Hazards Center InfraRed Precipitation with Station data (CHIRPS)**

A comprehensive Python pipeline for downloading, processing, and organizing CHIRPS monthly precipitation data (1981-present) for geospatial analysis.

---

## 📋 Table of Contents

- [About CHIRPS](#about-chirps)
- [Dataset Properties](#dataset-properties)
- [Version Comparison: v2.0 vs v3.0](#version-comparison-v20-vs-v30)
- [Workflow Features](#workflow-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Directory Structure](#directory-structure)
- [Data Access & Updates](#data-access--updates)
- [License & Terms of Use](#license--terms-of-use)
- [Citation](#citation)
- [Applications](#applications)
- [Known Limitations](#known-limitations)
- [Support & Resources](#support--resources)

---

## 🌧️ About CHIRPS

**CHIRPS** (Climate Hazards Center InfraRed Precipitation with Station data) is a high-resolution, quasi-global rainfall dataset developed by the Climate Hazards Center at UC Santa Barbara (UCSB). It combines satellite imagery with in-situ station observations to create gridded precipitation time series designed for:

- Trend analysis
- Drought monitoring
- Climate variability studies
- Hydrological modeling
- Agricultural planning
- Early warning systems

The dataset is developed to support the **USAID Famine Early Warning Systems Network (FEWS NET)** and provides critical precipitation data for food security monitoring worldwide.

---

## 📊 Dataset Properties

### Core Specifications

| Property | CHIRPS v2.0 | CHIRPS v3.0 |
|----------|-------------|-------------|
| **Spatial Coverage** | 50°S to 50°N (land only) | **60°S to 60°N** (land only) ✨ |
| **Spatial Resolution** | 0.05° (~5.5 km at equator) | 0.05° (~5.5 km at equator) |
| **Temporal Coverage** | 1981 to near-present | 1981 to near-present |
| **Temporal Resolution** | Daily, Pentad, Dekad, Monthly | Daily, Pentad, Dekad, Monthly, Annual |
| **Update Frequency** | Monthly (final), Pentad (prelim) | Monthly (final), Pentad (prelim) |
| **Units** | mm/day, mm/pentad, mm/month | mm/day, mm/pentad, mm/month |
| **File Format** | GeoTIFF (.tif.gz) | GeoTIFF (.tif), NetCDF, BIL, COG |
| **Data Sources** | ~24 station sources | **~90 station sources** (4x more!) ✨ |
| **Station Count** | ~10,000-20,000/month | **~20,000-30,000/month** ✨ |
| **Release Date** | 2015 | January 2025 |

### Key Characteristics

- **Quasi-Global Coverage**: Covers all land areas between specified latitudes and all longitudes
- **Blended Product**: Combines satellite thermal infrared (TIR) Cold Cloud Duration (CCD) with rain gauge observations
- **High Resolution Climatology**: Built on CHPclim (v2.0) or CHPclim2 (v3.0)
- **Low Latency**: Preliminary product available ~2 days after pentad end; final product ~3 weeks after month end
- **Quality Controlled**: Extensive R-Checks validation process monthly
- **Long Record**: 40+ years of consistent data (1981-present)

---

## 🔄 Version Comparison: v2.0 vs v3.0

### CHIRPS v3.0 Major Improvements (Released January 2025)

CHIRPS v3.0 represents a significant upgrade with several key enhancements:

#### 1. **Expanded Geographic Coverage** 🌍
- **v2.0**: 50°S to 50°N
- **v3.0**: 60°S to 60°N (10° expansion in both hemispheres)
- Better coverage of southern South America, southern Africa, and higher latitude regions

#### 2. **Dramatically Increased Station Data** 📡
- **v2.0**: ~24 station sources, ~10,000-20,000 stations/month
- **v3.0**: ~90+ station sources (nearly 4x more!), ~20,000-30,000 stations/month
- Includes new sources from:
  - Private weather networks (e.g., ElCompi.net)
  - National meteorological services
  - 3D-Printed Automatic Weather Stations (3D-PAWS)
  - Regional networks across Latin America, Africa, Asia

#### 3. **Improved Precipitation Variance Estimation** 📈
- **v2.0**: CHIRP2 algorithm tended to underestimate temporal precipitation variance
- **v3.0**: CHIRP3 algorithm better captures extreme precipitation events
- More accurate representation of both wet and dry extremes
- Better performance in estimating local precipitation extremes

#### 4. **Enhanced Climatology (CHPclim2)** 🗺️
- **v2.0**: Based on CHPclim (1980-2009 normals)
- **v3.0**: Based on CHPclim2 (1991-2020 normals) with:
  - Integration of IMERG v6 Final inputs
  - Gauge-undercatch correction (Legates-Willmott method)
  - Higher mean rainfall values due to systematic bias correction
  - More accurate precipitation estimates

#### 5. **Gauge-Undercatch Correction** 🔧
- **v3.0** applies Legates-Willmott correction factors to account for:
  - Wind-induced measurement errors
  - Evaporation from gauge
  - Wetting losses
  - Splashing effects
- Results in ~5-15% higher precipitation values in many regions
- More realistic representation of actual precipitation

#### 6. **Superior Station Archive** 📚
- **CHC Archive**: Now the best rapidly-updated precipitation database globally
- **More stations than GPCC**: Climate Hazards Center archive exceeds Global Precipitation Climatology Centre since 2016
- **Quality Control**: Extensive monthly R-Checks validation process
- **Documentation**: Detailed diagnostic tools and station maps available

### When to Use Which Version?

| Use Case | Recommended Version | Reason |
|----------|-------------------|---------|
| **New Projects (2025+)** | v3.0 | Latest improvements, more stations, better extremes |
| **Long-term Continuity** | v2.0 (until 2026) | Existing workflows, published methodologies |
| **Extreme Events** | v3.0 | Better variance estimation, extreme precipitation |
| **High Latitudes (50°-60°)** | v3.0 | Extended coverage not available in v2.0 |
| **Comparison Studies** | Both | Validate improvements, sensitivity analysis |
| **Station-Sparse Regions** | v3.0 | 4x more station sources |

**Note**: CHIRPS v2.0 will continue production through 2026 to support ongoing applications during the transition period.

---

## ✨ Workflow Features

### What This Pipeline Does

1. **Download Management**
   - Automated download of CHIRPS monthly GeoTIFF files
   - Support for both v2.0 (.tif.gz) and v3.0 (.tif) formats
   - Automatic extraction of compressed files
   - Resume capability (skips existing files)
   - Retry logic with exponential backoff
   - Progress tracking

2. **Data Organization**
   - Year-based directory structure
   - Separate folders for raw data, GeoTIFFs, previews, metadata
   - Automatic file naming and organization
   - Download and validation logs

3. **Quality Validation**
   - Automatic GeoTIFF validation using rasterio
   - Statistical summaries (min, max, mean, std dev)
   - Spatial extent verification
   - NoData value checking
   - Metadata extraction

4. **Visualization**
   - Automatic preview image generation
   - Log-scale precipitation maps
   - Publication-quality figures
   - Monthly rainfall visualization

5. **Metadata Generation**
   - Comprehensive metadata files
   - Processing parameters
   - Statistical summaries
   - Data provenance
   - Quality indicators

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Internet connection for data download

### Required Python Packages

```bash
# Core dependencies
pip install rasterio numpy matplotlib

# Optional but recommended
pip install geopandas  # For advanced geospatial analysis
pip install xarray     # For NetCDF handling
```

### Installation Steps

1. **Clone or Download This Repository**
   ```bash
   git clone <https://github.com/Benjamin025/CHIRPS_Rainfall_Pipeline>
   cd chirps-workflow
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation**
   ```python
   python -c "import rasterio; import numpy; import matplotlib; print('✓ All dependencies installed')"
   ```

---

## 🚀 Quick Start

### Option 1: Interactive Menu (Recommended)

```bash
python chirps_complete_workflow_v3.py
```

Follow the interactive prompts to:
1. Select CHIRPS version (2.0 or 3.0)
2. Choose product type (final or preliminary)
3. Download specific year ranges
4. Validate existing files
5. Generate previews and metadata

### Option 2: Quick Test (2 Years)

```bash
python chirps_complete_workflow_v3.py
# Select: 2. Quick start (test with 2023-2024)
```

### Option 3: Direct Python Usage

```python
from chirps_complete_workflow_v3 import CHIRPSCompleteWorkflow

# Initialize workflow for CHIRPS v3.0
workflow = CHIRPSCompleteWorkflow(version="3.0", product_type="final")

# Download specific year range
workflow.download_year_range(start_year=2020, end_year=2024)

# Validate all downloaded files
workflow.validate_all_files(start_year=2020, end_year=2024, create_previews=True)
```

---

## 📖 Usage Examples

### Example 1: Download Complete CHIRPS v3.0 Archive

```python
from chirps_complete_workflow_v3 import CHIRPSCompleteWorkflow

# Create workflow instance
workflow = CHIRPSCompleteWorkflow(version="3.0", product_type="final")

# Download entire archive (1981-2025)
# WARNING: This will download ~20 GB of data
workflow.run_complete_workflow(start_year=1981, end_year=2025)
```

### Example 2: Download Recent Years Only

```python
# Download last 5 years of data
workflow = CHIRPSCompleteWorkflow(version="3.0", product_type="final")
workflow.download_year_range(start_year=2020, end_year=2025)
```

### Example 3: Download CHIRPS v2.0 for Comparison

```python
# Download v2.0 for comparison studies
workflow_v2 = CHIRPSCompleteWorkflow(version="2.0")
workflow_v2.download_year_range(start_year=2020, end_year=2024)
```

### Example 4: Validate Existing Downloads

```python
# Validate files without downloading
workflow = CHIRPSCompleteWorkflow(version="3.0")
workflow.validate_all_files(
    start_year=2020,
    end_year=2024,
    create_previews=True  # Generate preview images
)
```

### Example 5: Access Specific Months

```python
# Download specific months
workflow = CHIRPSCompleteWorkflow(version="3.0")

# Download January 2024
workflow.download_single_file(year=2024, month=1)

# Download all months of 2024
for month in range(1, 13):
    workflow.download_single_file(year=2024, month=month)
```

### Example 6: Custom Base Directory

```python
# Use custom directory structure
workflow = CHIRPSCompleteWorkflow(
    base_dir="/path/to/my/data/CHIRPS",
    version="3.0",
    product_type="final"
)
workflow.download_year_range(2023, 2024)
```

### File Naming Convention

- **v2.0**: `chirps-v2.0.YYYY.MM.tif.gz` (compressed)
- **v3.0**: `chirps-v3.0.YYYY.MM.tif` (direct GeoTIFF)
- **Metadata**: `CHIRPS_YYYY_MM_metadata.txt`
- **Preview**: `CHIRPS_YYYY_MM_preview.png`

---

## 🌐 Data Access & Updates

### Download Sources

- **Primary Server**: https://data.chc.ucsb.edu/products/CHIRPS/
  - **v2.0**: `CHIRPS-2.0/global_monthly/tifs/`
  - **v3.0**: `v3.0/monthly/global/tifs/`

### Update Schedule

| Product Type | Latency | Availability | Station Sources |
|--------------|---------|--------------|-----------------|
| **Preliminary** | ~2 days after pentad | 2nd, 7th, 12th, 17th, 22nd, 27th of month | GTS rapid stations only |
| **Final** | ~3 weeks after month end | Monthly, typically 3rd week | All available sources (~90+) |

### Data Formats Available

- **GeoTIFF** (.tif) - Recommended for GIS
- **NetCDF** (.nc) - For climate modeling
- **BIL** (.bil) - Legacy format
- **COG** (Cloud-Optimized GeoTIFF) - For cloud platforms

### Alternative Access Methods

1. **Google Earth Engine**
   - Dataset: `UCSB-CHG/CHIRPS/DAILY`, `UCSB-CHG/CHIRPS/PENTAD`, `UCSB-CHG/CHIRPS/V3/MONTHLY`
   - Free API access for research

2. **AWS Open Data Registry**
   - Digital Earth Africa: `s3://deafrica-input-datasets/rainfall_chirps_monthly/`

3. **Early Warning Explorer (EWX)**
   - Web interface: https://earlywarning.usgs.gov/fews/ewx/
   - Visualization and analysis tools

---

## 📜 License & Terms of Use

### Public Domain Dedication

CHIRPS is in the **public domain**. To the extent possible under law, **Pete Peterson** and the **Climate Hazards Center** have waived all copyright and related or neighboring rights to CHIRPS.

### Creative Commons (v3.0)

CHIRPS v3.0 is registered with **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

### Terms of Use

```
This dataset is provided "as is" without warranty of any kind, either 
expressed or implied. The entire risk as to the quality and performance 
of the dataset is with the user.

The Climate Hazards Center and UC Santa Barbara make no representations 
or warranties regarding the accuracy, completeness, or reliability of 
this dataset.
```

### Usage Requirements

✅ **You MAY**:
- Use for commercial purposes
- Use for research and education
- Modify and redistribute
- Use without attribution (though citation is appreciated)

❌ **You SHOULD**:
- Cite the dataset (see Citation section)
- Acknowledge CHC/UCSB in publications
- Report issues or improvements to the CHC team

---

## 📚 Citation

### How to Cite CHIRPS

When using CHIRPS data in publications, please cite the appropriate papers:

#### CHIRPS v2.0 Primary Citation

```
Funk, C., Peterson, P., Landsfeld, M., Pedreros, D., Verdin, J., Shukla, S., 
Husak, G., Rowland, J., Harrison, L., Hoell, A., and Michaelsen, J. (2015). 
The climate hazards infrared precipitation with stations—a new environmental 
record for monitoring extremes. Scientific Data, 2, 150066. 
https://doi.org/10.1038/sdata.2015.66
```

#### CHIRPS v2.0 USGS Citation

```
Funk, C.C., Peterson, P.J., Landsfeld, M.F., Pedreros, D.H., Verdin, J.P., 
Rowland, J.D., Romero, B.E., Husak, G.J., Michaelsen, J.C., and Verdin, A.P. (2014). 
A quasi-global precipitation time series for drought monitoring: 
U.S. Geological Survey Data Series 832, 4 p.
http://dx.doi.org/10.3133/ds832
```

#### CHIRPS v3.0 Citation

```
Climate Hazards Center (2025). Climate Hazards Center Infrared Precipitation 
with Stations version 3 (CHIRPS v3). CHIRPS3 Data Repository. 
https://doi.org/10.15780/G2JQ0P
```

### BibTeX Format

```bibtex
@article{funk2015chirps,
  title={The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes},
  author={Funk, Chris and Peterson, Pete and Landsfeld, Martin and Pedreros, Diego and Verdin, James and Shukla, Shraddhanand and Husak, Gregory and Rowland, James and Harrison, Laura and Hoell, Andrew and others},
  journal={Scientific Data},
  volume={2},
  number={1},
  pages={1--21},
  year={2015},
  publisher={Nature Publishing Group},
  doi={10.1038/sdata.2015.66}
}

@misc{chirps_v3_2025,
  title={Climate Hazards Center Infrared Precipitation with Stations version 3},
  author={{Climate Hazards Center}},
  year={2025},
  publisher={University of California, Santa Barbara},
  doi={10.15780/G2JQ0P},
  url={https://data.chc.ucsb.edu/products/CHIRPS/v3.0/}
}
```

### Acknowledgment Text

```
This study/analysis/research used CHIRPS version [2.0/3.0] precipitation data, 
developed by the Climate Hazards Center at UC Santa Barbara and provided 
through the Climate Hazards Center data portal (https://www.chc.ucsb.edu/data/).
```

---

## 🎯 Applications

CHIRPS data is widely used across multiple domains:

### 1. **Drought Monitoring & Early Warning**
   - FEWS NET operational drought monitoring
   - Agricultural drought assessment
   - Hydrological drought indicators
   - Real-time food security alerts

### 2. **Climate Research**
   - Long-term precipitation trends
   - Climate variability studies
   - ENSO impact analysis
   - Regional climate change assessment

### 3. **Hydrological Modeling**
   - Rainfall-runoff modeling
   - Flood forecasting
   - Water resource management
   - Catchment hydrology studies

### 4. **Agricultural Applications**
   - Crop yield forecasting
   - Irrigation planning
   - Growing season analysis
   - Agricultural risk assessment

### 5. **Health & Disease Monitoring**
   - Malaria risk mapping (rainfall-driven)
   - Vector-borne disease prediction
   - Cholera outbreak monitoring
   - Climate-health relationships

### 6. **Land Surface Modeling**
   - Input for LSM (VIC, NOAH, CLM)
   - Soil moisture estimation
   - Evapotranspiration studies
   - Energy balance calculations

### 7. **Remote Sensing Validation**
   - Satellite precipitation validation
   - GPM/IMERG comparison
   - Algorithm development
   - Sensor calibration

---

## ⚠️ Known Limitations

### Geographic Limitations

1. **No Ocean Coverage**
   - Land-only dataset
   - Not suitable for oceanic precipitation studies

2. **Limited Polar Coverage**
   - v2.0: 50°S to 50°N only
   - v3.0: 60°S to 60°N (still excludes polar regions)
   - Not suitable for high-latitude studies (>60°)

3. **Complex Terrain Challenges**
   - Orographic effects may be underestimated
   - Mountain precipitation can be uncertain
   - Rain shadow effects may not be fully captured

### Temporal Limitations

4. **Preliminary Product Accuracy**
   - Uses fewer station sources (GTS only)
   - May differ from final product by 5-20%
   - Should be used cautiously for critical decisions

5. **Near Real-Time Lag**
   - Final product: ~3 weeks latency
   - Not suitable for same-day disaster response
   - Use CHIRPS Prelim for near-real-time needs

### Data Quality Limitations

6. **Station-Sparse Regions**
   - Lower accuracy in data-sparse areas (e.g., Sahara, Amazon interior)
   - More uncertainty in remote regions
   - Station density varies greatly by region

7. **Snowfall Representation**
   - Designed primarily for rainfall
   - Snow may be underestimated (gauge-undercatch even with correction)
   - Cold season precipitation less reliable

8. **Gauge Biases**
   - Even with correction, systematic biases remain
   - Wind-induced errors in high-wind areas
   - Wetting loss varies by gauge type

### Technical Limitations

9. **File Sizes**
   - Global monthly files: ~30-50 MB each
   - Full archive (1981-2025): ~20-25 GB
   - May require significant storage

10. **Processing Requirements**
    - High-resolution analysis computationally intensive
    - Requires GIS software or programming skills
    - Memory requirements for large spatial domains

### Version-Specific Limitations

11. **v3.0 Transition Period**
    - v3.0 released January 2025 (very new!)
    - Limited peer-reviewed validation studies
    - May have undiscovered issues

12. **v2.0/v3.0 Inconsistencies**
    - Values differ due to gauge-undercatch correction
    - Not directly interchangeable in time series
    - Requires careful consideration in long-term studies

---

## 🔧 Support & Resources

### Official Documentation

- **Main Website**: https://www.chc.ucsb.edu/data/chirps3
- **Data Portal**: https://data.chc.ucsb.edu/products/CHIRPS/
- **README**: https://data.chc.ucsb.edu/products/CHIRPS/v3.0/README-CHIRPSv3.0.txt
- **Diagnostics**: https://www.chc.ucsb.edu/data/chirps3/diagnostics

### Interactive Tools

- **Early Warning Explorer (EWX)**
  - USGS: https://earlywarning.usgs.gov/fews/ewx/
  - CHC: https://ewx3.chc.ucsb.edu/ewx/
  - Web-based visualization and analysis

### Google Earth Engine

```javascript
// CHIRPS v3.0 Monthly in GEE
var chirps_v3 = ee.ImageCollection('UCSB-CHC/CHIRPS/V3/MONTHLY');
var precipitation = chirps_v3
    .filter(ee.Filter.date('2024-01-01', '2024-12-31'))
    .select('precipitation');
```

### Community & Support

- **CHC Wiki**: https://wiki.chc.ucsb.edu/
- **Reality Checks**: https://wiki.chc.ucsb.edu/CHIRPS_Reality_Checks
- **Contact**: Climate Hazards Center (chc@ucsb.edu)

### Related Datasets

- **CHIRTS**: Temperature data companion to CHIRPS
- **CHIMES**: IMERG-based rapid update product
- **CHPclim**: Precipitation climatology
- **EDDI**: Evaporative Demand Drought Index

### Scientific Publications

Key papers for understanding CHIRPS methodology:

1. Funk et al. (2015) - Primary CHIRPS v2.0 paper
2. Funk et al. (2019) - CHIRTS temperature
3. Davenport et al. (2024) - CHIRPS applications
4. Peterson et al. (2023) - CHIMES and CHIRPS v3

### Comparison with Other Products

| Dataset | Resolution | Coverage | Period | Latency | Best For |
|---------|-----------|----------|--------|---------|----------|
| **CHIRPS** | 0.05° | Land 60°S-60°N | 1981-present | ~3 weeks | Drought monitoring, long records |
| **GPM IMERG** | 0.1° | Global 60°S-60°N | 2000-present | ~4 months | Global coverage, oceanic |
| **GPCC** | 0.25°-2.5° | Global land | 1891-present | ~2 months | Long-term climate, station-only |
| **PERSIANN-CDR** | 0.25° | Global 60°S-60°N | 1983-present | ~1 month | Climate studies, neural network |
| **TAMSAT** | 0.0375° | Africa only | 1983-present | ~2 days | African focus, dekadal |

---

## 🙏 Acknowledgments

CHIRPS is developed and maintained by the **Climate Hazards Center** at the **University of California, Santa Barbara** with support from:

- USAID Famine Early Warning Systems Network (FEWS NET)
- U.S. Geological Survey (USGS)
- National Aeronautics and Space Administration (NASA)
- National Oceanic and Atmospheric Administration (NOAA)

Station data contributions from **90+ sources** including:
- National meteorological services worldwide
- Global Telecommunications System (GTS)
- Global Historical Climatology Network (GHCN)
- Regional networks (SASSCAL, TAHMO, etc.)
- Private weather networks (e.g., ElCompi.net)

---

## 📝 Version History

### Workflow Script Versions

- **v1.0.0** (2025-02-12): Initial release
  - Support for CHIRPS v2.0 and v3.0
  - Automated download and validation
  - Preview generation
  - Metadata creation

### CHIRPS Dataset Versions

- **CHIRPS v3.0** (January 2025)
  - Expanded coverage: 60°S-60°N
  - 4x more station sources
  - Improved variance estimation
  - Gauge-undercatch correction

- **CHIRPS v2.0** (2015-2026)
  - Coverage: 50°S-50°N
  - ~24 station sources
  - Production continues through 2026

---

## 📧 Contact & Contribution

### Issues & Bug Reports

If you encounter issues with this workflow:
1. Check existing issues on GitHub
2. Create new issue with detailed description
3. Include error messages and system info

### Feature Requests

Suggestions for improvements are welcome! Please submit via GitHub issues.

### Contributing

Contributions are encouraged:
1. Fork the repository
2. Create feature branch
3. Submit pull request with description

### Citing This Workflow

If you use this workflow in your research:

```
[Karanja Benjamin Ndung'u] (2025). CHIRPS Monthly Precipitation Workflow. 
GitHub repository: [https://github.com/Benjamin025/CHIRPS_Rainfall_Pipeline]
```

---

## 📄 License

This workflow code is released under the **MIT License**.

CHIRPS data itself is in the **public domain** with **CC BY 4.0** (v3.0).

---

**Last Updated**: February 12, 2025  
**CHIRPS Version**: v3.0  
**Workflow Version**: 1.0.0

---

*For the latest information about CHIRPS, always refer to the official Climate Hazards Center website: https://www.chc.ucsb.edu/data/chirps3*