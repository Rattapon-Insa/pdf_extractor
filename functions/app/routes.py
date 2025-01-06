from flask import Blueprint, request, jsonify
from extractor import Extractor  # Updated path for `Extractor`
import os
import shutil

# Define the blueprint for routes
routes = Blueprint('routes', __name__)

# Initialize the Extractor service
extractor = Extractor()

@routes.route('/process', methods=['POST'])
def process_files():
    """
    Endpoint to process uploaded files.
    Saves each file to the input folder, processes it, and returns the results.
    """
    try:
        files = request.files.getlist("file")
        if not files:
            return jsonify({"error": "No files provided"}), 400

        results = []
        for file in files:
            try:
                # Save each file and process it
                file_path = os.path.join(extractor.input_folder, file.filename)
                file.save(file_path)
                output_file = extractor.process_file(file.filename)
                results.append({"file": file.filename, "output": output_file})
            except Exception as e:
                results.append({"file": file.filename, "error": str(e)})

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route('/summarize', methods=['POST'])
def summarize():
    """
    Endpoint to summarize the content of all processed files.
    Accepts an optional prompt in the JSON payload.
    """
    try:
        data = request.get_json()
        prompt = data.get("prompt", "Summarize the information from the uploaded files.")

        summary = extractor.summarize_all(prompt=prompt)
        return jsonify({"summary": summary}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route('/clear', methods=['POST'])
def clear_session():
    """
    Endpoint to clear input and output folders, resetting the session.
    """
    try:
        # Clear the input and output folders
        shutil.rmtree(extractor.input_folder, ignore_errors=True)
        shutil.rmtree(extractor.output_folder, ignore_errors=True)

        # Recreate the directories after deletion
        os.makedirs(extractor.input_folder, exist_ok=True)
        os.makedirs(extractor.output_folder, exist_ok=True)

        return jsonify({"message": "Session cleared successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route('/check_text_files', methods=['GET'])
def check_text_files():
    """
    Endpoint to check if text files are available in the output folder.
    """
    try:
        text_files = [
            f for f in os.listdir(extractor.output_folder) if f.endswith('.txt')
        ]
        return jsonify({"text_files_available": len(text_files) > 0}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
