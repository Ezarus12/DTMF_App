import wave
import numpy
import sounddevice
from PyQt5.QtCore import QFile, Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QFileDialog, QMessageBox
from PyQt5.QtGui import QFont

from constants import DTMF_FREQUENCIES, SCREEN_HEIGHT, SCREEN_WIDTH


# Main DTMF Window for generating tones
class DtmfWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DTMF Generator")
        self.setGeometry(320, 180, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background:#252525")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Load stylesheet
        self.load_stylesheet()

        # Create the layout and widgets
        self.create_widgets()

    def load_stylesheet(self):
        """
        Load stylesheet
        
        """

        style_file = QFile("styles.css")
        if style_file.open(QFile.ReadOnly | QFile.Text):
            self.stylesheet = style_file.readAll()
            style_file.close()
        else:
            print("Failed to open styles file")

    def create_widgets(self):
        """
        Creates widgets in GeneratorWindow

        Args:
        
        Returns:
        """
        layout = QHBoxLayout(self.central_widget)

        # Left layout for DTMF buttons
        left_widget = QWidget(self)
        left_layout = QGridLayout(left_widget)
        self.create_dtmf_buttons(left_layout)

        # Right layout for displaying code and saving
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        self.text_display = QLabel("DTMF code: ", self)
        self.text_display.setFont(QFont("Roboto", 32))
        self.text_display.setStyleSheet("color: white")
        self.text_display.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("Save", self)
        self.save_button.setStyleSheet(str(self.stylesheet, encoding='utf-8'))
        self.save_button.setFixedHeight(160)
        self.save_button.clicked.connect(self.save_string)

        right_layout.addWidget(self.text_display)
        right_layout.addWidget(self.save_button)

        layout.addWidget(left_widget, 1)
        layout.addWidget(right_widget, 1)

    def create_dtmf_buttons(self, layout):
        """
        Creates gird of buttons. One for each character in DTMF table

        Args: layout: window layout

        Returns:
        """
        dtmf_labels = [
            ["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"]
        ]
        for row, row_labels in enumerate(dtmf_labels):
            for col, label in enumerate(row_labels):
                button = QPushButton(label, self)
                button.setStyleSheet(str(self.stylesheet, encoding='utf-8'))
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.clicked.connect(lambda _, label=label: self.on_button_click(label))
                layout.addWidget(button, row, col)

    def on_button_click(self, label):
        """
        Method connected to every button in DTMF grid

        Args: label: character asigned to the button

        Returns: 
        """
        self.generate_dtmf_tone(label)
        current_text = self.text_display.text().replace("DTMF code: ", "")
        self.update_text_display(current_text + label)

    def generate_dtmf_tone(self, key, duration=0.5, sample_rate=44100):
        """
        Method generates and play DTMF tone based on given character from DTMF table

        Args: key: character, duration: time duration of dtmf tone, sample_rate: sample rate set to 44100

        Returns:
        """

        if key not in DTMF_FREQUENCIES:
            return
        freq_low, freq_high = DTMF_FREQUENCIES[key]
        t = numpy.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        tone = 0.5 * numpy.sin(2 * numpy.pi * freq_low * t) + 0.5 * numpy.sin(2 * numpy.pi * freq_high * t)
        sounddevice.play(tone, samplerate=sample_rate)

    def generate_dtmf_sequence(self, sequence, duration=0.5, pause=0.1, sample_rate=44100):
        """
        Method generates sequence of DTMF tones base on given sequence

        Args: sequence: sequence of DTMF tones, duration: duration time of each tone, pause: pause between each of the tones, sample_rate: sample rate set to 44100

        Returns: result: generated sequnece
        """

        result = numpy.array([])
        for key in sequence:
            if key in DTMF_FREQUENCIES:
                freq_low, freq_high = DTMF_FREQUENCIES[key]
                t = numpy.linspace(0, duration, int(sample_rate * duration), endpoint=False)
                tone = 0.5 * numpy.sin(2 * numpy.pi * freq_low * t) + 0.5 * numpy.sin(2 * numpy.pi * freq_high * t)
                result = numpy.concatenate((result, tone, numpy.zeros(int(sample_rate * pause))))
        return result

    def update_text_display(self, text):
        """
        Method updated text_display to also contain selected dtmf sequence

        Args: text: text to be updated

        Returns: 
        """

        self.text_display.setText(f"DTMF code: {text}")

    def save_string(self):
        """
        Method saves given Dtmf code to the .wav file

        Args: 

        Returns: 
        """
        current_string = self.text_display.text().replace("DTMF code: ", "")
        if not current_string:
            message_box = QMessageBox()
            message_box.setWindowTitle("No DTMF code to save.")
            message_box.setText("No DTMF code to save.")
            message_box.setStyleSheet("QMessageBox { background-color: #333333; } QMessageBox QLabel { color: white; }")
            message_box.exec_()
            return

        dtmf_signal = self.generate_dtmf_sequence(current_string)
        file_name, _ = QFileDialog.getSaveFileName(self, "Save DTMF Sequence", "", "WAV Files (*.wav)")

        if file_name:
            with wave.open(file_name, "w") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(44100)  # Sample rate
                wav_file.writeframes((dtmf_signal * 32767).astype(numpy.int16).tobytes())

            message_box = QMessageBox()
            message_box.setWindowTitle("DTMF sequence saved.")
            message_box.setText("DTMF sequence saved to " + file_name)
            message_box.setStyleSheet("QMessageBox { background-color: #333333; } QMessageBox QLabel { color: white; }")
            message_box.exec_()
            self.update_text_display("")  # Clear the display after saving
