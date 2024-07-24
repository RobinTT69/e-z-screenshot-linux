from PIL import Image, ImageDraw, ImageFont
import io
import os
from typing import Optional
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton

# Path to the font file
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def initialize_gui() -> QApplication:
    """Initialize the GUI application."""
    app = QApplication([])
    return app

def get_text_input(app: QApplication) -> (str, str):
    """Display the GUI dialog for text input."""
    class TextInputDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.top_text_edit = QLineEdit()
            self.bottom_text_edit = QLineEdit()
            self.top_text = None
            self.bottom_text = None
            self.init_ui()
        
        def init_ui(self):
            self.setWindowTitle("Text Input")
            self.setFixedSize(300, 150)  # Set fixed size for the floating window

            self.layout = QVBoxLayout()
            self.setLayout(self.layout)
            
            self.top_text_label = QLabel("Top Text:")
            self.top_text_edit.setPlaceholderText("Enter top text")
            self.layout.addWidget(self.top_text_label)
            self.layout.addWidget(self.top_text_edit)

            self.bottom_text_label = QLabel("Bottom Text:")
            self.bottom_text_edit.setPlaceholderText("Enter bottom text")
            self.bottom_text_edit.setVisible(False)  # Hide bottom text input initially
            self.layout.addWidget(self.bottom_text_label)
            self.layout.addWidget(self.bottom_text_edit)

            self.button = QPushButton('OK')
            self.button.clicked.connect(self.on_button_click)
            self.layout.addWidget(self.button)
            
            self.setModal(True)
            self.show()

        def on_button_click(self):
            if self.top_text is None:
                self.top_text = self.top_text_edit.text()
                self.top_text_edit.setVisible(False)  # Hide top text input
                self.bottom_text_label.setVisible(True)  # Show bottom text label
                self.bottom_text_edit.setVisible(True)  # Show bottom text input
            else:
                self.bottom_text = self.bottom_text_edit.text()
                self.accept()

    dialog = TextInputDialog()
    dialog.exec_()
    return dialog.top_text, dialog.bottom_text

def add_text_to_image(image_data: bytes, top_text: Optional[str], bottom_text: Optional[str], text_color: str, file_type: str='PNG', compression_level: int=0) -> bytes:
    """Add text to the image and return the modified image data."""
    with Image.open(io.BytesIO(image_data)).convert("RGBA") as img:
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size

        min_font_size = 20
        max_font_size = 80
        font_size = max(min(img_width // 10, img_height // 10), min_font_size)
        font_size = min(font_size, max_font_size)
        font = ImageFont.truetype(FONT_PATH, font_size)

        def draw_text(text: str, y_position: int) -> None:
            """Draw text on the image."""
            nonlocal font
            while True:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                if text_width > img_width * 0.9:
                    font_size -= 1
                    font = ImageFont.truetype(FONT_PATH, font_size)
                else:
                    break

            text_x = (img_width - text_width) // 2
            text_y = y_position

            draw.text((text_x, text_y), text, font=font, fill=text_color)

        if top_text:
            top_margin = img_height // 20
            draw_text(top_text, top_margin)

        if bottom_text:
            bottom_margin = img_height - img_height // 20 - font_size
            draw_text(bottom_text, bottom_margin)

        img = img.convert("RGB")

        output = io.BytesIO()
        img.save(output, format=file_type, compress_level=compression_level)
        
        return output.getvalue()
