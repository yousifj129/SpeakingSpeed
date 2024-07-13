import sys
import os
import math
import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                               QWidget, QLabel, QFileDialog, QProgressBar, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

class WaveformWidget(FigureCanvas):
    def __init__(self, parent=None, width=5, height=2, dpi=100):
        plt.style.use('dark_background')
        self.fig, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.fig.patch.set_facecolor('#2B2B2B')
        self.axes.set_facecolor('#2B2B2B')
        # Remove all spines, ticks, and labels
        self.axes.set_frame_on(False)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)

    def plot_waveform(self, audio_file):
        self.axes.clear()
        audio = AudioSegment.from_file(audio_file)
        samples = np.array(audio.get_array_of_samples())
        time = np.linspace(0, len(samples) / audio.frame_rate, num=len(samples))
        
        # Plot the waveform
        self.axes.plot(time, samples, linewidth=0.5, color='cyan')
        
        # Remove all margins
        self.fig.tight_layout(pad=0)
        self.axes.margins(0)
        
        # Set the background color
        self.fig.patch.set_facecolor('#2B2B2B')
        self.axes.set_facecolor('#2B2B2B')
        
        self.draw()

class AudioProcessorThread(QThread):
    update_progress = Signal(int)
    finished = Signal(dict)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file

    def run(self):
        try:
            wpm, word_count, duration = self.calculate_wpm(self.audio_file)
            self.finished.emit({"wpm": wpm, "word_count": word_count, "duration": duration})
        except Exception as e:
            self.finished.emit({"error": str(e)})

    def convert_to_wav(self, input_file):
        self.update_progress.emit(10)
        file_name, file_extension = os.path.splitext(input_file)
        output_file = f"{file_name}_temp.wav"
        
        if file_extension.lower() in ['.mp3', '.m4a']:
            audio = AudioSegment.from_file(input_file, format=file_extension[1:])
            audio.export(output_file, format="wav")
            return output_file
        elif file_extension.lower() == '.wav':
            return input_file
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def calculate_wpm(self, audio_file_path):
        wav_file = self.convert_to_wav(audio_file_path)
        self.update_progress.emit(30)

        recognizer = sr.Recognizer()
        audio = AudioSegment.from_wav(wav_file)
        duration_seconds = len(audio) / 1000

        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            self.update_progress.emit(50)
            text = recognizer.recognize_google(audio_data)

        self.update_progress.emit(80)
        word_count = len(text.split())
        wpm = math.ceil((word_count / duration_seconds) * 60)

        if wav_file != audio_file_path:
            os.remove(wav_file)

        self.update_progress.emit(100)
        return wpm, word_count, duration_seconds
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speaking Speed")
        self.setGeometry(100, 100, 600, 400)

        self.setup_dark_theme()

        main_layout = QVBoxLayout()

        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.select_button = QPushButton("Select Audio File")
        self.select_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.select_button)

        self.waveform_widget = WaveformWidget(self, width=5, height=2)

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.analyze_audio)
        self.analyze_button.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)

        self.result_label = QLabel("fkkkkkk")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 12))

        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.waveform_widget)
        main_layout.addWidget(self.analyze_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.result_label)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.loading_animation_timer = QTimer()
        self.loading_animation_timer.startTimer(100)
        self.loading_animation_timer.timeout.connect(self.update_loading_animation)
        self.loading_animation_frame = 0

    def setup_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_palette)

    # ... (keep the existing methods unchanged)
    def select_file(self):
        file_dialog = QFileDialog()
        self.audio_file, _ = file_dialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.wav *.mp3 *.m4a)")
        if self.audio_file:
            self.file_label.setText(os.path.basename(self.audio_file))
            self.analyze_button.setEnabled(True)
            self.waveform_widget.plot_waveform(self.audio_file)

    def analyze_audio(self):
        self.progress_bar.setValue(0)
        self.result_label.setText("Analyzing...")
        self.analyze_button.setEnabled(False)
        self.select_button.setEnabled(False)

        self.loading_animation_timer.start(100)  # Start the loading animation

        self.audio_thread = AudioProcessorThread(self.audio_file)
        self.audio_thread.update_progress.connect(self.update_progress)
        self.audio_thread.finished.connect(self.display_result)
        self.audio_thread.start()
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_result(self, result):
        self.analyze_button.setEnabled(True)
        self.select_button.setEnabled(True)
        self.loading_animation_timer.stop()  # Stop the loading animation

        if "error" in result:
            self.result_label.setText(f"Error: {result['error']}")
        else:
            wpm = result["wpm"]
            word_count = result["word_count"]
            duration = result["duration"]
            self.result_label.setText(f"Words per minute: {wpm}\nTotal words: {word_count}\nAudio duration: {duration:.2f} seconds")

    def update_loading_animation(self):
        animation_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading_animation_frame = (self.loading_animation_frame + 1) % len(animation_frames)
        self.result_label.setText(f"Fetching from Google API {animation_frames[self.loading_animation_frame]}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())