"""
CHIRPS COMPLETE WORKFLOW: DOWNLOAD + PROCESSING PIPELINE
Downloads CHIRPS monthly data (1981-2025) and organizes GeoTIFFs

CHIRPS = Climate Hazards Group InfraRed Precipitation with Station data
- Resolution: 0.05° (~5.5 km)
- Coverage: 50°S to 50°N (global land)
- Period: 1981 to near-present
- Units: mm/month (ALREADY IN FINAL UNITS - no conversion needed!)
- Format: GeoTIFF (gzipped)
"""

import os
import urllib.request
import urllib.error
import gzip
import shutil
import time
from pathlib import Path
from datetime import datetime as dt
import traceback
import warnings
warnings.filterwarnings('ignore')

# Try to import processing dependencies
try:
    import rasterio
    from rasterio.crs import CRS
    from rasterio.transform import from_origin
    import numpy as np
    HAS_RASTERIO = True
except ImportError:
    print("⚠️ rasterio not installed. Install with: pip install rasterio")
    HAS_RASTERIO = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as colors
    from matplotlib import cm
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class CHIRPSCompleteWorkflow:
    """Complete CHIRPS workflow: download, organize, validate"""
    
    def __init__(self, base_dir=None, version="2.0"):
        """
        Initialize CHIRPS workflow
        
        Parameters:
        -----------
        base_dir : str or Path
            Base directory for all CHIRPS data
        version : str
            CHIRPS version: "2.0" or "3.0" (default: "2.0")
        """
        
        # Configuration
        self.version = version
        
        if version == "2.0":
            self.BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs"
        elif version == "3.0":
            # CHIRPS v3 structure (available from January 2025)
            self.BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS/v3.0/monthly/global/tifs"
        else:
            raise ValueError(f"Unknown version: {version}. Use '2.0' or '3.0'")
        
        # Base directory structure
        if base_dir is None:
            self.base_dir = Path.home() / "Documents" / "Benjamin" / "CHIRPS" / f"CHIRPS_v{version}"
        else:
            self.base_dir = Path(base_dir)
        
        # Create directory structure
        self.dirs = {
            'raw_gz': self.base_dir / "raw_gz",        # Original .gz files
            'geotiffs': self.base_dir / "geotiffs",    # Extracted .tif files
            'previews': self.base_dir / "previews",    # Preview images
            'metadata': self.base_dir / "metadata",    # Metadata files
            'logs': self.base_dir / "logs"             # Download/process logs
        }
        
        for name, path in self.dirs.items():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {name}/")
        
        print(f"\n🌧️ CHIRPS v{version} COMPLETE WORKFLOW")
        print(f"📁 Base directory: {self.base_dir}")
        print(f"🌍 Coverage: 50°S to 50°N (global land)")
        print(f"📏 Resolution: 0.05° (~5.5 km)")
        print(f"📊 Units: mm/month (no conversion needed)")
        print("="*70)
    
    # =========================================================================
    # FILE NAMING AND URL METHODS
    # =========================================================================
    
    def build_filename(self, year, month):
        """
        Build CHIRPS filename based on version
        
        CHIRPS v2.0: chirps-v2.0.YYYY.MM.tif.gz
        CHIRPS v3.0: chirps-v3.0.YYYY.MM.tif.gz (or similar)
        """
        if self.version == "2.0":
            return f"chirps-v2.0.{year}.{month:02d}.tif.gz"
        elif self.version == "3.0":
            # Adjust based on actual v3.0 naming convention
            return f"chirps-v3.0.{year}.{month:02d}.tif.gz"
    
    def get_file_url(self, year, month):
        """Get download URL for a specific month"""
        filename = self.build_filename(year, month)
        url = f"{self.BASE_URL}/{filename}"
        return url, filename
    
    # =========================================================================
    # DOWNLOAD METHODS
    # =========================================================================
    
    def download_single_file(self, year, month, max_retries=3):
        """
        Download a single monthly CHIRPS file
        
        Returns:
        --------
        tuple: (gz_path, tif_path) or (None, None) if failed
        """
        
        # Create year-specific subfolder
        year_raw_dir = self.dirs['raw_gz'] / str(year)
        year_raw_dir.mkdir(exist_ok=True)
        
        year_tif_dir = self.dirs['geotiffs'] / str(year)
        year_tif_dir.mkdir(exist_ok=True)
        
        # Get URL and filename
        url, filename = self.get_file_url(year, month)
        
        gz_path = year_raw_dir / filename
        tif_filename = filename.replace('.gz', '')
        tif_path = year_tif_dir / tif_filename
        
        # Check if already extracted
        if tif_path.exists():
            size_mb = tif_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ Already exists: {tif_filename} ({size_mb:.1f} MB)")
            return gz_path, tif_path
        
        # Check if .gz exists but not extracted
        if gz_path.exists() and not tif_path.exists():
            print(f"  📦 Extracting existing .gz file...")
            success = self._extract_gz_file(gz_path, tif_path)
            if success:
                return gz_path, tif_path
        
        # Download with retries
        for attempt in range(max_retries):
            try:
                print(f"  Downloading... (attempt {attempt + 1}/{max_retries})")
                
                if attempt > 0:
                    wait_time = 2 ** attempt
                    print(f"  Waiting {wait_time}s...")
                    time.sleep(wait_time)
                
                # Download with progress
                def progress_callback(count, block_size, total_size):
                    if total_size > 0:
                        percent = min(100, int(count * block_size * 100 / total_size))
                        mb_downloaded = count * block_size / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        if mb_total > 0:
                            print(f"  Progress: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='\r')
                
                temp_path = gz_path.with_suffix('.downloading')
                urllib.request.urlretrieve(url, temp_path, reporthook=progress_callback)
                
                # Rename to final
                temp_path.rename(gz_path)
                
                if gz_path.exists():
                    size_mb = gz_path.stat().st_size / (1024 * 1024)
                    print(f"\n  ✅ Downloaded: {size_mb:.1f} MB")
                    
                    # Extract the .gz file
                    print(f"  📦 Extracting...")
                    success = self._extract_gz_file(gz_path, tif_path)
                    
                    if success:
                        return gz_path, tif_path
                    else:
                        print(f"  ❌ Extraction failed")
                        return None, None
                    
            except urllib.error.HTTPError as e:
                print(f"\n  ❌ HTTP Error {e.code}")
                if e.code == 404:
                    print(f"  File not found: {url}")
                    break
            except Exception as e:
                print(f"\n  ❌ Error: {e}")
        
        print(f"  ❌ Failed after {max_retries} attempts")
        return None, None
    
    def _extract_gz_file(self, gz_path, tif_path):
        """Extract a .gz file to .tif"""
        try:
            with gzip.open(gz_path, 'rb') as f_in:
                with open(tif_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            if tif_path.exists():
                size_mb = tif_path.stat().st_size / (1024 * 1024)
                print(f"  ✅ Extracted: {tif_path.name} ({size_mb:.1f} MB)")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"  ❌ Extraction error: {e}")
            return False
    
    def download_year_range(self, start_year=1981, end_year=2027):
        """
        Download all files for a range of years
        
        Parameters:
        -----------
        start_year : int
            Starting year (default: 1981 for CHIRPS v2.0)
        end_year : int
            Ending year (default: 2027)
        """
        
        print(f"\n📥 DOWNLOADING: {start_year} to {end_year}")
        print("="*70)
        
        downloaded_files = []
        failed_months = []
        
        for year in range(start_year, end_year + 1):
            print(f"\n📅 Year {year}:")
            
            # Determine months for this year
            if year == end_year:
                # Get current month for the end year
                end_month = min(12, dt.now().month)
            else:
                end_month = 12
            
            for month in range(1, end_month + 1):
                print(f"\n  Month {month:02d}:")
                
                gz_path, tif_path = self.download_single_file(year, month)
                
                if tif_path and tif_path.exists():
                    downloaded_files.append((year, month, gz_path, tif_path))
                else:
                    failed_months.append((year, month))
                
                # Small delay between downloads
                time.sleep(0.5)
        
        # Summary
        print(f"\n" + "="*70)
        print("📊 DOWNLOAD SUMMARY")
        print("="*70)
        print(f"Successfully downloaded: {len(downloaded_files)} files")
        print(f"Failed: {len(failed_months)} files")
        
        if failed_months:
            print("\nFailed months:")
            for year, month in failed_months[:20]:  # Show first 20
                print(f"  {year}-{month:02d}")
            if len(failed_months) > 20:
                print(f"  ... and {len(failed_months) - 20} more")
        
        # Create download log
        self._create_download_log(downloaded_files, failed_months)
        
        return downloaded_files
    
    def _create_download_log(self, downloaded_files, failed_months):
        """Create a log of downloaded files"""
        log_file = self.dirs['logs'] / f"download_log_{dt.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(log_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write(f"CHIRPS v{self.version} DOWNLOAD LOG\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Download date: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total downloaded: {len(downloaded_files)}\n")
            f.write(f"Total failed: {len(failed_months)}\n\n")
            
            f.write("DOWNLOADED FILES:\n")
            f.write("-"*50 + "\n")
            for year, month, gz_path, tif_path in downloaded_files:
                tif_size_mb = tif_path.stat().st_size / (1024 * 1024) if tif_path.exists() else 0
                f.write(f"{year}-{month:02d}: {tif_path.name} ({tif_size_mb:.1f} MB)\n")
            
            if failed_months:
                f.write("\nFAILED DOWNLOADS:\n")
                f.write("-"*50 + "\n")
                for year, month in failed_months:
                    f.write(f"{year}-{month:02d}\n")
        
        print(f"\n📝 Download log saved: {log_file}")
    
    # =========================================================================
    # VALIDATION AND METADATA METHODS
    # =========================================================================
    
    def validate_single_file(self, tif_path, create_preview=True):
        """
        Validate a CHIRPS GeoTIFF file and create metadata
        
        Parameters:
        -----------
        tif_path : Path
            Path to the GeoTIFF file
        create_preview : bool
            Whether to create a preview image
        """
        
        tif_path = Path(tif_path)
        print(f"\n🔍 Validating: {tif_path.name}")
        print("-"*50)
        
        # Extract year and month from filename
        # Expected: chirps-v2.0.YYYY.MM.tif
        try:
            import re
            match = re.search(r'(\d{4})\.(\d{2})', tif_path.name)
            if match:
                year = int(match.group(1))
                month = int(match.group(2))
            else:
                print("  ⚠️ Could not extract date from filename")
                return None
        except:
            print("  ⚠️ Could not extract date from filename")
            return None
        
        try:
            with rasterio.open(tif_path) as src:
                # Read basic info
                print(f"  CRS: {src.crs}")
                print(f"  Shape: {src.shape}")
                print(f"  Bounds: {src.bounds}")
                print(f"  NoData: {src.nodata}")
                
                # Read data
                data = src.read(1)
                
                # Calculate statistics (excluding nodata)
                if src.nodata is not None:
                    valid_data = data[data != src.nodata]
                else:
                    valid_data = data[~np.isnan(data)]
                
                stats = {
                    'min': float(np.min(valid_data)) if len(valid_data) > 0 else None,
                    'max': float(np.max(valid_data)) if len(valid_data) > 0 else None,
                    'mean': float(np.mean(valid_data)) if len(valid_data) > 0 else None,
                    'std': float(np.std(valid_data)) if len(valid_data) > 0 else None,
                    'valid_pixels': int(len(valid_data))
                }
                
                print(f"  Min: {stats['min']:.2f} mm/month")
                print(f"  Max: {stats['max']:.2f} mm/month")
                print(f"  Mean: {stats['mean']:.2f} mm/month")
                print(f"  Valid pixels: {stats['valid_pixels']:,}")
                
                # Create metadata file
                metadata_dir = self.dirs['metadata'] / str(year)
                metadata_dir.mkdir(exist_ok=True)
                metadata_path = metadata_dir / f"CHIRPS_{year}_{month:02d}_metadata.txt"
                
                self._create_metadata(
                    metadata_path=metadata_path,
                    tif_file=tif_path.name,
                    year=year,
                    month=month,
                    crs=str(src.crs),
                    bounds=src.bounds,
                    shape=src.shape,
                    stats=stats
                )
                
                # Create preview
                if create_preview and HAS_MATPLOTLIB:
                    preview_dir = self.dirs['previews'] / str(year)
                    preview_dir.mkdir(exist_ok=True)
                    preview_path = preview_dir / f"CHIRPS_{year}_{month:02d}_preview.png"
                    
                    self._create_preview(
                        data=data,
                        bounds=src.bounds,
                        output_path=preview_path,
                        year=year,
                        month=month,
                        nodata=src.nodata
                    )
                
                print(f"  ✅ Validated: {tif_path.name}")
                return stats
                
        except Exception as e:
            print(f"  ❌ Validation error: {e}")
            traceback.print_exc()
            return None
    
    def _create_metadata(self, metadata_path, tif_file, year, month, crs, bounds, shape, stats):
        """Create metadata file"""
        try:
            import calendar
            
            with open(metadata_path, 'w') as f:
                f.write("="*60 + "\n")
                f.write(f"CHIRPS v{self.version} MONTHLY METADATA\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"Processing Date: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"File: {tif_file}\n\n")
                
                f.write(f"Year: {year}\n")
                f.write(f"Month: {month} ({calendar.month_name[month]})\n\n")
                
                f.write("GEOSPATIAL INFORMATION:\n")
                f.write(f"  CRS: {crs}\n")
                f.write(f"  Bounds: {bounds}\n")
                f.write(f"  Shape (rows, cols): {shape}\n\n")
                
                f.write("STATISTICS (mm/month):\n")
                f.write(f"  Minimum: {stats['min']:.2f}\n")
                f.write(f"  Maximum: {stats['max']:.2f}\n")
                f.write(f"  Mean: {stats['mean']:.2f}\n")
                f.write(f"  Std Dev: {stats['std']:.2f}\n")
                f.write(f"  Valid pixels: {stats['valid_pixels']:,}\n\n")
                
                f.write("DATA INFORMATION:\n")
                f.write(f"  Dataset: CHIRPS v{self.version}\n")
                f.write("  Resolution: 0.05° (~5.5 km)\n")
                f.write("  Coverage: 50°S to 50°N (global land)\n")
                f.write("  Units: mm/month (no conversion needed)\n")
                f.write("  Source: Climate Hazards Center, UCSB\n")
                
        except Exception as e:
            print(f"    ⚠️ Metadata error: {e}")
    
    def _create_preview(self, data, bounds, output_path, year, month, nodata=None):
        """Create preview plot"""
        try:
            import calendar
            
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Mask nodata values
            if nodata is not None:
                plot_data = np.where(data == nodata, np.nan, data)
            else:
                plot_data = data.copy()
            
            # Mask zeros for better visualization
            plot_data = np.where(plot_data <= 0, np.nan, plot_data)
            
            # Colormap
            cmap = cm.get_cmap('YlGnBu').copy()
            cmap.set_bad('#cccccc', 1.0)
            
            # Plot
            extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
            
            im = ax.imshow(plot_data, 
                          cmap=cmap,
                          extent=extent,
                          interpolation='nearest',
                          aspect='auto',
                          norm=colors.LogNorm(vmin=1, vmax=max(np.nanmax(plot_data), 10)))
            
            # Colorbar
            cbar = plt.colorbar(im, ax=ax, extend='max', pad=0.02, fraction=0.046)
            cbar.set_label('Precipitation (mm/month)', fontsize=12)
            
            # Labels
            month_name = calendar.month_name[month]
            ax.set_title(f'CHIRPS v{self.version} - {month_name} {year}', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Longitude', fontsize=12)
            ax.set_ylabel('Latitude', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            print(f"    ✅ Preview saved: {output_path.name}")
            
        except Exception as e:
            print(f"    ⚠️ Preview error: {e}")
    
    def validate_all_files(self, start_year=1981, end_year=2027, create_previews=True):
        """Validate all downloaded files"""
        
        print(f"\n🔍 VALIDATING ALL FILES: {start_year} to {end_year}")
        print("="*70)
        
        if not HAS_RASTERIO:
            print("❌ rasterio not available. Install with: pip install rasterio")
            return []
        
        validated_files = []
        failed_files = []
        
        for year in range(start_year, end_year + 1):
            year_tif_dir = self.dirs['geotiffs'] / str(year)
            
            if not year_tif_dir.exists():
                print(f"\n📁 Year {year}: No geotiff directory")
                continue
            
            tif_files = list(year_tif_dir.glob("*.tif"))
            
            if not tif_files:
                print(f"\n📁 Year {year}: No TIF files found")
                continue
            
            print(f"\n📁 Year {year}: {len(tif_files)} files to validate")
            
            for tif_file in sorted(tif_files):
                result = self.validate_single_file(tif_file, create_previews)
                
                if result:
                    validated_files.append(tif_file)
                else:
                    failed_files.append(tif_file)
        
        # Summary
        print(f"\n" + "="*70)
        print("📊 VALIDATION SUMMARY")
        print("="*70)
        print(f"Successfully validated: {len(validated_files)} files")
        print(f"Failed: {len(failed_files)} files")
        
        if failed_files:
            print("\nFailed files:")
            for file in failed_files[:10]:  # Show first 10
                print(f"  {file.name}")
            if len(failed_files) > 10:
                print(f"  ... and {len(failed_files) - 10} more")
        
        # Create validation log
        self._create_validation_log(validated_files, failed_files)
        
        return validated_files
    
    def _create_validation_log(self, validated_files, failed_files):
        """Create validation log"""
        log_file = self.dirs['logs'] / f"validation_log_{dt.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(log_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write(f"CHIRPS v{self.version} VALIDATION LOG\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Validation date: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total validated: {len(validated_files)}\n")
            f.write(f"Total failed: {len(failed_files)}\n\n")
            
            f.write("VALIDATED FILES:\n")
            f.write("-"*50 + "\n")
            for filepath in validated_files:
                size_mb = filepath.stat().st_size / (1024 * 1024) if filepath.exists() else 0
                f.write(f"{filepath.name} ({size_mb:.1f} MB)\n")
        
        print(f"\n📝 Validation log saved: {log_file}")
    
    # =========================================================================
    # COMPLETE WORKFLOW
    # =========================================================================
    
    def run_complete_workflow(self, start_year=1981, end_year=2027, skip_download=False):
        """
        Run complete workflow: download and validate
        
        Parameters:
        -----------
        start_year : int
            Starting year (default: 1981)
        end_year : int
            Ending year (default: 2027)
        skip_download : bool
            Skip download step (use existing files)
        """
        
        print("\n" + "="*70)
        print(f"🚀 CHIRPS v{self.version} COMPLETE WORKFLOW")
        print("="*70)
        
        # Check dependencies
        if not HAS_RASTERIO:
            print("❌ Missing dependency: rasterio")
            print("Install with: pip install rasterio numpy")
            return
        
        # Step 1: Download
        downloaded_files = []
        if not skip_download:
            print("\n📥 STEP 1: DOWNLOADING DATA")
            print("-"*70)
            downloaded_files = self.download_year_range(start_year, end_year)
        else:
            print("\n📥 STEP 1: SKIPPING DOWNLOAD (using existing files)")
        
        # Step 2: Validate
        print("\n🔍 STEP 2: VALIDATING DATA")
        print("-"*70)
        validated_files = self.validate_all_files(start_year, end_year)
        
        # Final summary
        print("\n" + "="*70)
        print("🎉 WORKFLOW COMPLETE!")
        print("="*70)
        
        # Count files
        total_geotiffs = sum(1 for _ in self.dirs['geotiffs'].rglob("*.tif"))
        total_previews = sum(1 for _ in self.dirs['previews'].rglob("*.png"))
        
        print(f"\n📁 DIRECTORY STRUCTURE:")
        for name, path in self.dirs.items():
            if name == 'logs':
                continue
            file_count = len(list(path.rglob("*.*")))
            print(f"  {name}/ - {file_count} files")
        
        print(f"\n📊 OUTPUT STATISTICS:")
        print(f"  GeoTIFF files: {total_geotiffs}")
        print(f"  Preview images: {total_previews}")
        
        print(f"\n🎯 TO USE IN QGIS:")
        print(f"  1. Open QGIS")
        print(f"  2. Add basemap (XYZ Tiles → OpenStreetMap)")
        print(f"  3. Load GeoTIFFs from: {self.dirs['geotiffs']}")
        print(f"  4. Files are already georeferenced and ready to use!")
        
        print(f"\n💡 KEY DIFFERENCES FROM GPM:")
        print(f"  • CHIRPS data is ALREADY in mm/month (no conversion needed)")
        print(f"  • Files are downloaded as .gz and auto-extracted to .tif")
        print(f"  • Resolution: 0.05° (~5.5 km) vs GPM 0.1° (~11 km)")
        print(f"  • Coverage: 50°S-50°N (land only) vs GPM global")
        
        print(f"\n📁 Full output at: {self.base_dir}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function"""
    
    print("\n" + "="*70)
    print("🌧️ CHIRPS COMPLETE WORKFLOW MANAGER")
    print("="*70)
    print("Downloads CHIRPS data (1981-2025) as monthly GeoTIFFs")
    print("Resolution: 0.05° | Coverage: 50°S-50°N | Units: mm/month")
    print("="*70)
    
    # Version selection
    print("\nSelect CHIRPS version:")
    print("1. CHIRPS v2.0 (1981-2027, stable)")
    print("2. CHIRPS v3.0 (2027+, latest)")
    
    version_choice = input("\nVersion (1-2) [default: 1]: ").strip()
    version = "2.0" if version_choice != "2" else "3.0"
    
    # Create workflow instance
    workflow = CHIRPSCompleteWorkflow(version=version)
    
    while True:
        print("\n📋 MAIN MENU:")
        print("1. Run complete workflow (download + validate)")
        print("2. Download only (1981-2025)")
        print("3. Validate only (using existing downloads)")
        print("4. Check directory structure")
        print("5. Download specific year range")
        print("6. Exit")
        
        choice = input("\nChoice (1-6): ").strip()
        
        if choice == '1':
            print("\n🚀 COMPLETE WORKFLOW")
            print("="*70)
            
            start_year = input("Start year [default: 1981]: ").strip()
            start_year = int(start_year) if start_year.isdigit() else 1981
            
            end_year = input("End year [default: 2027]: ").strip()
            end_year = int(end_year) if end_year.isdigit() else 2025
            
            # Confirm for large downloads
            total_months = (end_year - start_year + 1) * 12
            print(f"\n⚠️ This will process up to {total_months} months")
            print(f"   Approximate total download size: {total_months * 30 / 1024:.1f} GB (compressed)")
            
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                workflow.run_complete_workflow(start_year, end_year)
            else:
                print("Operation cancelled")
        
        elif choice == '2':
            print("\n📥 DOWNLOAD ONLY")
            print("="*70)
            
            start_year = input("Start year [default: 1981]: ").strip()
            start_year = int(start_year) if start_year.isdigit() else 1981
            
            end_year = input("End year [default: 2027]: ").strip()
            end_year = int(end_year) if end_year.isdigit() else 2025
            
            workflow.download_year_range(start_year, end_year)
        
        elif choice == '3':
            print("\n🔍 VALIDATE ONLY")
            print("="*70)
            
            start_year = input("Start year [default: 1981]: ").strip()
            start_year = int(start_year) if start_year.isdigit() else 1981
            
            end_year = input("End year [default: 2027]: ").strip()
            end_year = int(end_year) if end_year.isdigit() else 2025
            
            create_previews = input("Create preview images? (y/n) [default: y]: ").strip().lower()
            create_previews = create_previews != 'n'
            
            workflow.validate_all_files(start_year, end_year, create_previews)
        
        elif choice == '4':
            print("\n📁 DIRECTORY STRUCTURE")
            print("="*70)
            
            for name, path in workflow.dirs.items():
                if path.exists():
                    file_count = len(list(path.rglob("*.*")))
                    dir_count = len(list(path.rglob("*/")))
                    print(f"{name}/ - {file_count} files, {dir_count} subdirectories")
                else:
                    print(f"{name}/ - NOT CREATED")
        
        elif choice == '5':
            print("\n📥 DOWNLOAD SPECIFIC RANGE")
            print("="*70)
            
            start_year = input("Start year: ").strip()
            start_year = int(start_year) if start_year.isdigit() else 1981
            
            end_year = input("End year: ").strip()
            end_year = int(end_year) if end_year.isdigit() else 2027
            
            workflow.download_year_range(start_year, end_year)
        
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

# =============================================================================
# QUICK START (for testing)
# =============================================================================

def quick_start():
    """Quick start for testing with small range"""
    
    print("\n" + "="*70)
    print("🚀 CHIRPS WORKFLOW QUICK START")
    print("="*70)
    print("Testing with 2020-2021 (2 years)")
    print("="*70)
    
    workflow = CHIRPSCompleteWorkflow(version="2.0")
    
    # Run for test range
    workflow.run_complete_workflow(start_year=2020, end_year=2021)
    
    print("\n✅ Quick start complete!")
    print(f"Check output in: {workflow.base_dir}")

# =============================================================================
# DIRECT EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Check for required dependencies
    missing_deps = []
    try:
        import rasterio
    except ImportError:
        missing_deps.append("rasterio")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("\nInstall with:")
        print("  pip install rasterio numpy matplotlib")
        print("\nThen run the script again.")
        exit(1)
    
    # Run the workflow
    print("\nSelect execution mode:")
    print("1. Complete workflow (1981-2027)")
    print("2. Quick start (test with 2020-2021)")
    print("3. Interactive menu")
    
    mode = input("\nMode (1-3): ").strip()
    
    if mode == '1':
        workflow = CHIRPSCompleteWorkflow(version="2.0")
        workflow.run_complete_workflow(start_year=1981, end_year=2027)
    elif mode == '2':
        quick_start()
    elif mode == '3':
        main()
    else:
        print("❌ Invalid mode. Using interactive menu.")
        main()