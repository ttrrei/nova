from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml


def ensure_raw_zips_dir(dir_path: str | Path = "data/raw_zips") -> Path:
    """Ensure the source directory for storing downloaded OCI PAR zip files exists.

    Args:
        dir_path: Path to the target directory.

    Returns:
        Path object pointing to the directory.
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def download_oci_par_zip(par_url: str, target_dir: str | Path = "data/raw_zips") -> Path:
    """Download a zip file from an OCI Pre-Authenticated Request (PAR) URL into the source folder,
    extracting the filename directly from the URL or headers.

    Args:
        par_url: The OCI PAR URL pointing to the zip file.
        target_dir: The directory where the zip file will be stored.

    Returns:
        Path object pointing to the downloaded zip file.
    """
    save_dir = ensure_raw_zips_dir(target_dir)

    # Derive filename from the URL path or fallback to a default name
    parsed_url = urlparse(par_url)
    path_name = Path(parsed_url.path).name
    if not path_name or not path_name.endswith(".zip"):
        output_filename = "downloaded_data.zip"
    else:
        output_filename = path_name

    file_path = save_dir / output_filename

    print(f"Downloading from PAR: {par_url} -> {file_path}")
    response = requests.get(par_url, stream=True, timeout=300)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Successfully downloaded: {file_path}")
    return file_path


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

    download_oci_par_zip(par_url=par_url)
