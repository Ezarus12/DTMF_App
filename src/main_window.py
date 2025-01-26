from PyQt5.QtCore import QFile, Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFont

from constants import SCREEN_HEIGHT, SCREEN_WIDTH

from dtmf_generator_window import DtmfWindow
from dtmf_decoder_window import DtmfDecodeWindow

# Main window to choose between DTMF generator and decoder
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DTMF FD")
        self.setGeometry(320, 180, SCREEN_WIDTH, SCREEN_HEIGHT)  # Window position and resolution

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.setStyleSheet("background:#252525")

        # Load styles
        self.load_stylesheet()

        # Create main layout and widgets
        layout = QVBoxLayout(self.central_widget)
        layout.setAlignment(Qt.AlignCenter)  # Align content to the center
        self.create_widgets(layout)

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

    def create_widgets(self, layout):
        """
        Creates widgets in main window
        """
        # Create and center the label
        self.chooseText = QLabel(self.central_widget)
        self.chooseText.setText("Choose option:")
        self.chooseText.setFont(QFont("Roboto", 32))
        self.chooseText.setStyleSheet("color: white;")
        self.chooseText.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.chooseText)

        # Create buttons with increased height
        self.GenDtmfButton = QPushButton("Generate DTMF", self.central_widget)
        self.GenDtmfButton.setStyleSheet(str(self.stylesheet, encoding='utf-8'))
        self.GenDtmfButton.setFixedHeight(160) 
        self.GenDtmfButton.setFixedWidth(600)  
        self.GenDtmfButton.clicked.connect(self.open_dtmf_window)

        self.EncDtmfButton = QPushButton("DTMF Encoder", self.central_widget)
        self.EncDtmfButton.setStyleSheet(str(self.stylesheet, encoding='utf-8'))
        self.EncDtmfButton.setFixedHeight(160)
        self.EncDtmfButton.setFixedWidth(600)  
        self.EncDtmfButton.clicked.connect(self.open_enc_dtmf_window)

        # Add buttons to layout
        layout.addWidget(self.GenDtmfButton)
        layout.addWidget(self.EncDtmfButton)

    def open_dtmf_window(self):
        self.dtmf_window = DtmfWindow()
        self.dtmf_window.show()
        #self.close()

    def open_enc_dtmf_window(self):
        self.dtmf_decode_window = DtmfDecodeWindow()
        self.dtmf_decode_window.show()
        #self.close()
