<template>
  <div class="container">
    <h1>Gemini + GPT Summarization</h1>

    <!-- File Upload Section -->
    <div class="upload-section">
      <label for="files">Select files (images/PDFs):</label>
      <input
        id="files"
        type="file"
        multiple
        @change="onFileChange"
        :disabled="isUploading || isSummarizing"
      />
    </div>

    <!-- Action Buttons -->
    <div class="upload-buttons">
      <button
        :disabled="isUploading || isSummarizing || !selectedFiles.length"
        @click="uploadFiles"
      >
        {{ isUploading ? "Uploading..." : "Upload Files" }}
      </button>
      <button
        :disabled="isUploading || isSummarizing"
        @click="summarize"
      >
        {{ isSummarizing ? "Summarizing..." : "Summarize" }}
      </button>
    </div>

    <!-- Summary Display Section -->
    <div v-if="summary" class="summary-section">
      <h2>Summary</h2>
      <pre>{{ summary }}</pre>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "App",
  data() {
    return {
      selectedFiles: [], // Tracks selected files for upload
      summary: "", // Stores summarized text
      isUploading: false, // Tracks whether an upload is in progress
      isSummarizing: false, // Tracks whether summarization is in progress
    };
  },
  methods: {
    // Triggered when files are selected
    onFileChange(event) {
      this.selectedFiles = Array.from(event.target.files); // Convert FileList to Array
    },

    // Handles file uploads
    async uploadFiles() {
      if (!this.selectedFiles.length) {
        alert("No files selected!");
        return;
      }

      this.isUploading = true; // Set loading state
      try {
        for (let file of this.selectedFiles) {
          const formData = new FormData();
          formData.append("file", file);

          // Send file to the backend
          await axios.post("http://127.0.0.1:5000/process", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
        }

        alert("All files uploaded successfully!");
        this.selectedFiles = []; // Clear selected files
      } catch (error) {
        console.error("Upload error:", error);
        alert("Error uploading files.");
      } finally {
        this.isUploading = false; // Reset loading state
      }
    },

    // Handles summarization request
    async summarize() {
      this.isSummarizing = true; // Set summarization state
      try {
        const response = await axios.get("http://127.0.0.1:5000/summarize");
        this.summary = response.data.summary || "No summary available.";
      } catch (error) {
        console.error("Summarization error:", error);
        alert("Error summarizing files.");
      } finally {
        this.isSummarizing = false; // Reset summarization state
      }
    },
  },
};
</script>

<style scoped>
.container {
  width: 600px;
  margin: 0 auto;
}

.upload-section,
.upload-buttons {
  margin: 1rem 0;
}

.summary-section {
  margin-top: 2rem;
  background-color: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
}

button {
  margin-right: 1rem;
  padding: 0.5rem 1rem;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
