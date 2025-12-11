import argparse
from pathlib import Path

from web_scraping_functions import (
    FileIterator,
    write_csv_annotation,
    download_mp3,
    build_url
)


def parse_args() -> argparse.Namespace:
    """
    Парсинг аргументов командной строки.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--out",
        dest="out_dir",
        type=str,
        default="task",
        help="path to output folder"
    )
    parser.add_argument(
        "search_sound",
        type=str,
        help="theme for searching sounds"
    )
    parser.add_argument(
        "-c", "--csv",
        dest="csv_file",
        type=str,
        default="annotation.csv",
        help="CSV annotation filename"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    csv_path = Path(args.csv_file)
    url = build_url(args.search_sound)

    # try:
        #files = download_mp3(url, "data-audio-player-preview-url-value", out_dir)
    iterator = FileIterator(out_dir)
    write_csv_annotation(list(iterator), csv_path, out_dir)

    for f in iterator:
        print(f)
    # except Exception as error:
    #     print(f"Ошибка: {error}")
        


if __name__ == "__main__":
    main()