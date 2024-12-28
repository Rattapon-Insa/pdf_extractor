from flask import Blueprint, request, jsonify
from extractor import Extractor

routes = Blueprint('routes', __name__)

# Initialize Extractor
extractor = Extractor()

@routes.route('/process', methods=['POST'])
def process_file():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Save uploaded file to input folder
    file_path = f"{extractor.input_folder}/{file.filename}"
    file.save(file_path)

    try:
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
