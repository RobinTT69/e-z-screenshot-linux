import sys
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

class TextInputDialog(QDialog):
    def __init__(self, title: str, label: str, placeholder: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(350, 80)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        self.label = QLabel(label)
        self.label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(self.label)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        self.input_field.setStyleSheet("padding: 5px; font-size: 14px;")
        self.input_field.setFixedHeight(30)
        layout.addWidget(self.input_field)

        self.setLayout(layout)
        self.input_field.returnPressed.connect(self.accept)
        self.input_field.installEventFilter(self)

    def get_text(self) -> str:
        return self.input_field.text().strip() if self.exec_() == QDialog.Accepted else ""

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QKeyEvent.KeyPress and event.key() == Qt.Key_Escape:
            self.reject()
            return True
        return super().eventFilter(obj, event)

def prompt_text_input() -> (str, str):
    app = QApplication(sys.argv)
    top_text = TextInputDialog("Top Text", "Text for the top of the screenshot:", "Top text").get_text()
    bottom_text = TextInputDialog("Bottom Text", "Text for the bottom of the screenshot:", "Bottom text").get_text()
    app.quit()
    return top_text, bottom_text
