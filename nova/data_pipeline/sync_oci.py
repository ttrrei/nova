import os
from pathlib import Path
import requests

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


def download_oci_par_zip(par_url: str, output_filename: str, target_dir: str | Path = "data/raw_zips") -> Path:
    """Download a zip file from an OCI Pre-Authenticated Request (PAR) URL into the source folder.

    Args:
        par_url: The OCI PAR URL pointing to the zip file.
        output_filename: The local filename to save the downloaded zip as.
        target_dir: The directory where the zip file will be stored.

    Returns:
        Path object pointing to the downloaded zip file.
    """
    save_dir = ensure_raw_zips_dir(target_dir)
    file_path = save_dir / output_filename

    response = requests.get(par_url, stream=True, timeout=300)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return file_path


if __name__ == "__main__":
    # Example standalone execution or test setup
    dest = ensure_raw_zips_dir()
    print(f"Source folder ready at: {dest.resolve()}")
