import os
from datetime import datetime
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class FileExporter:
    """
    Exports analysis reports to TXT format with auto-download support.
    Optimized for Google Colab and Kaggle environments.

    Author: Yousef Elsherbiny (YousefAutomates)
    """

    def __init__(self, output_dir: str = "output"):
        """
        Initialize the exporter.

        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _generate_filename(self, repo_name: str) -> str:
        """
        Generate a timestamped filename.

        Args:
            repo_name: Repository name for the filename

        Returns:
            Base filename without extension
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = repo_name.replace("/", "_").replace(" ", "_")
        return f"repo_analysis_{safe_name}_{timestamp}"

    def export_txt(self, report_text: str, repo_name: str) -> str:
        """
        Export report as a TXT file.

        Args:
            report_text: The complete report text
            repo_name: Repository name for the filename

        Returns:
            Path to the created file
        """
        filename = f"{self._generate_filename(repo_name)}.txt"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)

        file_size = os.path.getsize(filepath)
        print(f"  📄 TXT exported: {filepath} ({self._format_size(file_size)})")

        return filepath

    def auto_download(self, filepath: str) -> bool:
        """
        Automatically download the file in Colab/Kaggle.

        Args:
            filepath: Path to the file to download

        Returns:
            True if download was triggered, False otherwise
        """
        if not os.path.exists(filepath):
            print(f"  ❌ File not found: {filepath}")
            return False

        # Try Google Colab
        try:
            from google.colab import files
            print(f"  ⬇️  Downloading: {os.path.basename(filepath)}")
            files.download(filepath)
            return True
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Colab download failed: {e}")
            print(f"  ⚠️  Auto-download failed: {e}")

        # Try Kaggle
        try:
            kaggle_output = "/kaggle/working"
            if os.path.exists(kaggle_output):
                import shutil
                dest = os.path.join(kaggle_output, os.path.basename(filepath))
                shutil.copy2(filepath, dest)
                print(f"  📁 Copied to Kaggle output: {dest}")
                return True
        except Exception as e:
            logger.warning(f"Kaggle copy failed: {e}")

        # Terminal - just show path
        print(f"  📁 File saved at: {os.path.abspath(filepath)}")
        return False

    def export_and_download(
        self,
        report_text: str,
        repo_name: str,
        scan_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Export as TXT and automatically download.

        Args:
            report_text: The complete report text
            repo_name: Repository name
            scan_data: Optional scan data (for future use)

        Returns:
            Dictionary with format -> filepath mapping
        """
        exported = {}

        try:
            filepath = self.export_txt(report_text, repo_name)
            exported["txt"] = filepath
        except Exception as e:
            print(f"  ❌ Export error: {e}")
            logger.error(f"TXT export failed: {e}")
            return exported

        # Show file info
        file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        print(f"\n  📊 Report Summary:")
        print(f"     File    : {os.path.basename(filepath)}")
        print(f"     Size    : {self._format_size(file_size)}")
        print(f"     Lines   : {len(report_text.splitlines()):,}")
        print(f"     Chars   : {len(report_text):,}")

        if scan_data:
            tokens = scan_data.get("estimated_tokens", len(report_text) // 4)
            print(f"     Tokens  : ~{tokens:,} (estimated)")

        # Auto download
        print()
        self.auto_download(filepath)

        return exported

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                if unit == "B":
                    return f"{int(size_bytes)} {unit}"
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
