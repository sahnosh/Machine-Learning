"""Download the small MovieLens dataset from its official publisher."""
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
import hashlib
import json

ROOT = Path(__file__).resolve().parent
URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"

def main():
    data = ROOT / "data"
    data.mkdir(exist_ok=True)
    archive = data / "ml-latest-small.zip"
    temporary = data / "download.part"
    with urlopen(URL, timeout=120) as response, temporary.open("wb") as target:
        while chunk := response.read(1024 * 1024):
            target.write(chunk)
    with ZipFile(temporary) as bundle:
        for name in ("movies.csv", "ratings.csv", "tags.csv", "links.csv", "README.txt"):
            (data / name).write_bytes(bundle.read("ml-latest-small/" + name))
    temporary.replace(archive)
    (data / "source.json").write_text(json.dumps({"url": URL, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}, indent=2))
    print("MovieLens downloaded to", data)

if __name__ == "__main__":
    main()
