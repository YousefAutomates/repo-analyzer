#!/usr/bin/env python3
"""
GitHub Repository Analyzer v2.0.0
Quick start script with dependency management.

Author: Yousef Elsherbiny (YousefAutomates)
Website: https://yousefautomates.pages.dev
"""

import subprocess
import sys
import os


def install_dependencies():
    """Install required packages if not already present."""
    required = {
        "requests": "requests",
        "rich": "rich",
    }

    missing = []
    for import_name, package_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    if missing:
        print(f"  📦 Installing: {', '.join(missing)}")
        for package in missing:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        print("  ✅ Dependencies installed!")
    else:
        print("  ✅ All dependencies ready!")


def detect_environment():
    """Detect the running environment."""
    try:
        import google.colab
        return "colab"
    except ImportError:
        pass

    if os.environ.get("KAGGLE_KERNEL_RUN_TYPE"):
        return "kaggle"

    return "terminal"


if __name__ == "__main__":
    print()
    print("=" * 56)
    print("  🔍 GitHub Repository Analyzer v2.0.0")
    print("  📦 Checking dependencies...")
    print("=" * 56)

    install_dependencies()

    env = detect_environment()
    print(f"  🖥️  Environment: {env}")
    print()

    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from analyzer.main import RepoAnalyzerApp
    app = RepoAnalyzerApp()
    app.run()
