import os, sys
from .github_client import GitHubClient
from .repo_scanner import RepoScanner
from .report_generator import ReportGenerator
from .file_exporter import FileExporter

class RepoAnalyzerApp:
    def __init__(self):
        self.client = GitHubClient()
        self.scanner = RepoScanner(self.client)
        self.generator = ReportGenerator()
        self.exporter = FileExporter()
        self.user_info = None
        try:
            import google.colab
            self.is_colab = True
        except ImportError:
            self.is_colab = False

    def _inp(self, prompt, default=None):
        if default:
            r = input(f'{prompt} [{default}]: ').strip()
            return r if r else default
        return input(f'{prompt}: ').strip()

    def _menu(self, title, opts):
        print(f'\n{chr(9472)*55}')
        print(f'  {title}')
        print(f'{chr(9472)*55}')
        for i, o in enumerate(opts, 1): print(f'  {i}. {o}')
        print(f'{chr(9472)*55}')

    def run(self):
        print('\n' + '='*56)
        print('  GitHub Repository Analyzer v1.0.0')
        print('  Analyze repos + generate AI-ready reports')
        print('  Works on: Google Colab | Kaggle | Terminal')
        print('='*56)

        self._menu('Choose Mode', ['Public repo (no token)','Private repo (token needed)','Login + browse my repos'])
        mode = self._inp('\nChoice (1/2/3)', '1')
        owner = repo_name = None

        if mode == '1':
            print('\nEnter public repo URL (e.g. user/repo):')
            url = self._inp('URL')
            if not url: print('URL required!'); return
            try: owner, repo_name = self.client.parse_repo_url(url); print(f'Found: {owner}/{repo_name}')
            except ValueError as e: print(e); return

        elif mode == '2':
            print('\nToken from: https://github.com/settings/tokens')
            token = self._inp('Token')
            if not token: print('Required!'); return
            try: self.user_info = self.client.authenticate(token); self._show_user()
            except Exception as e: print(e); return
            url = self._inp('Repo URL')
            if not url: print('Required!'); return
            try: owner, repo_name = self.client.parse_repo_url(url); print(f'Found: {owner}/{repo_name}')
            except ValueError as e: print(e); return

        elif mode == '3':
            token = self._inp('Token')
            if not token: print('Required!'); return
            try: self.user_info = self.client.authenticate(token); self._show_user()
            except Exception as e: print(e); return
            scopes = self.client.get_token_scopes()
            if scopes: print(f'Scopes: {chr(44).join(scopes)}')
            rl = self.client.get_rate_limit()
            print(f'Rate: {rl["remaining"]}/{rl["limit"]}')
            print('\nFetching repos...')
            try: repos = self.client.get_user_repos()
            except Exception as e: print(e); return
            if not repos: print('No repos!'); return
            result = self._select_repo(repos)
            if not result: return
            owner, repo_name = result
        else: print('Invalid!'); return

        branch = None
        try:
            branches = self.client.get_repo_branches(owner, repo_name)
            if branches and len(branches) > 1:
                print('\nBranches:')
                for i, b in enumerate(branches, 1): print(f'  {i}. {b}')
                bc = self._inp('Branch # (Enter=default)', '')
                if bc.isdigit() and 1 <= int(bc) <= len(branches): branch = branches[int(bc)-1]
        except: pass

        inc_c = self._inp('Include file contents? (y/n)', 'y').lower() == 'y'
        inc_s = self._inp('Include statistics? (y/n)', 'y').lower() == 'y'
        inc_cm = self._inp('Include commits? (y/n)', 'y').lower() == 'y'
        inc_ct = self._inp('Include contributors? (y/n)', 'y').lower() == 'y'
        mk = self._inp('Max file size KB', '500')
        try: ms = int(mk) * 1024
        except: ms = 500*1024

        try: scan = self.scanner.scan_repository(owner, repo_name, branch, inc_c, ms)
        except Exception as e: print(f'Error: {e}'); return

        report = self.generator.generate_report(scan, inc_c, inc_s, inc_cm, inc_ct)
        print(f'Report: {len(report):,} chars')

        self._menu('Export Format', ['TXT','PDF','Word','TXT+PDF','TXT+Word','PDF+Word','All','All+ZIP'])
        ch = self._inp('Choice', '1')
        fm = {'1':(['txt'],False),'2':(['pdf'],False),'3':(['word'],False),'4':(['txt','pdf'],False),'5':(['txt','word'],False),'6':(['pdf','word'],False),'7':(['txt','pdf','word'],False),'8':(['txt','pdf','word'],True)}
        fmts, dz = fm.get(ch, (['txt'], False))
        full = f'{owner}_{repo_name}'
        exported = self.exporter.export_all(report, full, scan, fmts, dz)

        print('\nExported:')
        for fmt, path in exported.items():
            sz = os.path.getsize(path) if os.path.exists(path) else 0
            print(f'  {fmt.upper()}: {path} ({sz:,} bytes)')

        if self.is_colab:
            print('\nDownloading...')
            try:
                from google.colab import files
                for path in exported.values():
                    if os.path.exists(path): files.download(path)
            except Exception as e: print(f'Download err: {e}'); print(f'Files in: {self.exporter.output_dir}/')
        else: print(f'Files in: {self.exporter.output_dir}/')

        if self._inp('\nShow preview? (y/n)', 'n').lower() == 'y':
            for line in report.split(chr(10))[:60]: print(line)
            print(f'\n... [{len(report.split(chr(10)))-60} more lines]')
        print('\nDone!')

    def _show_user(self):
        i = self.user_info
        print(f'\n  User: {i["username"]} | Name: {i["name"]} | Email: {i["email"]}')
        print(f'  Repos: {i["public_repos"]} public + {i["private_repos"]} private = {i["total_repos"]} total')
        print(f'  Followers: {i["followers"]} | Following: {i["following"]} | Plan: {i["plan"]}')
        print(f'  2FA: {"Yes" if i["two_factor_authentication"] else "No"} | Profile: {i["html_url"]}')

    def _select_repo(self, repos):
        pub = [r for r in repos if not r['private']]
        priv = [r for r in repos if r['private']]
        print(f'\nRepos: {len(repos)} total ({len(pub)} public, {len(priv)} private)')
        self._menu('Filter', ['All','Public','Private','Search'])
        fc = self._inp('Choice', '1')
        if fc=='2': show = pub
        elif fc=='3': show = priv
        elif fc=='4':
            term = self._inp('Search').lower()
            show = [r for r in repos if term in r['name'].lower() or term in (r.get('description') or '').lower()]
        else: show = repos
        if not show: print('None found!'); return None
        ps = 15
        pages = (len(show)+ps-1)//ps
        pg = 0
        while True:
            s, e = pg*ps, min((pg+1)*ps, len(show))
            print(f'\nPage {pg+1}/{pages} ({s+1}-{e} of {len(show)})')
            print('-'*55)
            for i in range(s, e):
                r = show[i]
                vis = 'PRIV' if r['private'] else 'PUB '
                lang = r.get('language') or '---'
                desc = (r.get('description') or '')[:40]
                print(f'  {i+1:3d}. [{vis}] {r["name"]}')
                print(f'       Stars:{r.get("stars",0)} | {lang} | {desc}')
            print('-'*55)
            nav = []
            if pg > 0: nav.append('p=prev')
            if pg < pages-1: nav.append('n=next')
            nav.extend(['number=select','q=cancel'])
            print(f'  {" | ".join(nav)}')
            c = self._inp('Choice')
            if c.lower()=='n' and pg<pages-1: pg+=1
            elif c.lower()=='p' and pg>0: pg-=1
            elif c.lower()=='q': return None
            elif c.isdigit():
                idx = int(c)-1
                if 0<=idx<len(show):
                    sel = show[idx]
                    print(f'\nSelected: {sel["name"]}')
                    print(f'  {sel.get("description","")}')
                    print(f'  {sel["html_url"]}')
                    if self._inp('Confirm? (y/n)', 'y').lower()=='y':
                        return sel['full_name'].split('/')[0], sel['name']
                else: print('Invalid!')
            else: print('Invalid!')
        return None