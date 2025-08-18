# utils/meme_generator.py
from PIL import Image, ImageDraw, ImageFont
import io

# --- FUNCTION MODIFIED TO ACCEPT BYTES ---
def generate_meme(input_image_bytes, output_path, top_text, bottom_text):
    """
    Generates a meme from image bytes and saves it to the output path.
    """
    try:
        # Open the image directly from the in-memory bytes
        img = Image.open(io.BytesIO(input_image_bytes)).convert("RGB")
        
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Simple font sizing (can be improved)
        font_size = int(height / 10)
        try:
            # Try to load a common font, otherwise use default
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        # Function to draw text with a black outline
        def draw_text_with_outline(text, x, y):
            # Outline
            draw.text((x-2, y-2), text, font=font, fill="black")
            draw.text((x+2, y-2), text, font=font, fill="black")
            draw.text((x-2, y+2), text, font=font, fill="black")
            draw.text((x+2, y+2), text, font=font, fill="black")
            # Fill
            draw.text((x, y), text, font=font, fill="white")

        # Top text
        if top_text:
            bbox = draw.textbbox((0, 0), top_text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) / 2
            y = 10 # Padding from top
            draw_text_with_outline(top_text.upper(), x, y)

        # Bottom text
        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) / 2
            y = height - text_height - 10 # Padding from bottom
            draw_text_with_outline(bottom_text.upper(), x, y)
            
        img.save(output_path, "JPEG")
        return True
    except Exception as e:
        print(f"Error in generate_meme: {e}")
        return False