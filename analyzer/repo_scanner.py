import os
import logging
from typing import Dict, List, Optional, Set, Any
from .github_client import GitHubClient

logger = logging.getLogger(__name__)


class RepoScanner:
    """
    Scans a GitHub repository and collects all information
    needed for generating AI-ready reports.
    """

    # Source code and text file extensions
    CODE_EXTENSIONS: Set[str] = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".r", ".R",
        ".lua", ".sh", ".bash", ".zsh", ".sql", ".html", ".htm", ".css", ".scss",
        ".sass", ".less", ".xml", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
        ".conf", ".env", ".md", ".markdown", ".rst", ".txt", ".csv", ".gitignore",
        ".dockerignore", ".vue", ".svelte", ".graphql", ".proto", ".ipynb", ".dart",
        ".ex", ".elm", ".hs", ".clj", ".lock", ".gradle", ".tf", ".cmake",
        ".bat", ".cmd", ".ps1", ".psm1", ".psd1",
        ".rake", ".gemspec", ".podspec", ".m", ".mm",
        ".pl", ".pm", ".t", ".cgi",
        ".asm", ".s", ".v", ".vhd", ".vhdl",
        ".nix", ".dhall", ".jsonnet",
    }

    # Binary file extensions (skip these)
    BINARY_EXTENSIONS: Set[str] = {
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
        ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac", ".ogg",
        ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar", ".xz",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".exe", ".dll", ".so", ".dylib", ".bin",
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        ".pyc", ".class", ".o", ".obj",
        ".db", ".sqlite", ".sqlite3",
        ".pkl", ".h5", ".hdf5", ".model", ".weights",
        ".pb", ".onnx", ".pt", ".pth", ".safetensors",
        ".min.js", ".min.css", ".map",
        ".jar", ".war", ".ear",
        ".apk", ".ipa", ".deb", ".rpm",
        ".iso", ".img", ".dmg",
    }

    # Important files that should always be included
    SPECIAL_FILES: Set[str] = {
        "README.md", "README", "README.rst", "README.txt",
        "LICENSE", "LICENSE.md", "LICENSE.txt",
        "CHANGELOG.md", "CHANGELOG", "CHANGES.md",
        "CONTRIBUTING.md", "CONTRIBUTING",
        "CODE_OF_CONDUCT.md",
        ".gitignore", ".gitattributes",
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        "Makefile", "CMakeLists.txt",
        "requirements.txt", "Pipfile", "Pipfile.lock",
        "setup.py", "setup.cfg", "pyproject.toml",
        "package.json", "package-lock.json", "yarn.lock",
        "Gemfile", "Gemfile.lock",
        "Cargo.toml", "Cargo.lock",
        "go.mod", "go.sum",
        "pom.xml", "build.gradle", "build.gradle.kts",
        "tsconfig.json", "webpack.config.js", "vite.config.js",
        ".env.example", ".env.sample",
        "Procfile", "vercel.json", "netlify.toml",
        "fly.toml", "render.yaml",
        ".eslintrc.json", ".prettierrc",
        "jest.config.js", "pytest.ini", "tox.ini",
    }

    # Directories to always skip
    SKIP_DIRECTORIES: Set[str] = {
        "node_modules", "__pycache__", ".git", ".svn", ".hg",
        "vendor", "venv", "env", ".env", ".venv",
        "dist", "build", "out", "target",
        ".idea", ".vscode", ".vs",
        "coverage", ".nyc_output",
        ".tox", ".pytest_cache", ".mypy_cache",
        "eggs", "*.egg-info",
        ".terraform",
    }

    DEFAULT_MAX_FILE_SIZE = 500 * 1024  # 500 KB
    DEFAULT_MAX_FILES = 500

    def __init__(self, client: GitHubClient):
        """
        Initialize the scanner.

        Args:
            client: GitHubClient instance for API access
        """
        self.client = client
        self.max_file_size = self.DEFAULT_MAX_FILE_SIZE
        self.max_files = self.DEFAULT_MAX_FILES
        self.ignore_patterns: List[str] = []

    def is_text_file(self, path: str) -> bool:
        """
        Determine if a file is a text file (not binary).

        Args:
            path: File path

        Returns:
            True if the file appears to be text
        """
        filename = os.path.basename(path)

        # Always include special files
        if filename in self.SPECIAL_FILES:
            return True

        _, ext = os.path.splitext(path.lower())

        # Definitely binary
        if ext in self.BINARY_EXTENSIONS:
            return False

        # Definitely text
        if ext in self.CODE_EXTENSIONS:
            return True

        # No extension - likely text (scripts, configs)
        if not ext:
            return True

        # Unknown extension - skip to be safe
        return False

    def should_skip_path(self, path: str) -> bool:
        """
        Check if a path should be skipped based on directory rules.

        Args:
            path: File path to check

        Returns:
            True if the path should be skipped
        """
        parts = path.split("/")
        for part in parts:
            if part in self.SKIP_DIRECTORIES:
                return True
            # Check egg-info pattern
            if part.endswith(".egg-info"):
                return True

        # Check custom ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in path:
                return True

        return False

    def get_category(self, path: str) -> str:
        """
        Categorize a file based on its extension.

        Args:
            path: File path

        Returns:
            Category name string
        """
        _, ext = os.path.splitext(path.lower())
        filename = os.path.basename(path).lower()

        categories = {
            "Python": {".py"},
            "JavaScript": {".js", ".jsx", ".mjs", ".cjs"},
            "TypeScript": {".ts", ".tsx"},
            "HTML": {".html", ".htm"},
            "CSS": {".css", ".scss", ".sass", ".less"},
            "Java": {".java"},
            "C/C++": {".c", ".cpp", ".h", ".hpp", ".cc", ".cxx"},
            "C#": {".cs"},
            "Go": {".go"},
            "Rust": {".rs"},
            "Ruby": {".rb", ".rake", ".gemspec"},
            "PHP": {".php"},
            "Swift": {".swift"},
            "Kotlin": {".kt", ".kts"},
            "Dart": {".dart"},
            "Shell": {".sh", ".bash", ".zsh", ".fish"},
            "PowerShell": {".ps1", ".psm1", ".psd1"},
            "SQL": {".sql"},
            "Markdown": {".md", ".markdown"},
            "JSON": {".json"},
            "YAML": {".yaml", ".yml"},
            "XML": {".xml"},
            "TOML": {".toml"},
            "Config": {".ini", ".cfg", ".conf", ".env"},
            "Jupyter": {".ipynb"},
        }

        if filename.startswith("dockerfile"):
            return "Docker"
        if filename == "makefile" or filename == "cmakelists.txt":
            return "Build"

        for category, extensions in categories.items():
            if ext in extensions:
                return category

        return "Other"

    def scan_repository(
        self,
        owner: str,
        repo_name: str,
        branch: Optional[str] = None,
        include_content: bool = True,
        max_file_size: Optional[int] = None,
        ignore_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform a complete scan of a GitHub repository.

        Args:
            owner: Repository owner username
            repo_name: Repository name
            branch: Branch to scan (uses default if None)
            include_content: Whether to fetch file contents
            max_file_size: Maximum file size in bytes to fetch
            ignore_patterns: List of path patterns to ignore

        Returns:
            Dictionary containing all scan results
        """
        if max_file_size:
            self.max_file_size = max_file_size
        if ignore_patterns:
            self.ignore_patterns = ignore_patterns

        print(f"\n{'=' * 55}")
        print(f"  📂 Scanning: {owner}/{repo_name}")
        print(f"{'=' * 55}")

        # Fetch repository metadata
        print("  📋 Fetching repository info...")
        repo_info = self.client.get_repo_info(owner, repo_name)

        print("  🔤 Fetching languages...")
        languages = self.client.get_repo_languages(owner, repo_name)

        print("  🌿 Fetching branches...")
        branches = self.client.get_repo_branches(owner, repo_name)

        print("  👥 Fetching contributors...")
        contributors = self.client.get_repo_contributors(owner, repo_name)

        print("  📝 Fetching latest commits...")
        scan_branch = branch or repo_info.get("default_branch", "main")
        commits = self.client.get_latest_commits(owner, repo_name, branch=scan_branch)

        print("  🌳 Fetching file tree...")
        tree = self.client.get_repo_tree(owner, repo_name, scan_branch)

        # Separate files and directories
        all_files = [item for item in tree if item["type"] == "blob"]
        all_dirs = [item for item in tree if item["type"] == "tree"]

        # Filter out skipped directories
        files = [f for f in all_files if not self.should_skip_path(f["path"])]
        dirs = [d for d in all_dirs if not self.should_skip_path(d["path"])]

        skipped_by_dir = len(all_files) - len(files)
        if skipped_by_dir > 0:
            print(f"  ⏭️  Skipped {skipped_by_dir} files in ignored directories")

        # Build visual tree
        print("  🏗️  Building directory structure...")
        tree_text = self._build_visual_tree(tree)

        # Fetch file contents
        file_contents: Dict[str, str] = {}
        file_categories: Dict[str, str] = {}
        binary_files: List[str] = []
        skipped_files: List[Dict] = []

        if include_content:
            text_files = [f for f in files if self.is_text_file(f["path"])]

            if len(text_files) > self.max_files:
                print(f"  ⚠️  Limiting to {self.max_files} files (found {len(text_files)})")
                text_files = text_files[:self.max_files]

            total = len(text_files)
            print(f"  📖 Reading {total} text files...")

            for index, file_item in enumerate(text_files):
                path = file_item["path"]
                size = file_item.get("size", 0)

                # Progress indicator
                if (index + 1) % 15 == 0 or index == total - 1:
                    percent = int((index + 1) / total * 100)
                    print(f"    [{percent:3d}%] ({index + 1}/{total}) files processed")

                # Skip oversized files
                if size and size > self.max_file_size:
                    skipped_files.append({
                        "path": path,
                        "reason": f"Too large ({size // 1024} KB > {self.max_file_size // 1024} KB)",
                        "size": size,
                    })
                    continue

                # Fetch content
                content = self.client.get_file_content(owner, repo_name, path, scan_branch)

                if content is not None:
                    if content.startswith("[Binary"):
                        binary_files.append(path)
                    else:
                        file_contents[path] = content
                        file_categories[path] = self.get_category(path)

            # Collect binary files
            for file_item in files:
                if not self.is_text_file(file_item["path"]) and file_item["path"] not in binary_files:
                    binary_files.append(file_item["path"])

        # Calculate statistics
        statistics = self._calculate_statistics(files, file_contents, file_categories, languages)

        # Estimate token count for AI
        total_chars = sum(len(c) for c in file_contents.values())
        estimated_tokens = total_chars // 4  # Rough estimate: ~4 chars per token

        print(f"\n  ✅ Scan complete!")
        print(f"     Files: {len(files)} | Read: {len(file_contents)} | "
              f"Dirs: {len(dirs)} | Binary: {len(binary_files)}")
        print(f"     Estimated tokens: ~{estimated_tokens:,}")

        return {
            "repo_info": repo_info,
            "languages": languages,
            "branches": branches,
            "contributors": contributors,
            "latest_commits": commits,
            "directory_structure_text": tree_text,
            "total_files": len(files),
            "total_directories": len(dirs),
            "file_contents": file_contents,
            "file_categories": file_categories,
            "binary_files": binary_files,
            "skipped_files": skipped_files,
            "statistics": statistics,
            "scan_branch": scan_branch,
            "estimated_tokens": estimated_tokens,
        }

    def _build_visual_tree(self, tree: List[Dict]) -> str:
        """Build a visual directory tree representation."""
        lines = ["Project Root"]
        tree_dict: Dict = {}

        for item in sorted(tree, key=lambda x: x["path"]):
            if self.should_skip_path(item["path"]):
                continue

            parts = item["path"].split("/")
            current = tree_dict

            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            leaf = parts[-1]
            if item["type"] == "blob":
                current[leaf] = None
            else:
                if leaf not in current:
                    current[leaf] = {}

        def render(node: Dict, prefix: str = ""):
            items = sorted(node.items(), key=lambda x: (x[1] is not None, x[0]))
            for i, (name, sub) in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                extension = "    " if is_last else "│   "

                if sub is None:
                    lines.append(f"{prefix}{connector}{name}")
                else:
                    lines.append(f"{prefix}{connector}{name}/")
                    render(sub, prefix + extension)

        render(tree_dict)
        return "\n".join(lines)

    def _calculate_statistics(
        self,
        files: List[Dict],
        contents: Dict[str, str],
        categories: Dict[str, str],
        languages: Dict[str, int],
    ) -> Dict[str, Any]:
        """Calculate comprehensive statistics about the repository."""
        total_lines = 0
        lines_by_file: Dict[str, int] = {}

        for path, content in contents.items():
            line_count = len(content.split("\n"))
            lines_by_file[path] = line_count
            total_lines += line_count

        # Count files by category
        category_counts: Dict[str, int] = {}
        for category in categories.values():
            category_counts[category] = category_counts.get(category, 0) + 1

        # Total size
        total_size = sum(f.get("size", 0) for f in files)

        # Language percentages
        total_lang_bytes = sum(languages.values()) or 1
        language_percentages = {
            lang: round(bytes_count / total_lang_bytes * 100, 1)
            for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)
        }

        # Largest files
        largest = sorted(
            [(f["path"], f.get("size", 0)) for f in files],
            key=lambda x: x[1],
            reverse=True
        )[:10]

        def format_size(size_bytes: int) -> str:
            for unit in ["B", "KB", "MB", "GB"]:
                if size_bytes < 1024:
                    return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{int(size_bytes)} B"
                size_bytes /= 1024
            return f"{size_bytes:.1f} TB"

        return {
            "total_lines": total_lines,
            "total_size": total_size,
            "total_size_formatted": format_size(total_size),
            "lines_by_file": lines_by_file,
            "files_by_category": category_counts,
            "language_percentages": language_percentages,
            "largest_files": [
                {"path": path, "size": size, "size_formatted": format_size(size)}
                for path, size in largest
            ],
            "total_text_files": len(contents),
            "avg_lines_per_file": round(total_lines / max(len(contents), 1), 1),
        }
