import argparse

from max_amp_creation_logic import (
    read_from_csv,
    create_max_amp,
    filter_dataframe,
    save_dataframe,
    create_chart,

)

def parse_args() -> argparse.ArgumentParser:
    """
    Парсим аргументы для выполнения задания
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", type=str, help="Путь к файлу csv")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output",
        help="Название файла для датафрейма",
    )

    parser.add_argument(
        "-f",
        "--filter",
        type=float,
        default=0.0,
        help="Фильтрация по минимальной амплитуде"
    )

    return parser.parse_args()


def main():
    try:
        args = parse_args()

        df = read_from_csv(args.input)
        df = create_max_amp(df)
        filtered = filter_dataframe(df, args.filter)
        save_dataframe(filtered, args.output)
        create_chart(df, args.output)
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()