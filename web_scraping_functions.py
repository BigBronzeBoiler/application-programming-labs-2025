import csv
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


class FileIterator:
    """
    Итерируемый класс: CSV или директория с .mp3.
    """
    def __init__(self, source: Path) -> None:

        if not isinstance(source, Path):
            raise TypeError("Source must be path")

        self.source = source
        self.file_paths: list[Path] = []
        self._index = 0

        if self.source.is_file() and self.source.suffix == ".csv":
            self._load_from_csv()
        elif self.source.is_dir():
            self._load_from_dir()
        else:
            raise ValueError(f"Source must be dir or csv file {self.source}")

    def _load_from_csv(self) -> None:
        with self.source.open('r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if 'absolute_path' in reader:
                self.file_paths.append(Path(row['absolute path']))
            elif 'relative_path' in reader:
                self.file_paths.append(Path(row['relative path']))
            elif 'filename' in reader:
                self.file_paths.append(Path(row['filename']))
        print(f"Loaded {len(self.file_paths)} path's from CSV file")

    def _load_from_dir(self) -> None:
        """Ищет .mp3 в папке."""
        for p in self.source.rglob("*.mp3"):
            if p.is_file():
                self.file_paths.append(p)

    def __iter__(self) -> "FileIterator":
        self._index = 0
        return self

    def __next__(self) -> Path:
        if self._index >= len(self.file_paths):
            raise StopIteration
        res = self.file_paths[self._index]
        self._index += 1
        return res


def build_url(search_sound: str) -> str:
    """
    Формирует URL для поиска звуков на сайте Mixkit.
    """
    return f"https://mixkit.co/free-sound-effects/{search_sound}/"


def fetch_html(url: str) -> BeautifulSoup:
    """
    Скачивает страницу и возвращает BeautifulSoup.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers)
    return BeautifulSoup(resp.text, "html.parser")


def get_duration(duration_str: str) -> int:
    """
    Преобразует строку формата 'минуты:секунды' в целое число секунд
    """
    duration = duration_str.split(":")
    return int(duration[-1]) + int(duration[-2])*60
    

def extract_audio_urls(soup: BeautifulSoup, selector: str) -> list[str]:
    """
    Извлекает из HTML ссылки на MP3 дольше 10 секунд.
    """
    urls = []
    for div in soup.find_all("div", class_="item-grid-card item-grid-card--show-meta"):
        print(type(div))
        div_link = div.find_all("div", attrs={selector: True})[0]
        link = div_link.get(selector)
        duration_str = re.findall(r'(\d+:\d{1,2})', div.text)[0]
        duration = get_duration(duration_str)
        if (link and duration>10):
            urls.append(link)
    return urls


def write_csv_annotation(
    files: list[Path], csv_path: Path, base_dir: Path
) -> None:
    """
    Создаёт CSV с колонками filename, absolute_path, relative_path.
    """
    if csv_path.suffix != ".csv":
        csv_path = csv_path.with_suffix(".csv")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "absolute_path", "relative_path"])
        for p in files:
            abs_p = p.resolve()
            try:
                rel_p = abs_p.relative_to(base_dir.resolve())
            except ValueError:
                rel_p = Path(p.name)
            writer.writerow([p.name, str(abs_p), str(rel_p)])
    

def download_mp3(url: str, selector: str, out_dir: Path) -> list[Path]:
    """
    Cкачивает mp3 и возвращает список файлов.
    """
    soup = fetch_html(url)
    urls = extract_audio_urls(soup, selector)
    if not urls:
        raise RuntimeError("Не найдено MP3")

    out_dir.mkdir(exist_ok=True)
    files = []
    for audio_url in urls:
        filename = Path(audio_url).name
        audio_file = out_dir / filename
        resp = requests.get(audio_url)
        with audio_file.open("wb") as f:
            f.write(resp.content)
        files.append(audio_file)
    return files