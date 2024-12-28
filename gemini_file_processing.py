import os
import google.generativeai as genai
from dotenv import load_dotenv


# Load API keys from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Create the model
generation_config = {
    "temperature": 0.1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="Extract as much information as possible from this file.",
)

def process_file_with_gemini(file_path, mime_type):
    # Step 1: Upload file
    file = upload_to_gemini(file_path, mime_type)

    # Step 2: Start a chat session with historical context
    chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": [file]},
            {"role": "model", "parts": ["Processed file and ready to analyze."]},
        ]
    )

    # Step 3: Send a text-based instruction
    user_input = "Please extract all detailed information from the uploaded file."
    response = chat_session.send_message(user_input)
    return response.text

# Example usage
if __name__ == "__main__":
    file_path = "processed-39DA4D2D-C7AE-4FB4-A5F7-4E1367BF38B5.JPEG"
    mime_type = "image/jpeg"  # Update MIME type as necessary
    result = process_file_with_gemini(file_path, mime_type)
    print("Gemini API Response:")
    print(result)
