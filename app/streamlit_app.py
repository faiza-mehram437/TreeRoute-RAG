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
import re
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


class InstallError(Exception):
    """Installing TreeRoute failed; the message is safe to show (no token in it)."""


def hide_token(text: str) -> str:
    return re.sub(r"x-access-token:[^@\s]+@", "x-access-token:***@", text)


@st.cache_resource(show_spinner=False)
def install_treeroute() -> None:
    """Install the latest TreeRoute once per app start, so "Reboot app" picks up new code.

    Failures raise instead of returning, so they are not cached and the next run retries.
    """
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPO")
    # TREEROUTE_PIP_SPEC lets you test this launcher against a local copy of the code.
    spec = os.environ.get("TREEROUTE_PIP_SPEC")
    if not spec:
        if not (token and repo):
            raise InstallError("The GITHUB_TOKEN and GITHUB_REPO secrets are not set.")
        spec = f"treeroute @ git+https://x-access-token:{token}@github.com/{repo}.git"
    # Dependencies come from requirements.txt; only TreeRoute itself is (re)installed here.
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "--force-reinstall", "--no-deps", spec],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        output = hide_token((result.stderr or "") + (result.stdout or "")).strip()
        raise InstallError(output[-3000:] or f"pip exited with code {result.returncode}")
    importlib.invalidate_caches()


try:
    install_treeroute()
except InstallError as error:
    st.error(
        "Could not install TreeRoute from the private GitHub repo. Check that the "
        "GITHUB_TOKEN secret is valid with read access to that repo, that GITHUB_REPO "
        "is spelled correctly, and that the repo contains the code. Details:"
    )
    st.code(str(error), language=None)
    st.stop()

from treeroute.webapp import main  # noqa: E402  (importable only after the install above)

main()
