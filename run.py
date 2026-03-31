#!/usr/bin/env python3
import subprocess, sys, os

def install():
    pkgs = ['PyGithub','python-docx','fpdf2','requests','rich','ipywidgets']
    for p in pkgs:
        try: __import__(p.replace('-','_').lower())
        except ImportError:
            print(f'  Installing {p}...')
            subprocess.check_call([sys.executable,'-m','pip','install','-q',p],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == '__main__':
    print('\n📦 Checking dependencies...')
    install()
    print('✅ Ready!\n')
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from analyzer.main import RepoAnalyzerApp
    RepoAnalyzerApp().run()
