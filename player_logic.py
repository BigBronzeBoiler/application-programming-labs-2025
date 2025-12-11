import sys
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QLabel
)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.uic import loadUi

from main import FileIterator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("LargeBronzePlayer.ui", self)


        self.iterator: Optional[FileIterator] = None
        self.current_file: Optional[Path] = None

        self.player = QMediaPlayer(self)
        self.player.durationChanged.connect(self.update_duration)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.player.error.connect(self.on_player_error)

        self.filename_label: QLabel = self.Filename_label
        self.duration_label: QLabel = self.label_3

        self.AddAudio_button.clicked.connect(self.choose_source)
        self.Play_button.clicked.connect(self.toggle_play_pause)
        self.Pause_button.clicked.connect(self.pause)
        self.NextAudio_button.clicked.connect(self.next_audio)
        self.PrevAudio_button.clicked.connect(self.prev_audio)

        self.Pause_button.setVisible(False)

        self.history = []

    def choose_source(self):
        """
        Выбор CSV или папки с аудио
        """
        choice = QFileDialog.getExistingDirectory(self, "Выберите папку с аудиофайлами") \
                 or QFileDialog.getOpenFileName(self, "Выберите CSV-аннотацию", "", "CSV Files (*.csv)")[0]

        if not choice:
            return

        source_path = Path(choice)

        try:
            self.iterator = FileIterator(source_path)
            self.history = []
            self.next_audio()
            QMessageBox.information(self, "Успех", f"Загружено {len(self.iterator.file_paths)} аудиофайлов")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить датасет:\n{e}")

    def load_current_file(self):
        """
        Загружает текущий файл в плеер и обновляет интерфейс.
        """
        if not self.current_file or not self.current_file.exists():
            self.filename_label.setText("<b>Файл не найден</b>")
            self.duration_label.setText("Duration: --:--")
            return

        self.filename_label.setText(f"<b>{self.current_file.name}</b>")
        self.player.stop()

        url = QUrl.fromLocalFile(str(self.current_file.resolve()))
        self.player.setMedia(QMediaContent(url))

        self.duration_label.setText("Duration: загрузка...")

    def update_duration(self, duration_ms: int):
        """
        Обновляет отображение длительности в формате mm:ss.
        """
        if duration_ms <= 0:
            self.duration_label.setText("Duration: увы(")
            return
        minutes = duration_ms // 60000
        seconds = (duration_ms % 60000) // 1000
        self.duration_label.setText(f"Duration: {minutes:02d}:{seconds:02d}")

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.LoadedMedia:
            self.player.setPosition(0)

    def on_player_error(self, error):
        QMessageBox.warning(self, "Ошибка воспроизведения", f"Не удалось воспроизвести файл:\n{error}")

    def toggle_play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.pause()
        else:
            self.play()

    def play(self):
        if self.current_file:
            self.player.play()
            self.Play_button.setText("Stop")
            self.Pause_button.setVisible(True)

    def pause(self):
        self.player.pause()
        self.Play_button.setText("Play")
        self.Pause_button.setVisible(False)

    def stop_and_reset_buttons(self):
        self.player.stop()
        self.Play_button.setText("Play")
        self.Pause_button.setVisible(False)

    def next_audio(self):
        if not self.iterator:
            QMessageBox.warning(self, "Нет данных", "Сначала выберите источник аудиофайлов")
            return

        try:
            if self.current_file:
                self.history.append(self.current_file)
            self.current_file = next(self.iterator)
            self.load_current_file()
            self.stop_and_reset_buttons()
        except StopIteration:
            QMessageBox.information(self, "Стоять, бандит", "Ето последний аудиофайл в датасете")
            self.current_file = None
            self.filename_label.setText("<i>Конец датасета</i>")
            self.duration_label.setText("Duration: --:--")
            self.stop_and_reset_buttons()

    def prev_audio(self):
        if not self.history:
            QMessageBox.information(self, "Начало", "Ето первый трек")
            return
        self.current_file = self.history.pop()
        self.load_current_file()
        self.stop_and_reset_buttons()