# app/routes.py (or wherever you handle routes)
from flask import Blueprint, request, jsonify
from extractor import Extractor  # The class we built earlier

routes = Blueprint('routes', __name__)
extractor = Extractor()

@routes.route('/process', methods=['POST'])
def process_file():
    # Upload single file
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Save file to the input folder or process immediately
    file.save(f"{extractor.input_folder}/{file.filename}")

    try:
        # Extractor processes it
        output_file = extractor.process_file(file.filename)
        return jsonify({"message": "File processed successfully", "output_file": output_file})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route('/summarize', methods=['GET'])
def summarize():
    try:
        summary = extractor.summarize_all()
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
