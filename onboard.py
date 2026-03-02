"""Developer onboarding verification script.

Checks Python version, virtual environment, installed packages,
disk space, and internet connectivity. Generates a setup_report.txt summary.

Usage:
    python onboard.py               # standard run
    python onboard.py --verbose     # show extra detail per check
    python onboard.py --fix         # auto-install any missing packages
    python onboard.py --verbose --fix
"""

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MIN_PYTHON_MAJOR = 3
MIN_PYTHON_MINOR = 10
CONNECTIVITY_URL = "https://httpbin.org/get"
REPORT_FILE = "setup_report.txt"
DISK_WARN_GB = 1.0
REQUIRED_PACKAGES = ["pylint", "black", "numpy", "requests"]


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def parse_args():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Developer onboarding environment verification script.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python onboard.py                # standard check\n"
            "  python onboard.py --verbose      # extra detail per check\n"
            "  python onboard.py --fix          # install missing packages\n"
            "  python onboard.py --verbose --fix\n"
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show extra diagnostic detail for every check.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to install any missing required packages via pip.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Timing helper
# ---------------------------------------------------------------------------
def timed(func, *args, **kwargs):
    """Run *func* and return (result, elapsed_seconds).

    Args:
        func: Callable to time.
        *args: Positional arguments forwarded to *func*.
        **kwargs: Keyword arguments forwarded to *func*.

    Returns:
        tuple: (return_value_of_func, elapsed_float_seconds)
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------
def check_python_version():
    """Check that the running Python is version 3.10 or newer.

    Returns:
        tuple: (passed, version_str, verbose_detail)
    """
    major = sys.version_info.major
    minor = sys.version_info.minor
    version_str = f"{major}.{minor}.{sys.version_info.micro}"
    impl = sys.implementation.name
    passed = (major, minor) >= (MIN_PYTHON_MAJOR, MIN_PYTHON_MINOR)
    detail = (
        f"{version_str} [{impl}] (>= {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR} required)"
    )
    return passed, version_str, detail


def check_virtual_env():
    """Check that the script is running inside a virtual environment.

    Returns:
        tuple: (passed, venv_name_or_None, verbose_detail)
    """
    in_venv = sys.prefix != sys.base_prefix
    venv_name = os.path.basename(sys.prefix) if in_venv else None
    if in_venv:
        detail = f"Active ({venv_name})  [{sys.prefix}]"
    else:
        detail = f"Not active  [sys.prefix={sys.prefix}]"
    return in_venv, venv_name, detail


def check_disk_space(path="."):
    """Check available disk space and warn if below DISK_WARN_GB.

    Args:
        path: Filesystem path to inspect (defaults to current directory).

    Returns:
        tuple: (passed, free_gb, verbose_detail)
    """
    usage = shutil.disk_usage(path)
    free_gb = usage.free / (1024 ** 3)
    total_gb = usage.total / (1024 ** 3)
    passed = free_gb >= DISK_WARN_GB
    detail = (
        f"{free_gb:.2f} GB free of {total_gb:.2f} GB total"
        f"  (warn threshold: {DISK_WARN_GB} GB)"
    )
    return passed, free_gb, detail


def check_package_importable(package_name):
    """Try to import *package_name* and retrieve its version attribute.

    Args:
        package_name: Top-level module name to import.

    Returns:
        tuple: (passed, version_or_error_str, install_location_str)
    """
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", "unknown")
        location = getattr(module, "__file__", "unknown location")
        return True, version, location
    except ImportError as exc:
        return False, str(exc), ""


def check_internet_connectivity(verbose=False):
    """Try to reach CONNECTIVITY_URL using the requests library.

    Args:
        verbose: When True, include the HTTP status code in the detail.

    Returns:
        tuple: (passed, detail_string)
    """
    try:
        import requests  # pylint: disable=import-outside-toplevel

        response = requests.get(CONNECTIVITY_URL, timeout=5)
        response.raise_for_status()
        detail = f"OK  [HTTP {response.status_code}]" if verbose else "OK"
        return True, detail
    except ImportError:
        return False, "requests not installed"
    except Exception as exc:  # pylint: disable=broad-except
        return False, str(exc)


def get_installed_packages():
    """Return {lowercase_name: version} for every pip-installed package."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=False,
    )
    packages = {}
    if result.returncode == 0:
        for pkg in json.loads(result.stdout):
            packages[pkg["name"].lower()] = pkg["version"]
    return packages


