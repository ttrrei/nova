import zipfile
from pathlib import Path


def ensure_dir(dir_path: str | Path) -> Path:
    """Ensure the target directory exists.

    Args:
        dir_path: Path to the target directory.

    Returns:
        Path object pointing to the directory.
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def extract_all_zips_to_csv(zips_dir: str | Path = "data/raw_zips", csv_dir: str | Path = "data/raw_csv") -> list[Path]:
    """Recursively find all zip files in zips_dir and extract all csv files into csv_dir.

    Args:
        zips_dir: Directory containing downloaded zip files and subfolders.
        csv_dir: Destination directory for extracted CSV files.

    Returns:
        List of Path objects pointing to extracted CSV files.
    """
    source_dir = ensure_dir(zips_dir)
    target_dir = ensure_dir(csv_dir)
    extracted_csvs: list[Path] = []

    zip_files = list(source_dir.rglob("*.zip"))
    if not zip_files:
        print(f"No zip files found in {source_dir.resolve()}")
        return extracted_csvs

    for zip_path in zip_files:
        print(f"Processing zip: {zip_path.relative_to(source_dir)}")
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                for member in zf.namelist():
                    # Skip directory entries
                    if member.endswith("/"):
                        continue

                    # Extract file
                    extracted_path = Path(zf.extract(member, target_dir))
                    
                    # If it's a csv, keep track of it
                    if extracted_path.suffix.lower() == ".csv":
                        extracted_csvs.append(extracted_path)
        except (zipfile.BadZipFile, OSError) as e:
            print(f"Error extracting {zip_path}: {e}")

    print(f"Successfully extracted {len(extracted_csvs)} CSV files into {target_dir.resolve()}")
    return extracted_csvs


if __name__ == "__main__":
    extract_all_zips_to_csv()
