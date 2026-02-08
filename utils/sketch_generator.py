# utils/sketch_generator.py
import cv2
import numpy as np
import traceback

def generate_sketch(input_image_bytes, output_path):
    """
    Generates a sketch from image bytes and saves it to the output path.
    Enhanced with better error handling and debugging.
    """
    try:
        # Convert byte data to a NumPy array
        nparr = np.frombuffer(input_image_bytes, np.uint8)
        print(f"DEBUG: Created numpy array of size {len(nparr)}")
        
        # Decode the array into an image that OpenCV can use
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("ERROR: Failed to decode image from bytes in sketch_generator.")
            print(f"DEBUG: Input bytes length: {len(input_image_bytes)}")
            return False

        print(f"DEBUG: Image decoded successfully. Shape: {img.shape}")

        # Convert to grayscale
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print(f"DEBUG: Converted to grayscale. Shape: {gray_image.shape}")
        
        # Invert the grayscale image
        inverted_gray_image = 255 - gray_image
        
        # Apply Gaussian blur
        blurred_image = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
        
        # Invert the blurred image
        inverted_blurred_image = 255 - blurred_image
        
        # Create pencil sketch effect
        pencil_sketch = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)
        
        # Save the sketch
        success = cv2.imwrite(output_path, pencil_sketch)
        
        if success:
            print(f"SUCCESS: Sketch saved to {output_path}")
            return True
        else:
            print(f"ERROR: Failed to save sketch to {output_path}")
            return False
            
    except Exception as e:
        print(f"ERROR in generate_sketch: {e}")
        print(f"ERROR Traceback: {traceback.format_exc()}")
        return False