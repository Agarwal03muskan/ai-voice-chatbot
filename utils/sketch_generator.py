import cv2
import numpy as np

def apply_gamma_correction(image, gamma=1.0):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def generate_sketch(input_image_path, output_image_path):
    try:
        image = cv2.imread(input_image_path)
        if image is None:
            print(f"Error: Could not read the image from {input_image_path}")
            return False

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted_gray_image = 255 - gray_image
        blurred_image = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
        inverted_blurred_image = 255 - blurred_image
        pencil_sketch = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)

        # Lowered gamma for darker, more defined lines
        gamma = 0.5 
        darker_sketch = apply_gamma_correction(pencil_sketch, gamma=gamma)
        
        cv2.imwrite(output_image_path, darker_sketch)
        
        return True

    except Exception as e:
        print(f"An error occurred during sketch generation: {e}")
        return False