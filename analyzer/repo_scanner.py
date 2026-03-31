import os
from typing import Dict, List
from .github_client import GitHubClient

class RepoScanner:
    CODE_EXT = {'.py','.js','.ts','.jsx','.tsx','.java','.c','.cpp','.h','.hpp','.cs','.go','.rs','.rb','.php','.swift','.kt','.scala','.r','.R','.lua','.sh','.bash','.zsh','.sql','.html','.htm','.css','.scss','.sass','.less','.xml','.json','.yaml','.yml','.toml','.ini','.cfg','.conf','.env','.md','.markdown','.rst','.txt','.csv','.gitignore','.dockerignore','.vue','.svelte','.graphql','.proto','.ipynb','.dart','.ex','.elm','.hs','.clj','.lock','.gradle','.tf','.cmake'}
    BIN_EXT = {'.png','.jpg','.jpeg','.gif','.bmp','.ico','.svg','.webp','.mp3','.mp4','.avi','.mov','.wav','.zip','.tar','.gz','.bz2','.7z','.rar','.pdf','.doc','.docx','.xls','.xlsx','.ppt','.pptx','.exe','.dll','.so','.bin','.ttf','.otf','.woff','.woff2','.pyc','.class','.o','.db','.sqlite','.pkl','.h5','.model','.weights','.pb','.onnx','.pt','.pth','.min.js','.min.css','.map'}
    SPECIAL = {'README.md','README','LICENSE','LICENSE.md','CHANGELOG.md','CONTRIBUTING.md','.gitignore','Dockerfile','docker-compose.yml','Makefile','requirements.txt','setup.py','setup.cfg','pyproject.toml','package.json','Gemfile','Cargo.toml','go.mod','pom.xml','build.gradle','tsconfig.json','.env.example','Procfile','vercel.json'}
    MAX_SIZE = 500 * 1024
    MAX_FILES = 500

    def __init__(self, client): self.client = client

    def is_text(self, path):
        fn = os.path.basename(path)
        if fn in self.SPECIAL: return True
        _, ext = os.path.splitext(path.lower())
        if ext in self.BIN_EXT: return False
        if ext in self.CODE_EXT: return True
        if not ext: return True
        return ext not in self.BIN_EXT

    def get_category(self, path):
        _, ext = os.path.splitext(path.lower())
        fn = os.path.basename(path).lower()
        cats = {'Python':{'.py'},'JavaScript':{'.js','.jsx','.mjs'},'TypeScript':{'.ts','.tsx'},'HTML':{'.html','.htm'},'CSS':{'.css','.scss','.sass','.less'},'Java':{'.java'},'C/C++':{'.c','.cpp','.h','.hpp'},'C#':{'.cs'},'Go':{'.go'},'Rust':{'.rs'},'Ruby':{'.rb'},'PHP':{'.php'},'Swift':{'.swift'},'Kotlin':{'.kt'},'Dart':{'.dart'},'Shell':{'.sh','.bash','.zsh'},'SQL':{'.sql'},'Markdown':{'.md'},'JSON':{'.json'},'YAML':{'.yaml','.yml'},'XML':{'.xml'},'TOML':{'.toml'},'Config':{'.ini','.cfg','.conf','.env'}}
        if fn.startswith('dockerfile'): return 'Docker'
        for cat, exts in cats.items():
            if ext in exts: return cat
        return 'Other'

    def scan_repository(self, owner, repo_name, branch=None, include_content=True, max_file_size=None):
        if max_file_size: self.MAX_SIZE = max_file_size
        print(f'\n{"="*50}')
        print(f'  Scanning: {owner}/{repo_name}')
        print(f'{"="*50}')
        print('  Fetching repo info...')
        repo_info = self.client.get_repo_info(owner, repo_name)
        print('  Fetching languages...')
        languages = self.client.get_repo_languages(owner, repo_name)
        print('  Fetching branches...')
        branches = self.client.get_repo_branches(owner, repo_name)
        print('  Fetching contributors...')
        contributors = self.client.get_repo_contributors(owner, repo_name)
        print('  Fetching commits...')
        commits = self.client.get_latest_commits(owner, repo_name)
        print('  Fetching file tree...')
        tree = self.client.get_repo_tree(owner, repo_name, branch)
        files = [f for f in tree if f['type']=='blob']
        dirs = [f for f in tree if f['type']=='tree']
        print('  Building structure...')
        tree_text = self._visual_tree(tree)
        contents, cats, bins, skipped = {}, {}, [], []
        if include_content:
            text_files = [f for f in files if self.is_text(f['path'])]
            if len(text_files) > self.MAX_FILES:
                print(f'  Limiting to {self.MAX_FILES} files')
                text_files = text_files[:self.MAX_FILES]
            total = len(text_files)
            print(f'  Reading {total} files...')
            for i, f in enumerate(text_files):
                path, size = f['path'], f.get('size',0)
                if (i+1) % 20 == 0 or i == total-1:
                    pct = int((i+1)/total*100)
                    print(f'    [{pct}%] ({i+1}/{total})')
                if size and size > self.MAX_SIZE:
                    skipped.append({'path':path,'reason':f'Too large ({size//1024}KB)','size':size})
                    continue
                c = self.client.get_file_content(owner, repo_name, path, branch)
                if c is not None:
                    if c.startswith('[Binary'): bins.append(path)
                    else:
                        contents[path] = c
                        cats[path] = self.get_category(path)
            for f in files:
                if not self.is_text(f['path']) and f['path'] not in bins: bins.append(f['path'])
        stats = self._stats(files, contents, cats, languages)
        print(f'\n  Scan complete! Files:{len(files)} Read:{len(contents)} Dirs:{len(dirs)} Binary:{len(bins)}')
        return {'repo_info':repo_info,'languages':languages,'branches':branches,'contributors':contributors,'latest_commits':commits,'directory_structure_text':tree_text,'total_files':len(files),'total_directories':len(dirs),'file_contents':contents,'file_categories':cats,'binary_files':bins,'skipped_files':skipped,'statistics':stats,'scan_branch':branch or repo_info.get('default_branch','main')}

    def _visual_tree(self, tree):
        lines = ['Project Root']
        t = {}
        for item in sorted(tree, key=lambda x: x['path']):
            parts = item['path'].split('/')
            cur = t
            for p in parts[:-1]:
                if p not in cur: cur[p] = {}
                cur = cur[p]
            leaf = parts[-1]
            if item['type'] == 'blob': cur[leaf] = None
            else:
                if leaf not in cur: cur[leaf] = {}
        def render(node, prefix=''):
            items = sorted(node.items(), key=lambda x: (x[1] is not None, x[0]))
            for i, (name, sub) in enumerate(items):
                last = (i == len(items)-1)
                conn = 'L__ ' if last else '|-- '
                ext_p = '    ' if last else '|   '
                if sub is None:
                    lines.append(f'{prefix}{conn}{name}')
                else:
                    lines.append(f'{prefix}{conn}{name}/')
                    render(sub, prefix + ext_p)
        render(t)
        return '\n'.join(lines)

    def _stats(self, files, contents, cats, langs):
        total_lines = 0
        lines_by_file = {}
        for p, c in contents.items():
            l = len(c.split('\n'))
            lines_by_file[p] = l
            total_lines += l
        cat_counts = {}
        for cat in cats.values(): cat_counts[cat] = cat_counts.get(cat, 0) + 1
        total_size = sum(f.get('size',0) for f in files)
        total_lang = sum(langs.values()) or 1
        lang_pct = {l: round(b/total_lang*100, 1) for l, b in sorted(langs.items(), key=lambda x: x[1], reverse=True)}
        largest = sorted([(f['path'],f.get('size',0)) for f in files], key=lambda x: x[1], reverse=True)[:10]
        def fmt(b):
            for u in ['B','KB','MB','GB']:
                if b < 1024: return f'{b:.1f} {u}' if u != 'B' else f'{int(b)} B'
                b /= 1024
            return f'{b:.1f} TB'
        return {'total_lines':total_lines,'total_size':total_size,'total_size_formatted':fmt(total_size),'lines_by_file':lines_by_file,'files_by_category':cat_counts,'language_percentages':lang_pct,'largest_files':[{'path':p,'size':s,'size_formatted':fmt(s)} for p,s in largest],'total_text_files':len(contents),'avg_lines_per_file':round(total_lines/max(len(contents),1),1)}