import os
import sys
import logging
from typing import Optional, Tuple, List, Dict

from .github_client import GitHubClient
from .repo_scanner import RepoScanner
from .report_generator import ReportGenerator
from .file_exporter import FileExporter

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class RepoAnalyzerApp:
    """
    Main application class for GitHub Repository Analyzer.
    Provides interactive CLI for analyzing repos and generating reports.

    Author: Yousef Elsherbiny (YousefAutomates)
    Website: https://yousefautomates.pages.dev
    """

    VERSION = "2.0.0"

    def __init__(self):
        """Initialize the application and all components."""
        self.client = GitHubClient()
        self.scanner = RepoScanner(self.client)
        self.generator = ReportGenerator()
        self.exporter = FileExporter()
        self.user_info: Optional[Dict] = None
        self.environment = self._detect_environment()

    @staticmethod
    def _detect_environment() -> str:
        """Detect running environment (colab, kaggle, terminal)."""
        try:
            import google.colab
            return "colab"
        except ImportError:
            pass

        if os.environ.get("KAGGLE_KERNEL_RUN_TYPE"):
            return "kaggle"

        return "terminal"

    def _input(self, prompt: str, default: Optional[str] = None) -> str:
        """
        Get user input with optional default value.

        Args:
            prompt: Input prompt text
            default: Default value if user presses Enter

        Returns:
            User input or default value
        """
        try:
            if default:
                result = input(f"{prompt} [{default}]: ").strip()
                return result if result else default
            return input(f"{prompt}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  ⚠️  Operation cancelled.")
            sys.exit(0)

    def _print_header(self):
        """Print the application header."""
        print()
        print("=" * 58)
        print("  🔍 GitHub Repository Analyzer v" + self.VERSION)
        print("  📋 Analyze repos & generate AI-ready reports")
        print(f"  🖥️  Environment: {self.environment}")
        print("  👤 By: YousefAutomates | yousefautomates.pages.dev")
        print("=" * 58)

    def _print_menu(self, title: str, options: List[str]):
        """Print a formatted menu."""
        print(f"\n{'─' * 55}")
        print(f"  {title}")
        print(f"{'─' * 55}")
        for idx, option in enumerate(options, 1):
            print(f"  {idx}. {option}")
        print(f"{'─' * 55}")

    def run(self):
        """Main application entry point."""
        self._print_header()

        # Mode selection
        self._print_menu("Choose Mode", [
            "📂 Analyze public repo (no token needed)",
            "🔒 Analyze private repo (token needed)",
            "📋 Login & browse my repos",
        ])

        mode = self._input("\nChoice (1/2/3)", "1")

        owner = None
        repo_name = None

        if mode == "1":
            result = self._mode_public()
            if not result:
                return
            owner, repo_name = result

        elif mode == "2":
            result = self._mode_private()
            if not result:
                return
            owner, repo_name = result

        elif mode == "3":
            result = self._mode_browse()
            if not result:
                return
            owner, repo_name = result

        else:
            print("  ❌ Invalid choice!")
            return

        # Select branch
        branch = self._select_branch(owner, repo_name)

        # Scan options with smart defaults
        print("\n  ⚙️  Using optimal default settings...")
        print("     ✅ Include file contents: Yes")
        print("     ✅ Include statistics: Yes")
        print("     ✅ Include commits: Yes")
        print("     ✅ Include contributors: Yes")
        print("     ✅ Max file size: 500 KB")

        customize = self._input("\n  Customize settings? (y/n)", "n").lower()

        if customize == "y":
            include_content = self._input("  Include file contents? (y/n)", "y").lower() == "y"
            include_stats = self._input("  Include statistics? (y/n)", "y").lower() == "y"
            include_commits = self._input("  Include commits? (y/n)", "y").lower() == "y"
            include_contributors = self._input("  Include contributors? (y/n)", "y").lower() == "y"
            max_size_kb = self._input("  Max file size in KB", "500")
            try:
                max_size = int(max_size_kb) * 1024
            except ValueError:
                max_size = 500 * 1024
        else:
            include_content = True
            include_stats = True
            include_commits = True
            include_contributors = True
            max_size = 500 * 1024

        # Perform scan
        try:
            scan_data = self.scanner.scan_repository(
                owner, repo_name, branch,
                include_content=include_content,
                max_file_size=max_size,
            )
        except Exception as e:
            print(f"\n  ❌ Scan error: {e}")
            logger.error(f"Scan failed: {e}", exc_info=True)
            return

        # Generate report
        print("\n  📝 Generating report...")
        report = self.generator.generate_report(
            scan_data,
            include_file_contents=include_content,
            include_statistics=include_stats,
            include_commits=include_commits,
            include_contributors=include_contributors,
        )
        print(f"  ✅ Report generated: {len(report):,} characters")

        # Export and download
        print("\n  📤 Exporting TXT report...")
        full_name = f"{owner}_{repo_name}"
        exported = self.exporter.export_and_download(report, full_name, scan_data)

        # Show preview option
        if self._input("\n  Show preview? (y/n)", "n").lower() == "y":
            preview_lines = report.split("\n")[:60]
            print("\n" + "─" * 60)
            for line in preview_lines:
                print(line)
            remaining = len(report.split("\n")) - 60
            if remaining > 0:
                print(f"\n  ... [{remaining} more lines]")
            print("─" * 60)

        # Done
        print("\n  ✅ All done!")
        print("  📌 Next steps:")
        print("     1. Open the TXT file")
        print("     2. Copy all content")
        print("     3. Paste into ChatGPT / Claude / Gemini")
        print("     4. Add your request at the bottom")
        print("     5. Get AI-powered analysis or modifications!")
        print()

        # Cleanup token from memory
        self.client.clear_token()

    def _mode_public(self) -> Optional[Tuple[str, str]]:
        """Handle public repo analysis mode."""
        print("\n  📂 Analyze a public repository")
        print("  Enter repo URL or owner/repo format")
        print("  Examples: facebook/react, https://github.com/pallets/flask")

        url = self._input("\n  Repository")
        if not url:
            print("  ❌ Repository URL is required!")
            return None

        try:
            owner, repo_name = self.client.parse_repo_url(url)
            print(f"  ✅ Found: {owner}/{repo_name}")
            return owner, repo_name
        except ValueError as e:
            print(f"  ❌ {e}")
            return None

    def _mode_private(self) -> Optional[Tuple[str, str]]:
        """Handle private repo analysis mode."""
        print("\n  🔒 Analyze a private repository")
        print("  Get token from: https://github.com/settings/tokens")

        token = self.client.get_token_secure()
        if not token:
            print("  ❌ Token is required!")
            return None

        try:
            self.user_info = self.client.authenticate(token)
            self._show_user_info()
        except Exception as e:
            print(f"  ❌ Authentication failed: {e}")
            return None

        url = self._input("\n  Repository URL or owner/repo")
        if not url:
            print("  ❌ Repository URL is required!")
            return None

        try:
            owner, repo_name = self.client.parse_repo_url(url)
            print(f"  ✅ Found: {owner}/{repo_name}")
            return owner, repo_name
        except ValueError as e:
            print(f"  ❌ {e}")
            return None

    def _mode_browse(self) -> Optional[Tuple[str, str]]:
        """Handle browse repos mode."""
        print("\n  📋 Login & browse your repositories")
        print("  Get token from: https://github.com/settings/tokens")

        token = self.client.get_token_secure()
        if not token:
            print("  ❌ Token is required!")
            return None

        try:
            self.user_info = self.client.authenticate(token)
            self._show_user_info()
        except Exception as e:
            print(f"  ❌ Authentication failed: {e}")
            return None

        # Show rate limit
        rate = self.client.get_rate_limit()
        print(f"  📊 API Rate: {rate['remaining']}/{rate['limit']} requests remaining")

        # Fetch repos
        print("\n  📥 Fetching your repositories...")
        try:
            repos = self.client.get_user_repos()
        except Exception as e:
            print(f"  ❌ Failed to fetch repos: {e}")
            return None

        if not repos:
            print("  ❌ No repositories found!")
            return None

        return self._select_repo(repos)

    def _show_user_info(self):
        """Display authenticated user information."""
        info = self.user_info
        if not info:
            return

        print(f"\n  ✅ Authenticated!")
        print(f"  👤 User    : {info['username']}")
        print(f"  📛 Name    : {info['name']}")
        print(f"  📧 Email   : {info['email']}")
        print(f"  📦 Repos   : {info['public_repos']} public + {info['private_repos']} private = {info['total_repos']} total")
        print(f"  👥 Social  : {info['followers']} followers | {info['following']} following")
        print(f"  💼 Plan    : {info['plan']}")

    def _select_branch(self, owner: str, repo_name: str) -> Optional[str]:
        """Let user select a branch to analyze."""
        try:
            branches = self.client.get_repo_branches(owner, repo_name)
            if not branches or len(branches) <= 1:
                return None

            print(f"\n  🌿 Available branches ({len(branches)}):")
            for idx, branch_name in enumerate(branches, 1):
                print(f"     {idx}. {branch_name}")

            choice = self._input("  Select branch # (Enter = default)", "")

            if choice.isdigit():
                idx = int(choice)
                if 1 <= idx <= len(branches):
                    selected = branches[idx - 1]
                    print(f"  ✅ Selected branch: {selected}")
                    return selected

            return None

        except Exception as e:
            logger.warning(f"Could not fetch branches: {e}")
            return None

    def _select_repo(self, repos: List[Dict]) -> Optional[Tuple[str, str]]:
        """Interactive repo selection with filtering and pagination."""
        public_repos = [r for r in repos if not r["private"]]
        private_repos = [r for r in repos if r["private"]]

        print(f"\n  📊 Total: {len(repos)} repos ({len(public_repos)} public, {len(private_repos)} private)")

        # Filter options
        self._print_menu("Filter Repositories", [
            f"📋 All ({len(repos)})",
            f"🌐 Public only ({len(public_repos)})",
            f"🔒 Private only ({len(private_repos)})",
            "🔍 Search by name",
        ])

        filter_choice = self._input("Choice", "1")

        if filter_choice == "2":
            display_repos = public_repos
        elif filter_choice == "3":
            display_repos = private_repos
        elif filter_choice == "4":
            search_term = self._input("  Search term").lower()
            display_repos = [
                r for r in repos
                if search_term in r["name"].lower()
                or search_term in (r.get("description") or "").lower()
            ]
            if not display_repos:
                print(f"  ❌ No repos matching '{search_term}'")
                return None
            print(f"  🔍 Found {len(display_repos)} matching repos")
        else:
            display_repos = repos

        if not display_repos:
            print("  ❌ No repositories to show!")
            return None

        # Pagination
        page_size = 15
        total_pages = (len(display_repos) + page_size - 1) // page_size
        current_page = 0

        while True:
            start = current_page * page_size
            end = min(start + page_size, len(display_repos))

            print(f"\n  Page {current_page + 1}/{total_pages} (showing {start + 1}-{end} of {len(display_repos)})")
            print(f"  {'─' * 50}")

            for idx in range(start, end):
                repo = display_repos[idx]
                visibility = "🔒" if repo["private"] else "🌐"
                language = repo.get("language") or "---"
                stars = repo.get("stars", 0)
                description = (repo.get("description") or "No description")[:45]

                print(f"  {idx + 1:3d}. {visibility} {repo['name']}")
                print(f"       ⭐{stars} | {language} | {description}")

            print(f"  {'─' * 50}")

            # Navigation
            nav_options = []
            if current_page > 0:
                nav_options.append("p=prev")
            if current_page < total_pages - 1:
                nav_options.append("n=next")
            nav_options.extend(["[number]=select", "q=cancel"])
            print(f"  {' | '.join(nav_options)}")

            choice = self._input("  Choice")

            if choice.lower() == "n" and current_page < total_pages - 1:
                current_page += 1
            elif choice.lower() == "p" and current_page > 0:
                current_page -= 1
            elif choice.lower() == "q":
                return None
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(display_repos):
                    selected = display_repos[idx]
                    print(f"\n  📦 Selected: {selected['name']}")
                    print(f"     {selected.get('description', 'No description')}")
                    print(f"     {selected['html_url']}")

                    if self._input("  Confirm? (y/n)", "y").lower() == "y":
                        parts = selected["full_name"].split("/")
                        return parts[0], selected["name"]
                else:
                    print("  ❌ Invalid number!")
            else:
                print("  ❌ Invalid input!")

        return None
