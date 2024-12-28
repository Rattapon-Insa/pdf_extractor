# app/routes.py (or wherever you handle routes)
from flask import Blueprint, request, jsonify
from extractor import Extractor  # The class we built earlier
import os

routes = Blueprint('routes', __name__)
extractor = Extractor()

@routes.route('/process', methods=['POST'])
def process_files():
    files = request.files.getlist("file")  # Get all uploaded files
    if not files:
        return jsonify({"error": "No files provided"}), 400

    results = []
    for file in files:
        try:
            # Save each file and process it
            file.save(f"{extractor.input_folder}/{file.filename}")
            output_file = extractor.process_file(file.filename)
            results.append({"file": file.filename, "output": output_file})
        except Exception as e:
            results.append({"file": file.filename, "error": str(e)})

    return jsonify({"results": results}), 200

@routes.route('/summarize', methods=['GET'])
def summarize():
    try:
        summary = extractor.summarize_all()
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route('/clear', methods=['POST'])
def clear_session():
    import shutil
    try:
        # Clear the input and output folders
        shutil.rmtree(extractor.input_folder)
        shutil.rmtree(extractor.output_folder)

        # Recreate the directories after deletion
        os.makedirs(extractor.input_folder, exist_ok=True)
        os.makedirs(extractor.output_folder, exist_ok=True)

        return jsonify({"message": "Session cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
