from PyQt5.QtCore import Qt, QFile
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QMessageBox

from constants import DTMF_FREQUENCIES, SCREEN_WIDTH, SCREEN_HEIGHT
import wave
import numpy
import time
from scipy.signal import find_peaks

class DtmfDecodeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DTMF Decoder")
        self.setGeometry(320, 180, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.setStyleSheet("background: #252525; color: white;")

        self.load_stylesheet()

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
        # Central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Label for decoded DTMF sequence
        self.decoded_label = QLabel("Decoded DTMF sequence:", self)
        self.decoded_label.setStyleSheet("font-size: 36px; padding: 20px;")
        self.decoded_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.decoded_label)

        # Button to open file dialog
        self.file_button = QPushButton("Select a .wav file", self)
        self.file_button.setStyleSheet(str(self.stylesheet, encoding='utf-8'))
        self.file_button.setFixedHeight(160) 
        self.file_button.setFixedWidth(600)  
        self.file_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.file_button)

        # Label to show the selected file path
        self.file_label = QLabel("No file selected", self)
        self.file_label.setStyleSheet("font-size: 18px; padding: 10px;")
        self.file_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.file_label)
        
        layout.setAlignment(Qt.AlignCenter)

    def open_file_dialog(self):
        """
        Open a file dialog to select a .wav file
        
        Args:
        
        Return:
        
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a .wav file", "", "Audio Files (*.wav)")
        if file_path:
            if file_path.endswith(".wav"):
                self.selected_file_path = file_path
                self.file_label.setText(f"Selected file: {file_path}")
                sequnece = self.decodeDtmfSequence(file_path)
                self.decoded_label.setText("Decoded DTMF sequence: " + str(sequnece))
                print(sequnece)
            else:
                QMessageBox.warning(self, "Invalid File", "Please select a valid .wav file.")
        else:
            self.file_label.setText("No file selected")

    def identify_dtmf_tone(self, low_freq, high_freq):
        """
        Method to identify dtmf tone by comparing low and high frequences to DTMF table

        Args: low and high frequencies

        Returns: key: DTMF char
        """
        for key, (dtmf_low, dtmf_high) in DTMF_FREQUENCIES.items():
            if (
                abs(low_freq - dtmf_low) <= 10 and  
                abs(high_freq - dtmf_high) <= 10   
            ):
                return key
        return "?"

    def decodeDtmfSequence(self, file_path):
        """
        Method to check if given file is dtmf sequence and decode it

        Args: file_path: path to the given file

        Returns: dtmf_sequence: decoded sequence
        """
        with wave.open(file_path, "rb") as wav_file:
            #getting data from the wave_file
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()

            #getting data from wav_file into numpy table
            raw_data = wav_file.readframes(n_frames)
            data_table = numpy.frombuffer(raw_data, dtype=numpy.int16)

            chunk_size = int(framerate * 0.1)

            chunk_duration_time = 0

            for i in range(0, len(data_table), chunk_size):
                chunk = data_table[i:i + chunk_size]
                if all(x == 0 for x in chunk):
                    chunk_duration_time = i/chunk_size*0.1
                    break

            #print(chunk_duration_time)
            #setting chunksize to 0.6s
            chunk_size = int(framerate * chunk_duration_time)
            dtmf_sequence = []

            #checking every chunk of the sequence
            for i in range(0, len(data_table), chunk_size):
                chunk = data_table[i:i + chunk_size]
                if len(chunk) < chunk_size:
                    break
                # Fast Fourier Transform for chunk
                fft = numpy.fft.rfft(chunk)

                # Frequency table
                freqs = numpy.fft.rfftfreq(len(chunk), 1 / framerate)

                # Magnitudes table
                magnitudes = numpy.abs(fft)

                # Finding high frequency
                peaks, _ = find_peaks(magnitudes, height=1000)
                peak_freqs_magnitudes = []
                for p in peaks:
                    peak_freqs_magnitudes.append((freqs[p], magnitudes[p]))

                # Sorting magnitudes in descending order
                peak_freqs_magnitudes = sorted(peak_freqs_magnitudes, key=lambda x: -x[1])

                peak_freqs = []

                for freq, _ in peak_freqs_magnitudes[:2]:
                    peak_freqs.append(freq)  # Adding only the frequency (not the tuple)

                if len(peak_freqs) == 2:
                    low_freq, high_freq = sorted(peak_freqs)
                    tone = self.identify_dtmf_tone(low_freq, high_freq)
                    dtmf_sequence.append(tone)

            for char in dtmf_sequence:
                if char == "?":
                    return "Not a valid DTMF sequence"

            return "".join(dtmf_sequence)
                    
