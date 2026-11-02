"""TreeRoute on Streamlit Community Cloud.

This folder holds no app code. On startup it installs TreeRoute from a private
GitHub repo using a read-only token kept in the app's secrets, then runs it.

Secrets (Streamlit Cloud -> your app -> Settings -> Secrets):
    GITHUB_TOKEN = "github_pat_..."              # read-only access to the private repo
    GITHUB_REPO = "faiza-mehram437/TreeRoute"
    GEMINI_API_KEY = "..."                         # free key from aistudio.google.com/apikey
"""

import importlib
import os
import subprocess
import sys
import tempfile

import streamlit as st

# TreeRoute reads its settings from environment variables, so copy the secrets there.
try:
    for key, value in st.secrets.items():
        if isinstance(value, str):
            os.environ.setdefault(key, value)
except FileNotFoundError:
    pass  # no secrets file: running locally with plain environment variables

data_dir = os.path.join(tempfile.gettempdir(), "treeroute")
os.environ.setdefault("TREEROUTE_CHROMA_DIR", os.path.join(data_dir, "chroma"))
os.environ.setdefault("TREEROUTE_LIBRARY_DIR", os.path.join(data_dir, "library"))


@st.cache_resource(show_spinner=False)
def install_treeroute() -> None:
    """Install the latest TreeRoute once per app start, so "Reboot app" picks up new code."""
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPO")
    # TREEROUTE_PIP_SPEC lets you test this launcher against a local copy of the code.
    spec = os.environ.get("TREEROUTE_PIP_SPEC")
    if not spec:
        if not (token and repo):
            raise RuntimeError("Set the GITHUB_TOKEN and GITHUB_REPO secrets.")
        spec = f"treeroute @ git+https://x-access-token:{token}@github.com/{repo}.git"
    # Dependencies come from requirements.txt; only TreeRoute itself is (re)installed here.
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "--force-reinstall", "--no-deps", spec],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Never print pip's output here: it contains the URL with the token.
        raise RuntimeError(
            "Could not install TreeRoute from GitHub. "
            "Check the GITHUB_TOKEN (not expired, read access) and GITHUB_REPO secrets."
        )
    importlib.invalidate_caches()


install_treeroute()

from treeroute.webapp import main  # noqa: E402  (importable only after the install above)

main()
