"""
Complete Data Pipeline for Baltimore Dashboard Project
Runs all data extraction, integration, and validation steps

Author: AI Assistant for 蔡伊扬
Date: 2026-02-15

Usage:
    python run_full_pipeline.py [--skip-download] [--validate-only]
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import argparse

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_script(script_name, description):
    """
    Run a Python script and handle errors.
    
    Args:
        script_name: Name of the script to run
        description: Human-readable description
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"[info] {description}...")
    print(f"[info] Running: {script_name}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[OK] {description} completed in {elapsed:.1f}s")
            if result.stdout:
                # Print last few lines of output
                lines = result.stdout.strip().split('\n')
                for line in lines[-5:]:
                    print(f"  {line}")
            return True
        else:
            print(f"[ERROR] {description} failed!")
            print(f"[ERROR] Exit code: {result.returncode}")
            if result.stderr:
                print(f"[ERROR] Error output:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] {description} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"[ERROR] {description} failed with exception: {e}")
        return False


def check_prerequisites():
    """Check if required files and API keys exist."""
    print_section("Checking Prerequisites")
    
    all_good = True
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("[WARN] .env file not found")
        print("[WARN] API keys may not be configured")
        all_good = False
    else:
        print("[OK] .env file found")
    
    # Check for required scripts
    required_scripts = [
        "expand_health_indicators.py",
        "fetch_census_economic_data.py",
        "integrate_economic_data.py",
        "Baltimore_MetricsWithMap.py"
    ]
    
    for script in required_scripts:
        if os.path.exists(script):
            print(f"[OK] Found: {script}")
        else:
            print(f"[ERROR] Missing: {script}")
            all_good = False
    
    return all_good


def run_data_extraction():
    """Run all data extraction scripts."""
    print_section("Step 1: Data Extraction")
    
    steps = [
        ("expand_health_indicators.py", "Expanding health indicators (4 → 35)"),
        ("fetch_census_economic_data.py", "Fetching economic indicators (24 metrics)"),
    ]
    
    for script, description in steps:
        if not run_script(script, description):
            print(f"\n[ERROR] Pipeline failed at: {description}")
            return False
    
    return True


def run_data_integration():
    """Run data integration script."""
    print_section("Step 2: Data Integration")
    
    return run_script(
        "integrate_economic_data.py",
        "Integrating health + economic data"
    )


def run_dashboard_generation():
    """Generate dashboards."""
    print_section("Step 3: Dashboard Generation")
    
    return run_script(
        "Baltimore_MetricsWithMap.py",
        "Generating health dashboard"
    )


def run_validation():
    """Run data validation checks."""
    print_section("Step 4: Data Validation")
    
    print("[info] Running validation checks...")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Health data exists
    checks_total += 1
    health_file = "data/health_expanded/baltimore_health_35indicators_2022.csv"
    if os.path.exists(health_file):
        print(f"[OK] Health data file exists: {health_file}")
        checks_passed += 1
    else:
        print(f"[ERROR] Health data file missing: {health_file}")
    
    # Check 2: Economic data exists
    checks_total += 1
    econ_file = "data/economic/baltimore_economic_data_2022.csv"
    if os.path.exists(econ_file):
        print(f"[OK] Economic data file exists: {econ_file}")
        checks_passed += 1
    else:
        print(f"[ERROR] Economic data file missing: {econ_file}")
    
    # Check 3: Integrated data exists
    checks_total += 1
    integrated_file = "data/integrated/baltimore_integrated_health_economic_2022.csv"
    if os.path.exists(integrated_file):
        print(f"[OK] Integrated data file exists: {integrated_file}")
        checks_passed += 1
    else:
        print(f"[ERROR] Integrated data file missing: {integrated_file}")
    
    # Check 4: Dashboard HTML exists
    checks_total += 1
    dashboard_file = "output/dashboard_multi_year.html"
    if os.path.exists(dashboard_file):
        print(f"[OK] Dashboard HTML exists: {dashboard_file}")
        checks_passed += 1
    else:
        print(f"[ERROR] Dashboard HTML missing: {dashboard_file}")
    
    # Check 5: Data completeness (if pandas available)
    checks_total += 1
    try:
        import pandas as pd
        df = pd.read_csv(integrated_file)
        if len(df) == 199:
            print(f"[OK] Integrated data has correct number of tracts: 199")
            checks_passed += 1
        else:
            print(f"[WARN] Expected 199 tracts, found {len(df)}")
    except Exception as e:
        print(f"[WARN] Could not validate data completeness: {e}")
    
    print(f"\n[info] Validation: {checks_passed}/{checks_total} checks passed")
    
    return checks_passed == checks_total


def print_summary(success, elapsed_time):
    """Print pipeline execution summary."""
    print_section("Pipeline Summary")
    
    if success:
        print("[OK] Pipeline completed successfully!")
        print(f"[OK] Total time: {elapsed_time:.1f} seconds")
        print("\nGenerated files:")
        print("  - data/health_expanded/baltimore_health_35indicators_2022.csv")
        print("  - data/economic/baltimore_economic_data_2022.csv")
        print("  - data/integrated/baltimore_integrated_health_economic_2022.csv")
        print("  - output/dashboard_multi_year.html")
        print("\nNext steps:")
        print("  1. Open output/dashboard_multi_year.html in your browser")
        print("  2. Run: streamlit run BLS_and_FRED_Data_Interface.py")
        print("  3. Review PAPER_METHODS_DRAFT.md for publication")
    else:
        print("[ERROR] Pipeline failed!")
        print(f"[ERROR] Time elapsed: {elapsed_time:.1f} seconds")
        print("\nTroubleshooting:")
        print("  1. Check API keys in .env file")
        print("  2. Review error messages above")
        print("  3. Run individual scripts manually for debugging")


def main():
    """Main pipeline execution."""
    parser = argparse.ArgumentParser(description="Run Baltimore Dashboard data pipeline")
    parser.add_argument("--skip-download", action="store_true", 
                       help="Skip data download steps")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only run validation checks")
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("  Baltimore Dashboard - Complete Data Pipeline")
    print("  Integrating Health and Economic Indicators")
    print("=" * 70)
    
    start_time = time.time()
    success = True
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n[WARN] Some prerequisites are missing, but continuing...")
    
    # Run pipeline steps
    if args.validate_only:
        success = run_validation()
    else:
        if not args.skip_download:
            if not run_data_extraction():
                success = False
        
        if success and not run_data_integration():
            success = False
        
        if success and not run_dashboard_generation():
            success = False
        
        if success:
            run_validation()
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print_summary(success, elapsed_time)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
