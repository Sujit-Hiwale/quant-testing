import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    os.path.join(ROOT, "app", "main.py"),
])
