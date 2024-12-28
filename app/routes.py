# app/routes.py (or wherever you handle routes)
from flask import Blueprint, request, jsonify
from extractor import Extractor  # The class we built earlier

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
