import plistlib
from pathlib import Path

PLIST = Path(__file__).parent.parent / "dist/FlipFlops.app/Contents/Info.plist"


with open(PLIST, "rb") as file:
    info = plistlib.load(file)
    info["CFBundleDisplayName"] = "FlipFlops"
    info["CFBundleIdentifier"] = "dev.hereiskevin.flipflops"
    info["CFBundleName"] = "FlipFlops"

with open(PLIST, "wb") as file:
    plistlib.dump(info, file)
