from PIL import Image, ImageDraw, ImageFont

def wrap_text(text, font, max_width):
    lines = []
    if not text:
        return lines
    words = text.split(' ')
    current_line = ''
    for word in words:
        test_line = f'{current_line} {word}'.strip()
        bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def generate_meme(input_image_path, output_image_path, top_text="", bottom_text=""):
    try:
        img = Image.open(input_image_path).convert("RGB")
        width, height = img.size
        draw = ImageDraw.Draw(img)
        font_path = "static/fonts/impact.ttf"
        font_size = int(width / 10)
        font = ImageFont.truetype(font_path, font_size)
        text_color = "white"
        outline_color = "black"
        outline_width = max(1, int(font_size / 20))

        def draw_text_with_outline(text_line, position, text_align='center'):
            x, y = position
            bbox = draw.textbbox((0, 0), text_line, font=font)
            text_width = bbox[2] - bbox[0]
            if text_align == 'center':
                x = (width - text_width) / 2
            for dx in [-outline_width, 0, outline_width]:
                for dy in [-outline_width, 0, outline_width]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text_line, font=font, fill=outline_color)
            draw.text((x, y), text_line, font=font, fill=text_color)

        if top_text:
            wrapped_top_lines = wrap_text(top_text.upper(), font, width - 20)
            y_cursor = 10
            for line in wrapped_top_lines:
                draw_text_with_outline(line, (0, y_cursor))
                y_cursor += font.getbbox(line)[3] + 5

        if bottom_text:
            wrapped_bottom_lines = wrap_text(bottom_text.upper(), font, width - 20)
            bbox = font.getbbox("A")
            line_height = bbox[3] - bbox[1]
            total_text_height = line_height * len(wrapped_bottom_lines) + 5 * (len(wrapped_bottom_lines) - 1)
            y_cursor = height - total_text_height - 10
            for line in wrapped_bottom_lines:
                draw_text_with_outline(line, (0, y_cursor))
                y_cursor += line_height + 5
                
        img.save(output_image_path)
        return True
    except Exception as e:
        print(f"An error occurred during meme generation: {e}")
        return False