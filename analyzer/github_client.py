import os, re, base64, requests
from typing import Optional, List, Dict, Tuple

class GitHubClient:
    def __init__(self):
        self.token = None
        self.username = None
        self.base_url = 'https://api.github.com'
        self.session = requests.Session()
        self.session.headers.update({'Accept':'application/vnd.github.v3+json','User-Agent':'RepoAnalyzer/1.0'})
        self.is_authenticated = False

    def authenticate(self, token):
        self.token = token
        self.session.headers.update({'Authorization': f'token {token}'})
        r = self.session.get(f'{self.base_url}/user')
        if r.status_code == 200:
            d = r.json()
            self.username = d.get('login')
            self.is_authenticated = True
            return {
                'username':d.get('login'),'name':d.get('name','N/A'),
                'email':d.get('email','N/A'),'bio':d.get('bio','N/A'),
                'company':d.get('company','N/A'),'location':d.get('location','N/A'),
                'public_repos':d.get('public_repos',0),
                'private_repos':d.get('total_private_repos',0),
                'total_repos':d.get('public_repos',0)+d.get('total_private_repos',0),
                'followers':d.get('followers',0),'following':d.get('following',0),
                'html_url':d.get('html_url',''),'avatar_url':d.get('avatar_url',''),
                'created_at':d.get('created_at',''),'disk_usage':d.get('disk_usage',0),
                'plan':d.get('plan',{}).get('name','free'),
                'two_factor_authentication':d.get('two_factor_authentication',False),
            }
        raise Exception(f'Auth failed ({r.status_code})')

    def get_token_scopes(self):
        r = self.session.get(f'{self.base_url}/user')
        if r.status_code == 200:
            s = r.headers.get('X-OAuth-Scopes','')
            return [x.strip() for x in s.split(',') if x.strip()]
        return []

    def get_rate_limit(self):
        r = self.session.get(f'{self.base_url}/rate_limit')
        if r.status_code == 200:
            c = r.json().get('rate',{})
            return {'limit':c.get('limit',0),'remaining':c.get('remaining',0)}
        return {'limit':60,'remaining':0}

    def get_user_repos(self, include_private=True, sort='updated'):
        if not self.is_authenticated: raise Exception('Must authenticate first!')
        repos, page = [], 1
        while True:
            r = self.session.get(f'{self.base_url}/user/repos',
                params={'sort':sort,'direction':'desc','per_page':100,'page':page,
                        'type':'all' if include_private else 'public'})
            if r.status_code != 200: raise Exception(f'Failed: {r.status_code}')
            data = r.json()
            if not data: break
            for rp in data:
                repos.append({
                    'name':rp.get('name'),'full_name':rp.get('full_name'),
                    'description':rp.get('description','No description'),
                    'private':rp.get('private',False),'html_url':rp.get('html_url'),
                    'language':rp.get('language','Unknown'),
                    'size':rp.get('size',0),'stars':rp.get('stargazers_count',0),
                    'forks':rp.get('forks_count',0),
                    'open_issues':rp.get('open_issues_count',0),
                    'default_branch':rp.get('default_branch','main'),
                    'created_at':rp.get('created_at',''),
                    'updated_at':rp.get('updated_at',''),
                    'topics':rp.get('topics',[]),
                    'license':(rp.get('license') or {}).get('name','None'),
                    'archived':rp.get('archived',False),'fork':rp.get('fork',False),
                })
            page += 1
            if len(data) < 100: break
        return repos

    def parse_repo_url(self, url):
        url = url.strip().rstrip('/')
        if url.endswith('.git'): url = url[:-4]
        for p in [r'github\.com/([^/]+)/([^/]+)', r'^([^/\s]+)/([^/\s]+)$']:
            m = re.search(p, url)
            if m: return m.group(1), m.group(2)
        raise ValueError(f'Invalid URL: {url}')

    def get_repo_info(self, owner, repo_name):
        r = self.session.get(f'{self.base_url}/repos/{owner}/{repo_name}')
        if r.status_code == 200:
            rp = r.json()
            return {
                'name':rp.get('name'),'full_name':rp.get('full_name'),
                'description':rp.get('description','No description'),
                'private':rp.get('private',False),'html_url':rp.get('html_url'),
                'language':rp.get('language','Unknown'),
                'size':rp.get('size',0),'stars':rp.get('stargazers_count',0),
                'forks':rp.get('forks_count',0),
                'open_issues':rp.get('open_issues_count',0),
                'default_branch':rp.get('default_branch','main'),
                'created_at':rp.get('created_at',''),
                'updated_at':rp.get('updated_at',''),
                'topics':rp.get('topics',[]),
                'license':(rp.get('license') or {}).get('name','None'),
                'subscribers_count':rp.get('subscribers_count',0),
                'owner':{'login':rp.get('owner',{}).get('login'),
                         'avatar_url':rp.get('owner',{}).get('avatar_url'),
                         'html_url':rp.get('owner',{}).get('html_url')},
            }
        elif r.status_code == 404: raise Exception(f'Not found: {owner}/{repo_name}')
        elif r.status_code == 403: raise Exception(f'Access denied: {owner}/{repo_name}')
        else: raise Exception(f'Error: {r.status_code}')

    def get_repo_tree(self, owner, repo_name, branch=None):
        if not branch:
            info = self.get_repo_info(owner, repo_name)
            branch = info['default_branch']
        r = self.session.get(f'{self.base_url}/repos/{owner}/{repo_name}/git/trees/{branch}',
                            params={'recursive':'1'})
        if r.status_code == 200:
            return [{'path':i.get('path'),'type':i.get('type'),
                     'size':i.get('size',0),'sha':i.get('sha')}
                    for i in r.json().get('tree',[])]
        raise Exception(f'Tree error: {r.status_code}')

    def get_file_content(self, owner, repo_name, file_path, branch=None):
        params = {'ref': branch} if branch else {}
        r = self.session.get(f'{self.base_url}/repos/{owner}/{repo_name}/contents/{file_path}',
                            params=params)
        if r.status_code == 200:
            d = r.json()
            if d.get('encoding') == 'base64':
                try: return base64.b64decode(d['content']).decode('utf-8')
                except: return f'[Binary file: {file_path}]'
            return d.get('content','')
        elif r.status_code == 404: return None
        return f'[Error: {r.status_code}]'

    def get_repo_languages(self, owner, repo_name):
        r = self.session.get(f'{self.base_url}/repos/{owner}/{repo_name}/languages')
        return r.json() if r.status_code == 200 else {}

    def get_repo_branches(self, owner, repo_name):
        r = self.session.get(f'{self.base_url}/repos/{owner}/{repo_name}/branches',params={'per_page':100})
        return [b['name'] for b in r.json()] if r.status_code == 200 else []

    def get_repo_contributors(self, owner, repo_name):
        r = self.session.get(f'{self.base_url}/repos/{owner}/{repo_name}/contributors',params={'per_page':30})
        if r.status_code == 200:
            return [{'login':c.get('login'),'contributions':c.get('contributions',0),
                     'html_url':c.get('html_url')} for c in r.json()]
        return []

    def get_latest_commits(self, owner, repo_name, count=10):
        r = self.session.get(f'{self.base_url}/repos/{owner}/{repo_name}/commits',params={'per_page':count})
        if r.status_code == 200:
            return [{'sha':c.get('sha','')[:7],
                     'message':c.get('commit',{}).get('message',''),
                     'author':c.get('commit',{}).get('author',{}).get('name',''),
                     'date':c.get('commit',{}).get('author',{}).get('date',''),
                     'html_url':c.get('html_url','')} for c in r.json()]
        return []