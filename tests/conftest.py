import sys
import os

# Ensure repo root is first on sys.path so imports like 'import app' resolve to the
# repository 'app' package, not to any file named app.py inside subfolders (e.g. temp/lab3/app.py).
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)