# Gemini + GPT Summarization App

The **Gemini + GPT Summarization App** allows users to upload image or PDF files, extract information using Google Gemini, and summarize the extracted data using OpenAI's GPT model. It provides an easy-to-use interface for handling files, customizing prompts, and generating consolidated summaries.

My approach combines the strengths of Gemini and ChatGPT to enhance invoice processing efficiency.

Gemini's Role in Invoice Data Extraction:

Cost-Effective Text Extraction: Gemini is adept at extracting information from invoice images, providing a precise and affordable solution for automating invoice processing. 
GITHUB
ChatGPT's Reasoning Capabilities:

Advanced Reasoning: OpenAI's ChatGPT models, particularly the 4o series, are designed to spend more time deliberating before responding, enabling them to tackle complex tasks in science, coding, and mathematics. 
OPENAI

---

## Features

- **Drag-and-Drop File Upload**: Easily upload multiple files by dragging and dropping them into the upload zone.
- **File Format Support**: Supports image and PDF files for processing.
- **Customizable Summarization Prompt**: Tailor the summarization process by editing the prompt text.
- **Summarization Process**: Extract and consolidate information from multiple files into a summarized output.
- **Session Management**:
  - Clear uploaded files and summaries with the **Clear Session** button.
  - Disable the **Summarize** button if no processed text files are available.
- **Responsive and User-Friendly Interface**: Includes a clean design with feedback notifications and a loading animation during summarization.

---

## Prerequisites

### Backend Requirements
- **Python 3.8+**
- **Flask** for API handling
- **Dependencies**:
  - `google-generativeai` (Google Gemini API)
  - `openai` (OpenAI API)
  - `Flask-CORS` for Cross-Origin Resource Sharing
  - `dotenv` for environment variable management

Install the required packages:

```bash
pip install flask flask-cors python-dotenv google-generativeai openai
```

### Frontend Requirements
- Node.js and npm for managing Vue.js dependencies.

### Frontend Setup
- Navigate to the frontend directory:

bash
```
cd frontend
```

Install the dependencies:

bash
```
npm install
```

Start the development server:

bash
```
npm run serve
```
### Access the app in your browser at http://localhost:8080.

### Usage Instructions
1. Upload Files
Drag and drop files into the upload zone or click the Choose Files button.
Click Upload Files to process the files. The app will extract text from the uploaded files using Google Gemini.
2. Customize the Summarization Prompt
Edit the text in the Customize Summarization Prompt box to define how the summary should be generated.
3. Summarize
Once files are processed, the Summarize button will be enabled.
Click Summarize to consolidate extracted information into a detailed summary.
4. Clear Session
Use the Clear Session button to delete all uploaded files and reset the session.

### Project Structure

bash
```
project/
├── backend/
│   ├── app.py                # Flask app entry point
│   ├── routes.py             # API route handlers
│   ├── extractor.py          # File processing and summarization logic
│   ├── output_texts/         # Folder for storing processed text files
│   ├── input_files/          # Folder for storing uploaded files
│   └── .env                  # Environment variables (API keys)
├── frontend/
│   ├── src/
│   │   ├── App.vue           # Main Vue.js application
│   │   └── components/       # Vue components
│   ├── public/
│   └── package.json          # Frontend dependencies
└── README.md                 # Documentation
```

## API Endpoints

### `/process` (POST)
Upload a file for processing.

- **Request Body**:  
  Multipart form-data containing the file.

- **Response**:  
  - **Success**:  
    ```json
    {
      "message": "File processed successfully",
      "output_file": "<file_path>"
    }
    ```
  - **Error**:  
    ```json
    {
      "error": "<error_message>"
    }
    ```


### `/summarize` (POST)
Summarize extracted text from processed files.

- **Request Body**:  
  ```json
  {
    "prompt": "<custom_prompt>"
  }
- **Response**:  
  - **Success**:  
    ```json
    { "summary": "<generated_summary>" }
    ```
  - **Error**:  
    ```json
    {
      "error": "<error_message>"
    }
    ```

### `/clear` (POST)
Clear uploaded files and summaries.

- **Response**:  
  - **Success**:  
    ```json
    { "message": "Session cleared successfully" }
    ```
  - **Error**:  
    ```json
    {
      "error": "<error_message>"
    }
    ```

### `/check_text_files` (POST)
Check if text files are available for summarization.

- **Response**:  
  - **Success**:  
    ```json
    { "text_files_available": true }
    ```
    or
  
    ```json
    { "text_files_available": false }
    ```
