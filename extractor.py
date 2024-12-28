import mimetypes
import os

import google.generativeai as genai
import openai
from dotenv import load_dotenv

# Load API keys
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
openai.api_key = os.getenv("OPEN_AI_API_KEY")


class Extractor:
    def __init__(self, input_folder="input_files", output_folder="output_texts"):
        self.input_folder = input_folder
        self.output_folder = output_folder
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

    def upload_to_gemini(self, path):
        """Uploads a file to Gemini API."""
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            raise ValueError(f"Unable to determine MIME type for {path}")
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file: {file.uri}")
        return file

    def extract_information(self, file_path):
        """Extracts information from the uploaded file using Gemini."""
        file = self.upload_to_gemini(file_path)
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
        print(f"Extracted information: {response.text}")
        return response.text

    def process_file(self, filename):
        """Processes a single file and saves the extracted text."""
        file_path = os.path.join(self.input_folder, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        extracted_text = self.extract_information(file_path)
        output_file = os.path.join(
            self.output_folder, f"{os.path.splitext(filename)[0]}.txt"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print(f"Extracted text saved to {output_file}")
        return output_file

    def summarize_all(self):
        """Summarizes the extracted text from all processed files using OpenAI."""
        consolidated_text = ""
        for filename in os.listdir(self.output_folder):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.output_folder, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    consolidated_text += f"\n---\nFile: {filename}\n" + f.read()

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant specializing in consolidating and summarizing information.",
                    },
                    {
                        "role": "user",
                        "content": f"Summarize the following information from multiple files:\n\n{consolidated_text}",
                    },
                ],
                temperature=0.1,
                max_tokens=2048,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            summary = response.choices[0].message.content
            print(f"Summary: {summary}")
            return summary

        except Exception as e:
            print(f"Error during summarization: {e}")
            raise
