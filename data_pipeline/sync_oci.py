from pathlib import Path
from urllib.parse import urljoin
import zipfile

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


def ensure_raw_csv_dir(dir_path: str | Path = "data/raw_csv") -> Path:
    """Ensure the target directory for storing extracted raw CSV files exists.

    Args:
        dir_path: Path to the target directory.

    Returns:
        Path object pointing to the directory.
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def extract_zips_to_raw_csv(zips_dir: str | Path = "data/raw_zips", csv_dir: str | Path = "data/raw_csv") -> list[Path]:
    """Recursively find all zip files in zips_dir and extract their contents into csv_dir.

    Args:
        zips_dir: Directory containing downloaded zip files.
        csv_dir: Destination directory for extracted CSV files.

    Returns:
        List of Path objects pointing to extracted files.
    """
    source_dir = ensure_raw_zips_dir(zips_dir)
    target_dir = ensure_raw_csv_dir(csv_dir)
    extracted_files: list[Path] = []

    zip_files = list(source_dir.rglob("*.zip"))
    if not zip_files:
        print(f"No zip files found in {source_dir.resolve()}")
        return extracted_files

    for zip_path in zip_files:
        print(f"Extracting {zip_path.name} to {target_dir.resolve()}")
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for member in zf.namelist():
                    # Extract only files (skip directories)
                    if member.endswith("/"):
                        continue
                    
                    extracted_path = zf.extract(member, target_dir)
                    extracted_files.append(Path(extracted_path))
        except Exception as e:
            print(f"Error extracting {zip_path}: {e}")

    print(f"Successfully extracted {len(extracted_files)} files into {target_dir.resolve()}")
    return extracted_files


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
    
    # Automatically trigger extraction to raw_csv after download
    extract_zips_to_raw_csv()

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
