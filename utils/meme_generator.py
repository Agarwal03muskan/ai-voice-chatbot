# utils/meme_generator.py
from PIL import Image, ImageDraw, ImageFont
import io
import traceback

def generate_meme(input_image_bytes, output_path, top_text, bottom_text):
    """
    Generates a meme from image bytes and saves it to the output path.
    Enhanced with better error handling and debugging.
    """
    try:
        # Open the image directly from the in-memory bytes
        img = Image.open(io.BytesIO(input_image_bytes)).convert("RGB")
        print(f"DEBUG: Image opened successfully. Size: {img.size}")
        
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Simple font sizing (can be improved)
        font_size = int(height / 10)
        try:
            # Try to load a common font, otherwise use default
            font = ImageFont.truetype("arial.ttf", font_size)
            print(f"DEBUG: Using Arial font at size {font_size}")
        except IOError:
            try:
                # Try alternative font paths for different systems
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                print(f"DEBUG: Using DejaVu font at size {font_size}")
            except IOError:
                font = ImageFont.load_default()
                print(f"DEBUG: Using default font")

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
            y = 10  # Padding from top
            draw_text_with_outline(top_text.upper(), x, y)
            print(f"DEBUG: Added top text: {top_text}")

        # Bottom text
        if bottom_text:
            bbox = draw.textbbox((0, 0), bottom_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) / 2
            y = height - text_height - 10  # Padding from bottom
            draw_text_with_outline(bottom_text.upper(), x, y)
            print(f"DEBUG: Added bottom text: {bottom_text}")
            
        # Save the meme
        img.save(output_path, "JPEG")
        print(f"SUCCESS: Meme saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"ERROR in generate_meme: {e}")
        print(f"ERROR Traceback: {traceback.format_exc()}")
        return False