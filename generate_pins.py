"""
generate_pins.py
Reads GPS coordinates straight out of your photos' EXIF data and builds pins.js
for the RiverTrace map site.

Also automatically shrinks any photo that's too large (over ~3MB or wider/
taller than 2000px) before generating pins — this keeps every photo safely
under GitHub's 25MB upload limit and keeps the site fast to load. GPS and
date data are preserved, so this never affects where a pin ends up.

USAGE:
    1. Drop your geotagged photos into the images/ folder — either directly,
       or organized into subfolders (e.g. images/Canavati_a_Media_Luna/).
       Subfolders are searched too, so organize your photos however makes
       sense to you.
    2. (Optional) For each photo, add a same-named .txt file with a short caption,
       e.g. images/spot1.jpg + images/spot1.txt
    3. Run:  python3 generate_pins.py
    4. Open index.html to preview your map.

Requires only Pillow:  pip install Pillow --break-system-packages
"""

import os
import sys
import json
from PIL import Image, ExifTags

GPS_TAG_ID = next((k for k, v in ExifTags.TAGS.items() if v == "GPSInfo"), 0x8825)
GPS_TAGS = ExifTags.GPSTAGS

# Photos larger than this (in bytes) or wider/taller than this (in pixels)
# get automatically shrunk before pins are generated. This keeps every
# photo safely under GitHub's 25MB web-upload limit and keeps the site
# fast to load. 2000px and ~3MB is still plenty sharp for a photo popup.
MAX_DIMENSION = 2000
MAX_FILE_SIZE_BYTES = 3 * 1024 * 1024
JPEG_QUALITY = 82


def optimize_image(path):
    """
    Shrinks a photo in place if it's larger than necessary. Skips photos
    that are already small enough — safe to run every time. Preserves the
    original EXIF data (GPS, date, orientation) so pin extraction and the
    map keep working exactly the same after the resize.

    Returns (size_before, size_after) in bytes if it changed the file,
    or None if the photo was left untouched.
    """
    size_before = os.path.getsize(path)
    try:
        with Image.open(path) as img:
            width, height = img.size
            oversized_dims = max(width, height) > MAX_DIMENSION
            oversized_bytes = size_before > MAX_FILE_SIZE_BYTES
            if not oversized_dims and not oversized_bytes:
                return None

            exif_bytes = img.info.get("exif")

            if oversized_dims:
                scale = MAX_DIMENSION / max(width, height)
                new_size = (round(width * scale), round(height * scale))
                img = img.resize(new_size, Image.LANCZOS)

            save_kwargs = {"quality": JPEG_QUALITY, "optimize": True}
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes
            img.convert("RGB").save(path, "JPEG", **save_kwargs)
    except Exception:
        return None

    size_after = os.path.getsize(path)
    return size_before, size_after


def dms_to_decimal(dms, ref):
    degrees, minutes, seconds = dms
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def extract_gps(image_path):
    try:
        img = Image.open(image_path)
        exif = img.getexif()
        gps_ifd = exif.get_ifd(GPS_TAG_ID)
        if not gps_ifd:
            return None
        gps = {GPS_TAGS.get(k, k): v for k, v in gps_ifd.items()}
        if "GPSLatitude" not in gps or "GPSLongitude" not in gps:
            return None
        lat = dms_to_decimal(gps["GPSLatitude"], gps.get("GPSLatitudeRef", "N"))
        lng = dms_to_decimal(gps["GPSLongitude"], gps.get("GPSLongitudeRef", "E"))
        return round(lat, 6), round(lng, 6)
    except Exception:
        return None


def extract_date(image_path):
    try:
        img = Image.open(image_path)
        exif = img.getexif()
        # DateTimeOriginal lives in the nested "Exif" sub-IFD on most cameras/phones
        exif_sub_ifd = exif.get_ifd(0x8769)
        val = exif_sub_ifd.get(36867)  # DateTimeOriginal
        if val:
            return val
        val = exif.get(306)  # DateTime, top-level fallback
        if val:
            return val
    except Exception:
        pass
    return ""


def read_caption_and_status(caption_path):
    """
    Reads a caption .txt file. If its first line is exactly "CLEANED"
    (case-insensitive), the photo is marked as a cleanup, and the rest of
    the file becomes the caption. Otherwise the whole file is the caption
    and the photo is treated as a trash report.
    """
    if not os.path.exists(caption_path):
        return "", "reported"
    with open(caption_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if lines and lines[0].strip().upper() == "CLEANED":
        caption = "\n".join(lines[1:]).strip()
        return caption, "cleaned"
    return "\n".join(lines).strip(), "reported"


def find_photos(folder):
    """
    Finds every .jpg/.jpeg photo inside folder, including subfolders — so
    photos organized into folders like images/Canavati_a_Media_Luna/ are
    found too, not just ones directly inside images/.
    Returns a sorted list of (full_path, relative_path) tuples, where
    relative_path always uses forward slashes (/) regardless of OS, since
    it ends up in a URL on the website.
    """
    photos = []
    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for fname in sorted(files):
            if fname.lower().endswith((".jpg", ".jpeg")):
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, folder).replace(os.sep, "/")
                photos.append((full_path, rel_path))
    photos.sort(key=lambda pair: pair[1])
    return photos


def main(folder="images"):
    if not os.path.isdir(folder):
        print(f"❌ Couldn't find the '{folder}' folder. Create it and add photos first.")
        return

    pins = []
    skipped = []
    optimized = []

    for path, rel_path in find_photos(folder):
        result = optimize_image(path)
        if result:
            optimized.append((rel_path, *result))

        coords = extract_gps(path)
        if not coords:
            skipped.append(rel_path)
            continue
        lat, lng = coords
        caption_path = os.path.splitext(path)[0] + ".txt"
        caption, status = read_caption_and_status(caption_path)
        pins.append({
            "lat": lat,
            "lng": lng,
            "image": f"{folder}/{rel_path}",
            "caption": caption,
            "date": extract_date(path),
            "status": status,
        })

    with open("pins.js", "w", encoding="utf-8") as f:
        f.write(
            "// Auto-generated by generate_pins.py\n"
            "// Re-run the script any time you add new photos.\n"
            "// You can also hand-edit this file directly if you want to tweak a caption.\n"
            "const PINS = "
        )
        f.write(json.dumps(pins, indent=2, ensure_ascii=False))
        f.write(";\n")

    print(f"✅ Wrote {len(pins)} pin(s) to pins.js")
    cleaned_count = sum(1 for p in pins if p["status"] == "cleaned")
    if cleaned_count:
        print(f"   ({len(pins) - cleaned_count} still need cleanup, {cleaned_count} marked cleaned)")
    if optimized:
        saved_mb = sum(before - after for _, before, after in optimized) / (1024 * 1024)
        print(f"📦 Resized {len(optimized)} large photo(s) to keep them web-friendly (saved {saved_mb:.1f} MB total):")
        for fname, before, after in optimized:
            print(f"   - {fname}: {before / (1024*1024):.1f} MB → {after / (1024*1024):.1f} MB")
    if skipped:
        print(f"⚠️  Skipped {len(skipped)} photo(s) with no GPS data — make sure Location Services was on:")
        for s in skipped:
            print(f"   - {s}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "images")