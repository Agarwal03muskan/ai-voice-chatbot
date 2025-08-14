import requests
import time
import os

def generate_video(image_url, audio_path):
    """
    Generates a lip-synced video using the D-ID API.
    """
    DID_API_KEY = os.getenv("DID_API_KEY")
    url = "https://api.d-id.com/talks"

    with open(audio_path, 'rb') as audio:
        files = {'audio': audio}
        payload = {
            "source_url": image_url
        }
        headers = {
            "accept": "application/json",
            "authorization": f"Basic {DID_API_KEY}"
        }

        try:
            # Create the talk
            create_response = requests.post(url, headers=headers, data=payload, files=files)
            create_response.raise_for_status()
            talk_id = create_response.json().get("id")

            # Poll for the result
            while True:
                get_response = requests.get(f"{url}/{talk_id}", headers=headers)
                get_response.raise_for_status()
                result = get_response.json()
                if result.get("status") == "done":
                    return result.get("result_url")
                elif result.get("status") == "error":
                    print(f"D-ID video generation failed: {result.get('error')}")
                    return None
                time.sleep(5)  # Wait before polling again
        except requests.exceptions.RequestException as e:
            print(f"Error in D-ID API call: {e}")
            return None