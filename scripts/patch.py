import plistlib
from pathlib import Path

PLIST = Path(__file__).parent.parent / "dist/FlipFlops.app/Contents/Info.plist"


with PLIST.open("rb") as file:
    info = plistlib.load(file)
    info["CFBundleDisplayName"] = "FlipFlops"
    info["CFBundleIdentifier"] = "dev.hereiskevin.flipflops"
    info["CFBundleName"] = "FlipFlops"

with PLIST.open("wb") as file:
    plistlib.dump(info, file)
