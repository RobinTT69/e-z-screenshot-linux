import io
from PIL import Image, ImageDraw, ImageFont
import os

FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', 'impact.ttf')

def add_text_to_image(image_data: bytes, top_text: str, bottom_text: str, text_color: str, file_type: str, compression_level: int) -> bytes:
    with Image.open(io.BytesIO(image_data)).convert("RGBA") as img:
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size

        def draw_text(text: str, y_position: int) -> None:
            font_size = min(max(img_width // 10, img_height // 10), 80)
            font = ImageFont.truetype(FONT_PATH, font_size)
            text_bbox = draw.textbbox((0, 0), text, font=font)
            while text_bbox[2] - text_bbox[0] > img_width * 0.9:
                font_size -= 1
                font = ImageFont.truetype(FONT_PATH, font_size)
                text_bbox = draw.textbbox((0, 0), text, font=font)
            
            text_x = (img_width - (text_bbox[2] - text_bbox[0])) // 2
            draw.text((text_x, y_position), text, font=font, fill=text_color)

        if top_text:
            draw_text(top_text, img_height // 20)

        if bottom_text:
            draw_text(bottom_text, img_height - img_height // 20 - font_size)

        img = img.convert("RGB")
        output = io.BytesIO()
        img.save(output, format=file_type, compress_level=compression_level)
        return output.getvalue()

