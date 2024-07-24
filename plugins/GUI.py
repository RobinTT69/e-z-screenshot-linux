from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent

class TextInputDialog(QDialog):
    def __init__(self, title: str, label: str, placeholder: str):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(350, 80)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()

        self.label = QLabel(label)
        self.label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        self.layout.addWidget(self.label)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(placeholder)
        self.input_field.setStyleSheet("padding: 5px; font-size: 14px;")
        self.input_field.setFixedHeight(30)
        self.layout.addWidget(self.input_field)

        self.setLayout(self.layout)

        self.input_field.returnPressed.connect(self.accept)
        self.input_field.installEventFilter(self)

    def get_text(self) -> str:
        """Get text from the input field."""
        if self.exec_() == QDialog.Accepted:
            return self.input_field.text().strip()
        return ""
    
    def eventFilter(self, obj, event) -> bool:
        """Handle key events."""
        if event.type() == QKeyEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.reject()
                return True
        return super().eventFilter(obj, event)

