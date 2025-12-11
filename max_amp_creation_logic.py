import pandas as pd
import librosa
import matplotlib.pyplot as plt
import numpy as np


def read_from_csv(csv_path: str) -> pd.DataFrame:
    """
    Загружает датафрейм из CSV, и берёт две последние колонки (пути)
    """
    try:
        df = pd.read_csv(csv_path)
        df = df.iloc[:, -3:]
        df["max_amp"] = 0.0
        return df
    except FileNotFoundError:
        print(f"Файл {csv_path} не найден")


def find_max_amplitude(filepath: str) -> float:
    """
    Возвращает максимальную по модулю амплитуду аудиофайла
    """
    data, sr = librosa.load(filepath, mono=True)
    return np.max(abs(data))


def create_max_amp(df: pd.DataFrame) -> pd.DataFrame:
    """
    Создаёт датафрейм, добавляет максимальную амплитуду и сортирует max_amp
    """
    for index, row in df.iterrows():
        filename = row["absolute_path"]
        max_amp = find_max_amplitude(filename)
        df.loc[index, "max_amp"] = max_amp
    df = df.sort_values("max_amp")
    df = df.reset_index(drop=True)
    return df


def sort_dataframe(df, column_name, ascending=True) -> pd.DataFrame:
    """
    Сортирует DataFrame по указанной колонке.
    """
    return df.sort_values(by=column_name, ascending=ascending)


def filter_dataframe(df: pd.DataFrame, val: float) -> pd.DataFrame:
    """
    Фильтрует DataFrame по заданному значению
    """
    filtered_df = df[df["max_amp"] >= val]
    return filtered_df


def create_chart(df: pd.DataFrame, output_path: str) -> None:
    """
    Построение графика для распределения
    """

    x = np.arange(len(df))
    y = df["max_amp"].values

    plt.figure(figsize=(12, 6))
    plt.plot(x, y, linewidth=2, color="blue", marker="o", markersize=4)

    plt.title("Максимальная амплитуда звука по файлам")
    plt.xlabel("Номер файла (отсортированный список)")
    plt.ylabel("Максимальная амплитуда")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_path}.png", dpi=300)
    print(f"График сохранен в {output_path}.png")
    plt.show()


def save_dataframe(df: pd.DataFrame, output_path: str) -> None:
    """
    Сохраняет датафрейм в csv файл
    """
    filename = output_path + ".csv"
    df.to_csv(filename)
    return