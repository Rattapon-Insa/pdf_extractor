import mimetypes
import os

import google.generativeai as genai
import openai
from dotenv import load_dotenv
from pdf2image import convert_from_path

# Load API keys
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
openai.api_key = os.getenv("OPEN_AI_API_KEY")


class Extractor:
    def __init__(
        self,
        input_folder="input_files",
        output_folder="output_texts",
        temp_folder="temp_images",
    ):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.temp_folder = temp_folder
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)

    def upload_to_gemini(self, path):
        """Uploads a file to Gemini API."""
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type is None:
            raise ValueError(f"Unable to determine MIME type for {path}")
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file: {file.uri}")
        return file

    def pdf_to_jpg(self, pdf_path):
        """Converts a PDF to JPG images and saves them in the temp folder."""
        images = convert_from_path(pdf_path, dpi=300)
        jpg_files = []
        for i, image in enumerate(images):
            image_path = os.path.join(
                self.temp_folder,
                f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{i + 1}.jpg",
            )
            image.save(image_path, "JPEG")
            jpg_files.append(image_path)
            print(f"Saved: {image_path}")
        return jpg_files

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

        # If the file is a PDF, convert it to JPGs first
        if filename.lower().endswith(".pdf"):
            print(f"Processing PDF: {filename}")
            jpg_files = self.pdf_to_jpg(file_path)
            extracted_text = ""
            for jpg_file in jpg_files:
                extracted_text += self.extract_information(jpg_file) + "\n"
        else:
            print(f"Processing non-PDF file: {filename}")
            extracted_text = self.extract_information(file_path)

        output_file = os.path.join(
            self.output_folder, f"{os.path.splitext(filename)[0]}.txt"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print(f"Extracted text saved to {output_file}")
        return output_file

    def summarize_all(self, prompt=None):
        """
        Summarizes the extracted text from all processed files using OpenAI.
        Allows a custom prompt for flexibility.
        """
        consolidated_text = ""
        for filename in os.listdir(self.output_folder):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.output_folder, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    consolidated_text += f"\n---\nFile: {filename}\n" + f.read()

        # Use default prompt if no custom prompt is provided
        prompt = (
            prompt
            or "Summarize the following information from the uploaded files as much detail as possible. try to put it in the same format."
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant specializing in consolidating information.",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{consolidated_text}",
                    },
                ],
                temperature=0.1,
                max_tokens=9000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )

            summary = response.choices[0].message.content
            print(f"Summary: {summary}")
            return summary

        except Exception as e:
            print(f"Error during summarization: {e}")
            raise
