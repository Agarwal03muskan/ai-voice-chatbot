# utils/sketch_generator.py
import cv2
import numpy as np

# --- FUNCTION MODIFIED TO ACCEPT BYTES ---
def generate_sketch(input_image_bytes, output_path):
    """
    Generates a sketch from image bytes and saves it to the output path.
    """
    try:
        # Convert byte data to a NumPy array
        nparr = np.frombuffer(input_image_bytes, np.uint8)
        # Decode the array into an image that OpenCV can use
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("Error: Failed to decode image from bytes in sketch_generator.")
            return False

        # --- THIS IS THE CORRECTED LINE ---
        # The typo 'cv.COLOR_BGR2GRAY' has been fixed to 'cv2.COLOR_BGR2GRAY'
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # ------------------------------------

        inverted_gray_image = 255 - gray_image
        blurred_image = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
        inverted_blurred_image = 255 - blurred_image
        pencil_sketch = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)
        
        cv2.imwrite(output_path, pencil_sketch)
        return True
    except Exception as e:
        print(f"Error in generate_sketch: {e}")
        return False