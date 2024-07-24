import io
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "fonts/impact.ttf"  # Adjust the path as necessary

def add_text_to_image(image_data: bytes, top_text: str, bottom_text: str, text_color: str, file_type: str, compression_level: int) -> bytes:
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
            bottom_margin = img_height - img_height // 20

