#!/usr/bin/env -S uv run --script

import platform
import plistlib
import shutil
import subprocess
import tomllib
from pathlib import Path

from dmgbuild import build_dmg

if platform.system() != "Darwin":
    raise RuntimeError("Deploying is only supported on macOS.")

ROOT = Path(__file__).parent.parent
DIST = ROOT / "dist"
APP = DIST / "FlipFlops.app"
PLIST = APP / "Contents/Info.plist"

with (ROOT / "pyproject.toml").open("rb") as file:
    VERSION = tomllib.load(file)["project"]["version"]

shutil.rmtree(DIST, ignore_errors=True)
subprocess.run(["uv", "run", "pyside6-project", "clean"])
subprocess.run(["uv", "run", "pyside6-project", "build"])
subprocess.run(["uv", "run", "pyside6-project", "deploy"])

with PLIST.open("rb") as file:
    info = plistlib.load(file)
    info["CFBundleDisplayName"] = "FlipFlops"
    info["CFBundleIdentifier"] = "com.hereiskevin.flipflops"
    info["CFBundleName"] = "FlipFlops"

with PLIST.open("wb") as file:
    plistlib.dump(info, file)

build_dmg(
    filename=str(DIST / f"flipflops-v{VERSION}.dmg"),
    volume_name="FlipFlops",
    settings={
        "files": [str(APP)],
        "symlinks": {"Applications": "/Applications/"},
        "window_rect": ((0, 100000), (380, 300)),
        "text_size": 14,
        "icon_size": 100,
        "icon_locations": {
            "FlipFlops.app": (100, 100),
            "Applications": (275, 100),
        },
    },
)
