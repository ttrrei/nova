from pathlib import Path
from urllib.parse import urljoin

import requests
import yaml


def ensure_raw_zips_dir(dir_path: str | Path = "data/raw_zips") -> Path:
    """Ensure the source directory for storing downloaded OCI PAR objects exists.

    Args:
        dir_path: Path to the target directory.

    Returns:
        Path object pointing to the directory.
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sync_oci_par_recursive(par_url: str, target_dir: str | Path = "data/raw_zips") -> list[Path]:
    """Recursively list and download all objects from an OCI Pre-Authenticated Request (PAR) prefix URL.

    Args:
        par_url: The OCI PAR prefix URL pointing to the bucket/folder.
        target_dir: The local directory where files will be stored.

    Returns:
        List of Path objects pointing to the downloaded files.
    """
    save_dir = ensure_raw_zips_dir(target_dir)
    downloaded_files: list[Path] = []

    # Ensure PAR URL ends with '/' for proper base joining
    base_url = par_url if par_url.endswith("/") else f"{par_url}/"
    
    # OCI Object Storage PAR prefix listing endpoint query parameters
    # When using a bucket/prefix PAR, appending ?prefix= or querying the listing API returns objects.
    # Alternatively, if it's an object listing request:
    listing_url = f"{base_url}?fields=name"

    print(f"Fetching object list from OCI PAR: {listing_url}")
    
    try:
        response = requests.get(listing_url, timeout=60)
        response.raise_for_status()
        listing_data = response.json()
    except Exception as e:
        raise RuntimeError(
            f"Failed to list objects from OCI PAR URL. Ensure the PAR grants 'List Object' permissions. Error: {e}"
        ) from e

    objects = listing_data.get("objects", [])
    if not objects:
        print("No objects found under the specified PAR prefix.")
        return downloaded_files

    for obj in objects:
        object_name = obj.get("name")
        if not object_name or object_name.endswith("/"):
            continue  # Skip folder placeholder markers

        # Construct download URL for the specific object
        # OCI PAR object download URL format appends the object name to the PAR base
        obj_url = urljoin(base_url, object_name)
        local_file_path = save_dir / object_name

        # Ensure subdirectories exist
        local_file_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Downloading: {object_name} -> {local_file_path}")
        obj_response = requests.get(obj_url, stream=True, timeout=300)
        obj_response.raise_for_status()

        with open(local_file_path, "wb") as f:
            for chunk in obj_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        downloaded_files.append(local_file_path)

    print(f"Successfully downloaded {len(downloaded_files)} objects to {save_dir.resolve()}")
    return downloaded_files


def load_config(config_path: str | Path = "config/config.yml") -> dict:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary containing configuration parameters.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path.resolve()}")
    
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


if __name__ == "__main__":
    config = load_config()
    
    oci_config = config.get("oci", {})
    par_url = oci_config.get("par_url")

    if not par_url:
        raise ValueError("OCI PAR URL ('par_url') not found under 'oci' section in config/config.yml")

    sync_oci_par_recursive(par_url=par_url)
