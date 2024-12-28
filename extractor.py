import os
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

# Load API keys from .env file
load_dotenv()

# Configure API keys
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Directories for input and output
INPUT_FOLDER = "input_images"
OUTPUT_FOLDER = "output_texts"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def extract_information_with_gemini(file_path, mime_type):
    """Extracts information from the uploaded file using Gemini."""
    file = upload_to_gemini(file_path, mime_type)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        },
        system_instruction="Extract as much information as possible from this file.",
    )

    chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": [file]},
            {"role": "model", "parts": ["Processed file and ready to analyze."]},
        ]
    )

    user_input = "Please extract all detailed information from the uploaded file."
    response = chat_session.send_message(user_input)
    return response.text

def process_images():
    """Processes all images in the input folder and saves extracted text."""
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(INPUT_FOLDER, filename)
            print(f"Processing {file_path}...")

            try:
                extracted_text = extract_information_with_gemini(file_path, mime_type="image/jpeg")
                output_file = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(filename)[0]}.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                print(f"Extracted text saved to {output_file}")
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")

def summarize_with_openai():
    """Reads all text files and generates a summarized report using OpenAI."""
    consolidated_text = ""
    for filename in os.listdir(OUTPUT_FOLDER):
        if filename.endswith('.txt'):
            file_path = os.path.join(OUTPUT_FOLDER, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                consolidated_text += f"\n---\nFile: {filename}\n" + f.read()

    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant specializing in consolidating information."},
            {"role": "user", "content": f"consolidate the following information from multiple files and provide consolidated information to the user:\n\n{consolidated_text}"}
        ],
        temperature=0.1,
        max_tokens=1000)
        summary = response.choices[0].message.content
        print("Summary of All Extracted Information:")
        print(summary)
        return summary
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

def main():
    # Step 1: Process all images in the input folder
    process_images()

    # Step 2: Summarize all extracted text
    summarize_with_openai()

if __name__ == "__main__":
    main()
