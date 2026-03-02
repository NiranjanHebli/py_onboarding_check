"""Developer onboarding verification script.

Checks Python version, virtual environment, installed packages,
and internet connectivity. Generates a setup_report.txt summary.
"""

import sys
import os
import importlib
import subprocess
from datetime import datetime


MIN_PYTHON_MAJOR = 3
MIN_PYTHON_MINOR = 10
CONNECTIVITY_URL = "https://httpbin.org/get"
REPORT_FILE = "setup_report.txt"


def check_python_version():
    """Check that Python version is 3.10 or newer."""
    major = sys.version_info.major
    minor = sys.version_info.minor
    version_str = f"{major}.{minor}.{sys.version_info.micro}"
    passed = (major, minor) >= (MIN_PYTHON_MAJOR, MIN_PYTHON_MINOR)
    if not passed:
        print(
            f"[WARN] Python version: {version_str} "
            f"(>= {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR} required)"
        )
    return passed, version_str


def check_virtual_env():
    """Check that the script is running inside a virtual environment."""
    in_venv = sys.prefix != sys.base_prefix
    venv_name = os.path.basename(sys.prefix) if in_venv else None
    if not in_venv:
        print("[ERROR] Not running inside a virtual environment.")
    return in_venv, venv_name


def get_installed_packages():
    """Return a dict of {package_name: version} for all installed packages."""
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--format=json"],
        capture_output=True,
        text=True,
        check=False,
    )
    packages = {}
    if result.returncode == 0:
        import json  # pylint: disable=import-outside-toplevel

        for pkg in json.loads(result.stdout):
            packages[pkg["name"].lower()] = pkg["version"]
    return packages


def check_package_importable(package_name):
    """Try to import a package and return (success, version_or_error)."""
    try:
        module = importlib.import_module(package_name)
        version = getattr(module, "__version__", "unknown")
        return True, version
    except ImportError as exc:
        return False, str(exc)


def check_internet_connectivity():
    """Try to reach a public URL using requests."""
    try:
        import requests  # pylint: disable=import-outside-toplevel

        response = requests.get(CONNECTIVITY_URL, timeout=5)
        response.raise_for_status()
        return True, "OK"
    except ImportError:
        return False, "requests not installed"
    except Exception as exc:  # pylint: disable=broad-except
        return False, str(exc)


def build_report(results):
    """Build a formatted report string from results list."""
    lines = []
    lines.append("=== Developer Onboarding Check ===")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    passed_count = 0
    for label, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        lines.append(f"[{status}] {label}: {detail}")
        if passed:
            passed_count += 1

    total = len(results)
    symbol = "✓" if passed_count == total else "✗"
    lines.append("")
    lines.append("---")
    lines.append(f"Result: {passed_count}/{total} checks passed {symbol}")
    return "\n".join(lines)


def save_report(report_text):
    """Save report text to REPORT_FILE."""
    with open(REPORT_FILE, "w", encoding="utf-8") as fh:
        fh.write(report_text)
        fh.write("\n")


def main():
    """Run all onboarding checks and print/save the report."""
    results = []

    # 1. Python version
    py_passed, py_version = check_python_version()
    results.append(
        (
            f"Python version",
            py_passed,
            f"{py_version} (>= {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR} required)",
        )
    )

    # 2. Virtual environment
    venv_passed, venv_name = check_virtual_env()
    venv_detail = f"Active ({venv_name})" if venv_passed else "Not active"
    results.append(("Virtual environment", venv_passed, venv_detail))

    # 3. pylint
    pylint_ok, pylint_ver = check_package_importable("pylint")
    results.append(
        (
            "pylint installed",
            pylint_ok,
            f"version {pylint_ver}" if pylint_ok else pylint_ver,
        )
    )

    # 4. black
    black_ok, black_ver = check_package_importable("black")
    results.append(
        (
            "black installed",
            black_ok,
            f"version {black_ver}" if black_ok else black_ver,
        )
    )

    # 5. Internet connectivity
    inet_ok, inet_detail = check_internet_connectivity()
    results.append(("Internet connectivity", inet_ok, inet_detail))

    # 6. numpy
    numpy_ok, numpy_ver = check_package_importable("numpy")
    results.append(
        (
            "numpy installed",
            numpy_ok,
            f"version {numpy_ver}" if numpy_ok else numpy_ver,
        )
    )

    # 7. List all packages (informational, not a pass/fail check)
    packages = get_installed_packages()
    if packages:
        print("\n--- Installed Packages ---")
        for name, version in sorted(packages.items()):
            print(f"  {name}=={version}")
        print()

    # Build and output report
    report = build_report(results)
    print(report)
    save_report(report)
    print(f"\nReport saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()