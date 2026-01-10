import os
import re
import sys
import json
import time
import shutil
import zipfile
import subprocess
from dataclasses import dataclass
from pathlib import Path

import requests

APP_ID = "tweakmanager"
GITHUB_REPO = "saydut/program-and-tweak-manager-main"  # owner/repo
TEMP_ROOT = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "Saydut" / "Updates" / APP_ID

DEFAULT_TIMEOUT = 15
PROGRAMS_URL = "https://www.saydut.com/static/programs.json"


def _normalize_version(v: str) -> str:
    v = (v or "").strip()
    if v.lower().startswith("v"):
        v = v[1:]
    return v


def version_tuple(v: str):
    v = _normalize_version(v)
    parts = re.split(r"[.\-+_]", v)
    out = []
    for p in parts:
        if p.isdigit():
            out.append(int(p))
        else:
            # non-numeric suffix: ignore for ordering in our simple scheme
            break
    while len(out) < 3:
        out.append(0)
    return tuple(out[:3])


def is_newer(latest: str, current: str) -> bool:
    return version_tuple(latest) > version_tuple(current)


def read_local_version(install_dir: Path) -> str:
    # version.txt (portable standard)
    vt = install_dir / "version.txt"
    if vt.exists():
        try:
            return vt.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    # fallback: config.json version
    cfg = install_dir / "config.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            return str(data.get("version", "0.0.0")).strip()
        except Exception:
            pass
    return "0.0.0"


@dataclass
class ReleaseInfo:
    tag: str
    name: str
    body: str
    zip_name: str
    zip_url: str


def fetch_latest_release() -> ReleaseInfo:
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    r = requests.get(url, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    j = r.json()
    tag = j.get("tag_name") or ""
    name = j.get("name") or tag
    body = j.get("body") or ""
    assets = j.get("assets") or []

    # pick first zip asset
    zip_asset = None
    for a in assets:
        n = (a.get("name") or "").lower()
        if n.endswith(".zip"):
            zip_asset = a
            break
    if not zip_asset:
        raise RuntimeError("Release asset (.zip) bulunamadı.")

    return ReleaseInfo(
        tag=tag,
        name=name,
        body=body,
        zip_name=zip_asset.get("name") or "update.zip",
        zip_url=zip_asset.get("browser_download_url") or "",
    )


def fetch_programs_manifest() -> dict:
    r = requests.get(PROGRAMS_URL, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    return r.json()


def read_program_version(payload: dict, program_id: str) -> str:
    for item in payload.get("programs", []):
        if item.get("id") == program_id:
            return str(item.get("version", "")).strip()
    return ""


def download_file(url: str, dest: Path, progress_cb=None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=DEFAULT_TIMEOUT) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", "0") or "0")
        done = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue
                f.write(chunk)
                done += len(chunk)
                if progress_cb:
                    progress_cb(done, total)
    return dest


def run_updater(install_dir: Path, zip_path: Path, app_exe: str):
    """
    Calls updater.exe in install_dir, passing:
      --install-dir, --package, --app-exe
    """
    updater = install_dir / "updater.exe"
    if not updater.exists():
        raise RuntimeError("updater.exe bulunamadı. Release paketine updater.exe eklemelisin.")
    args = [
        str(updater),
        "--install-dir", str(install_dir),
        "--package", str(zip_path),
        "--app-exe", app_exe,
    ]
    # Start updater detached; app should exit after calling this.
    subprocess.Popen(args, cwd=str(install_dir), shell=False)
