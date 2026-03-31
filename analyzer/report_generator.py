import os
from datetime import datetime

class ReportGenerator:
    SEP = '=' * 80

    def generate_report(self, scan_data, include_file_contents=True, include_statistics=True, include_commits=True, include_contributors=True):
        parts = [self._header(scan_data), self._repo_info(scan_data)]
        if include_statistics: parts.append(self._statistics(scan_data))
        parts.append(self._tree(scan_data))
        parts.append(self._languages(scan_data))
        if include_contributors and scan_data.get('contributors'): parts.append(self._contributors(scan_data))
        if include_commits and scan_data.get('latest_commits'): parts.append(self._commits(scan_data))
        if include_file_contents and scan_data.get('file_contents'): parts.append(self._files(scan_data))
        if scan_data.get('binary_files'): parts.append(self._binaries(scan_data))
        if scan_data.get('skipped_files'): parts.append(self._skipped(scan_data))
        parts.append(self._footer(scan_data))
        parts.append(self._ai_prompt(scan_data))
        return '\n\n'.join(parts)

    def _header(self, d):
        i = d['repo_info']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.SEP}\nGITHUB REPOSITORY - COMPLETE ANALYSIS REPORT\nDate: {now}\nRepo: {i["full_name"]}\nURL: {i["html_url"]}\nBranch: {d.get("scan_branch","main")}\n{self.SEP}\nThis report contains complete project description and ALL source code.\nSend to AI (ChatGPT/Claude/Gemini) to request modifications.'

    def _repo_info(self, d):
        i = d['repo_info']
        vis = 'Private' if i.get('private') else 'Public'
        t = f'{self.SEP}\nREPOSITORY INFO\n{self.SEP}\nName: {i["name"]}\nFull: {i["full_name"]}\nDesc: {i.get("description","N/A")}\nVisibility: {vis}\nLanguage: {i.get("language","N/A")}\nStars: {i.get("stars",0)} | Forks: {i.get("forks",0)} | Issues: {i.get("open_issues",0)}\nLicense: {i.get("license","None")}\nBranch: {i.get("default_branch","main")}\nCreated: {i.get("created_at","N/A")}\nUpdated: {i.get("updated_at","N/A")}\nOwner: {i.get("owner",{}).get("login","N/A")}'
        if i.get('topics'): t += f'\nTopics: {chr(44).join(i["topics"])}'
        if d.get('branches'):
            t += f'\n\nBranches ({len(d["branches"])}):'
            for j, b in enumerate(d['branches'], 1):
                mk = ' (default)' if b == i.get('default_branch') else ''
                t += f'\n  {j}. {b}{mk}'
        return t

    def _statistics(self, d):
        s = d.get('statistics',{})
        t = f'{self.SEP}\nSTATISTICS\n{self.SEP}\nFiles: {d.get("total_files",0)}\nDirs: {d.get("total_directories",0)}\nAnalyzed: {s.get("total_text_files",0)}\nLines: {s.get("total_lines",0):,}\nSize: {s.get("total_size_formatted","N/A")}\nAvg Lines/File: {s.get("avg_lines_per_file",0)}'
        if s.get('files_by_category'):
            t += '\n\nBy Category:'
            for cat, cnt in sorted(s['files_by_category'].items(), key=lambda x: x[1], reverse=True):
                t += f'\n  {cat:20s}: {cnt:4d}'
        if s.get('largest_files'):
            t += '\n\nLargest:'
            for j, f in enumerate(s['largest_files'], 1):
                t += f'\n  {j}. {f["path"]:50s} ({f["size_formatted"]})'
        return t

    def _tree(self, d): return f'{self.SEP}\nPROJECT STRUCTURE\n{self.SEP}\n{d.get("directory_structure_text","N/A")}'

    def _languages(self, d):
        lp = d.get('statistics',{}).get('language_percentages',{})
        if not lp: return ''
        t = f'{self.SEP}\nLANGUAGES\n{self.SEP}'
        for lang, pct in lp.items(): t += f'\n  {lang:20s}: {pct:5.1f}%'
        return t

    def _contributors(self, d):
        t = f'{self.SEP}\nCONTRIBUTORS\n{self.SEP}'
        for j, c in enumerate(d.get('contributors',[]), 1): t += f'\n  {j}. {c["login"]} ({c["contributions"]} commits)'
        return t

    def _commits(self, d):
        t = f'{self.SEP}\nLATEST COMMITS\n{self.SEP}'
        for j, c in enumerate(d.get('latest_commits',[]), 1):
            msg = c['message'].split(chr(10))[0]
            t += f'\n  {j}. [{c["sha"]}] {msg}\n     By: {c["author"]} | {c["date"]}'
        return t

    def _files(self, d):
        contents = d.get('file_contents',{})
        cats = d.get('file_categories',{})
        t = f'{self.SEP}\nFILE CONTENTS ({len(contents)} files)\n{self.SEP}'
        by_dir = {}
        for p in sorted(contents.keys()):
            parts = p.rsplit('/', 1)
            dr = parts[0] if len(parts) > 1 else '(root)'
            by_dir.setdefault(dr, []).append(p)
        num = 0
        for dr in sorted(by_dir.keys()):
            t += f'\n\n--- Directory: {dr} ---'
            for p in by_dir[dr]:
                num += 1
                c = contents[p]
                cat = cats.get(p, 'Other')
                lines = len(c.split(chr(10)))
                lang = self._lang(p)
                t += f'\n\n{"="*60}\nFile #{num}: {p}\nCategory: {cat} | Lines: {lines}\n{"="*60}\n\n```{lang}\n{c}\n```'
        return t

    def _binaries(self, d):
        bins = d.get('binary_files',[])
        t = f'{self.SEP}\nBINARY FILES ({len(bins)})\n{self.SEP}'
        for j, p in enumerate(sorted(bins), 1): t += f'\n  {j}. {p}'
        return t

    def _skipped(self, d):
        t = f'{self.SEP}\nSKIPPED FILES\n{self.SEP}'
        for j, f in enumerate(d.get('skipped_files',[]), 1): t += f'\n  {j}. {f["path"]} - {f["reason"]}'
        return t

    def _footer(self, d):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.SEP}\nEND OF REPORT | Generated: {now}\nRepo: {d["repo_info"]["full_name"]}\n{self.SEP}'

    def _ai_prompt(self, d):
        i = d['repo_info']
        s = d.get('statistics',{})
        return f'{self.SEP}\nAI INSTRUCTIONS\n{self.SEP}\n\nProject: {i["full_name"]}\nDesc: {i.get("description","N/A")}\nLang: {i.get("language","N/A")}\nFiles: {d.get("total_files",0)}\nLines: {s.get("total_lines",0):,}\n\nAbove is the complete project with all source code.\nREQUESTED CHANGES: [Write what you want here]\n\n{self.SEP}'

    def _lang(self, path):
        _, ext = os.path.splitext(path.lower())
        fn = os.path.basename(path).lower()
        m = {'.py':'python','.js':'javascript','.ts':'typescript','.jsx':'jsx','.tsx':'tsx','.java':'java','.c':'c','.cpp':'cpp','.h':'c','.cs':'csharp','.go':'go','.rs':'rust','.rb':'ruby','.php':'php','.swift':'swift','.kt':'kotlin','.dart':'dart','.sh':'bash','.sql':'sql','.html':'html','.css':'css','.scss':'scss','.json':'json','.yaml':'yaml','.yml':'yaml','.toml':'toml','.xml':'xml','.md':'markdown','.txt':'text','.vue':'vue','.env':'bash','.gitignore':'gitignore','.ini':'ini'}
        if fn.startswith('dockerfile'): return 'dockerfile'
        if fn == 'makefile': return 'makefile'
        return m.get(ext, 'text')