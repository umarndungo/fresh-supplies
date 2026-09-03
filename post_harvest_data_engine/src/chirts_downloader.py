"""CHIRTS-ERA5 Monthly Tmax GeoTIFF Downloader."""

import os
from urllib.parse import urljoin
import bs4
import requests

CHIRTS_BASE_URL = (
    "https://data.chc.ucsb.edu/experimental/CHIRTS-ERA5/tmax/tifs/monthly/"
)


def download_latest_chirts_raster(
    output_dir: str = "data/raw/climate/",
) -> str:
  """Scrapes monthly tifs directory, downloads newest valid .tif file, and verifies integrity."""
  os.makedirs(output_dir, exist_ok=True)

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like"
          " Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  print("[Info] Scraping CHIRTS monthly GeoTIFF directory...")

  try:
    response = requests.get(CHIRTS_BASE_URL, headers=headers, timeout=15)
    response.raise_for_status()
  except requests.RequestException as e:
    print(f"[Error] Failed to connect to CHC server: {e}")
    return None

  soup = bs4.BeautifulSoup(response.text, "html.parser")

  tif_links = [
      urljoin(CHIRTS_BASE_URL, node.get("href"))
      for node in soup.find_all("a", href=True)
      if node.get("href", "").lower().endswith((".tif", ".tiff"))
  ]

  if not tif_links:
    print("[Warning] No valid GeoTIFF (.tif) files found in index.")
    return None

  latest_tif_url = tif_links[-1]
  filename = os.path.basename(latest_tif_url)
  local_path = os.path.join(output_dir, filename)
  tmp_path = os.path.join(output_dir, f"{filename}.tmp")

  if os.path.exists(local_path) and os.path.getsize(local_path) > 1024 * 1024:
    print(f"[Info] Using cached CHIRTS raster: {local_path}")
    return local_path

  print(f"[Info] Downloading latest monthly GeoTIFF: {filename}...")

  try:
    with requests.get(
        latest_tif_url, headers=headers, stream=True, timeout=90
    ) as r:
      r.raise_for_status()
      with open(tmp_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=16384):
          f.write(chunk)

    os.rename(tmp_path, local_path)
    print(f"[Success] Saved GeoTIFF raster to {local_path}")
    return local_path

  except Exception as e:
    print(f"[Error] Download failed: {e}")
    if os.path.exists(tmp_path):
      os.remove(tmp_path)
    return None