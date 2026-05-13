"""Download GIF files from URLs."""
import sys
import urllib.request
import os

def download(url: str, output_path: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
        return os.path.getsize(output_path) > 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: download_gif.py <url> <output_path>")
        sys.exit(1)
    ok = download(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
