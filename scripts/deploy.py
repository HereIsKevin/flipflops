#!/usr/bin/env -S uv run --script

import plistlib
import shutil
import subprocess
from pathlib import Path

DIST = Path(__file__).parent.parent / "dist"
PLIST = DIST / "FlipFlops.app/Contents/Info.plist"

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
