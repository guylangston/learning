#!/usr/bin/env python3
"""
find_near_reigate.py
--------------------
Scans a folder of images, extracts GPS EXIF data from each,
and lists all photos taken within a given radius of Reigate, UK.

Usage:
    python find_near_reigate.py [folder] [--radius KM] [--lat LAT] [--lon LON] [--recursive]

Examples:
    python find_near_reigate.py ~/Pictures
    python find_near_reigate.py ~/WhatsApp/Images --radius 10
    python find_near_reigate.py ~/Photos --lat 51.2362 --lon -0.2056 --radius 5
    python find_near_reigate.py . --recursive

Requirements:
    pip install Pillow
"""

import os
import sys
import math
import argparse
from pathlib import Path

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("❌  Pillow is required.  Run:  pip install Pillow")
    sys.exit(1)


# ── Defaults ───────────────────────────────────────────────────────────────────

REIGATE_LAT = 51.2362   # Reigate town centre, Surrey, UK
REIGATE_LON = -0.2056
DEFAULT_RADIUS_KM = 15.0

SUPPORTED = {".jpg", ".jpeg", ".tif", ".tiff", ".webp", ".png", ".heic"}


# ── GPS extraction ─────────────────────────────────────────────────────────────

def _to_decimal(dms, ref: str) -> float:
    """Convert a (degrees, minutes, seconds) tuple + hemisphere ref to decimal degrees."""
    d, m, s = [float(x) for x in dms]
    value = d + m / 60.0 + s / 3600.0
    return -value if ref in ("S", "W") else value


def extract_gps(path: Path):
    """
    Open an image and return (latitude, longitude) as floats,
    or None if no GPS EXIF data is present.
    """
    try:
        img = Image.open(path)
        raw_exif = img._getexif()
        if not raw_exif:
            return None

        exif = {TAGS.get(tag, tag): val for tag, val in raw_exif.items()}
        gps_raw = exif.get("GPSInfo")
        if not gps_raw:
            return None

        gps = {GPSTAGS.get(tag, tag): val for tag, val in gps_raw.items()}

        lat_dms = gps.get("GPSLatitude")
        lat_ref = gps.get("GPSLatitudeRef", "N")
        lon_dms = gps.get("GPSLongitude")
        lon_ref = gps.get("GPSLongitudeRef", "E")

        if not (lat_dms and lon_dms):
            return None

        return _to_decimal(lat_dms, lat_ref), _to_decimal(lon_dms, lon_ref)

    except Exception:
        return None


# ── Distance ───────────────────────────────────────────────────────────────────

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi    = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Scan ───────────────────────────────────────────────────────────────────────

def scan_folder(folder: Path, centre_lat: float, centre_lon: float,
                radius_km: float, recursive: bool):
    """Walk the folder, extract GPS, and return (nearby, total, no_gps_count)."""
    nearby = []
    total  = 0
    no_gps = 0

    glob = folder.rglob("*") if recursive else folder.glob("*")

    for path in sorted(glob):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue

        total += 1
        coords = extract_gps(path)

        if coords is None:
            no_gps += 1
            continue

        lat, lon = coords
        dist = haversine_km(lat, lon, centre_lat, centre_lon)

        if dist <= radius_km:
            nearby.append({"path": path, "lat": lat, "lon": lon, "dist": dist})

    nearby.sort(key=lambda x: x["dist"])
    return nearby, total, no_gps


# ── Display ────────────────────────────────────────────────────────────────────

def print_results(nearby, total, no_gps, centre_lat, centre_lon,
                  radius_km, folder, centre_name):
    width = 72
    sep   = "─" * width

    print()
    print("┌" + "─" * (width - 2) + "┐")
    print(f"│{'📍  GPS Photo Finder':^{width - 2}}│")
    print("└" + "─" * (width - 2) + "┘")
    print()
    print(f"  Folder   : {folder}")
    print(f"  Centre   : {centre_name}  ({centre_lat:.4f}, {centre_lon:.4f})")
    print(f"  Radius   : {radius_km} km")
    print(f"  Scanned  : {total} image(s)   |   No GPS: {no_gps}   |   Has GPS: {total - no_gps}")
    print()

    if not nearby:
        print(f"  ⚠️  No images found within {radius_km} km of {centre_name}.")
        print()
        return

    print(f"  ✅  {len(nearby)} image(s) within {radius_km} km of {centre_name}:\n")
    print(f"  {'#':<4}  {'Distance':>9}  {'Lat':>9}  {'Lon':>10}  File")
    print("  " + sep)

    for i, item in enumerate(nearby, 1):
        filename = item["path"].name
        if len(filename) > 38:
            filename = filename[:35] + "..."
        print(f"  {i:<4}  {item['dist']:>7.2f} km"
              f"  {item['lat']:>9.4f}  {item['lon']:>10.4f}  {filename}")

    print()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Find photos taken near Reigate, UK (or any custom location).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Folder to scan (default: current directory)",
    )
    parser.add_argument(
        "--radius", "-r",
        type=float,
        default=DEFAULT_RADIUS_KM,
        metavar="KM",
        help=f"Search radius in kilometres (default: {DEFAULT_RADIUS_KM})",
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=REIGATE_LAT,
        help=f"Centre latitude  (default: {REIGATE_LAT} — Reigate)",
    )
    parser.add_argument(
        "--lon",
        type=float,
        default=REIGATE_LON,
        help=f"Centre longitude (default: {REIGATE_LON} — Reigate)",
    )
    parser.add_argument(
        "--recursive", "-R",
        action="store_true",
        help="Search subfolders recursively",
    )

    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"❌  Folder not found: {folder}")
        sys.exit(1)

    centre_name = "Reigate, UK"
    if args.lat != REIGATE_LAT or args.lon != REIGATE_LON:
        centre_name = f"custom point ({args.lat:.4f}, {args.lon:.4f})"

    print(f"\n  Scanning {'recursively ' if args.recursive else ''}in: {folder} …", flush=True)

    nearby, total, no_gps = scan_folder(
        folder, args.lat, args.lon, args.radius, args.recursive
    )

    print_results(nearby, total, no_gps, args.lat, args.lon,
                  args.radius, folder, centre_name)


if __name__ == "__main__":
    main()