# ---------------------------------------------------------------------------
# Auto-fix
# ---------------------------------------------------------------------------
def attempt_fix(package_name):
    """Attempt to install *package_name* via pip.

    Args:
        package_name: PyPI package name to install.

    Returns:
        tuple: (success, message_string)
    """
    print(f"  [FIX] Attempting: pip install {package_name} ...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package_name],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print(f"  [FIX] Successfully installed {package_name}.")
        return True, "installed by --fix"
    stderr_lines = result.stderr.strip().splitlines()
    last_line = stderr_lines[-1] if stderr_lines else "unknown error"
    print(f"  [FIX] Failed to install {package_name}: {last_line}")
    return False, f"install failed: {last_line}"


# ---------------------------------------------------------------------------
# Report building
# ---------------------------------------------------------------------------
def build_report(results, total_elapsed):
    """Build a formatted report string from check results.

    Args:
        results: list of (label, passed, display_detail, elapsed_seconds)
        total_elapsed: total wall-clock time for the full run (seconds)

    Returns:
        Formatted multi-line report string.
    """
    lines = [
        "=== Developer Onboarding Check ===",
        f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total time: {total_elapsed:.3f}s",
        "",
    ]

    passed_count = 0
    for label, passed, detail, elapsed in results:
        status = "PASS" if passed else "FAIL"
        lines.append(f"[{status}] {label}: {detail}  ({elapsed * 1000:.1f}ms)")
        if passed:
            passed_count += 1

    total = len(results)
    symbol = "✓" if passed_count == total else "✗"
    lines += ["", "---", f"Result: {passed_count}/{total} checks passed {symbol}"]
    return "\n".join(lines)


def save_report(report_text):
    """Write *report_text* to REPORT_FILE on disk."""
    with open(REPORT_FILE, "w", encoding="utf-8") as fh:
        fh.write(report_text)
        fh.write("\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    """Orchestrate all onboarding checks, print results, and save report."""
    args = parse_args()
    results = []  # list of (label, passed, display_detail, elapsed_s)
    wall_start = time.perf_counter()

    print("=== Developer Onboarding Check ===\n")

    # 1. Python version
    (py_passed, py_version, py_detail), elapsed = timed(check_python_version)
    display = (
        py_detail
        if args.verbose
        else f"{py_version} (>= {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR} required)"
    )
    results.append(("Python version", py_passed, display, elapsed))

    # 2. Virtual environment
    (venv_passed, venv_name, venv_detail), elapsed = timed(check_virtual_env)
    display = (
        venv_detail
        if args.verbose
        else (f"Active ({venv_name})" if venv_passed else "Not active")
    )
    results.append(("Virtual environment", venv_passed, display, elapsed))

    # 3. Disk space
    (disk_passed, free_gb, disk_detail), elapsed = timed(check_disk_space)
    display = disk_detail if args.verbose else f"{free_gb:.2f} GB free"
    results.append(("Disk space", disk_passed, display, elapsed))
    if not disk_passed:
        print(f"  [WARN] Low disk space: only {free_gb:.2f} GB free!\n")

    # 4-7. Required packages (pylint, black, numpy, requests)
    for pkg in REQUIRED_PACKAGES:
        (ok, ver_or_err, location), elapsed = timed(check_package_importable, pkg)

        if not ok and args.fix:
            fix_ok, fix_msg = attempt_fix(pkg)
            if fix_ok:
                (ok, ver_or_err, location), retry_elapsed = timed(
                    check_package_importable, pkg
                )
                elapsed += retry_elapsed
                ver_or_err = f"{ver_or_err} ({fix_msg})"

        if ok:
            display = (
                f"version {ver_or_err}  [{location}]"
                if args.verbose
                else f"version {ver_or_err}"
            )
        else:
            display = ver_or_err

        results.append((f"{pkg} installed", ok, display, elapsed))

    # 8. Internet connectivity
    (inet_ok, inet_detail), elapsed = timed(check_internet_connectivity, args.verbose)
    results.append(("Internet connectivity", inet_ok, inet_detail, elapsed))

    # Full package listing — verbose mode only
    if args.verbose:
        packages, _ = timed(get_installed_packages)
        if packages:
            print("\n--- All Installed Packages ---")
            for name, version in sorted(packages.items()):
                print(f"  {name}=={version}")
            print()

    # Build, print, and persist the report
    total_elapsed = time.perf_counter() - wall_start
    report = build_report(results, total_elapsed)
    print(report)
    save_report(report)
    print(f"\nReport saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()