import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


class VideoPlayer(QMainWindow):
    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.video_widget = QVideoWidget(self.central_widget)
        self.layout.addWidget(self.video_widget)

        self.player = QMediaPlayer(self)
        self.player.setVideoOutput(self.video_widget)

        open_button = QPushButton("Open Video File", self.central_widget)
        open_button.clicked.connect(self.open_file)
        self.layout.addWidget(open_button)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi)")
        if filename:
            media = QMediaContent(QUrl.fromLocalFile(filename))
            self.player.setMedia(media)
            self.player.play()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.show()
    sys.exit(app.exec_())
