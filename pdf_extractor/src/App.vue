<template>
  <div class="container">
    <h1>Gemini + GPT Summarization</h1>

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

    <div v-if="summary" class="summary-section">
      <h2>Summary</h2>
      <pre>{{ summary }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: "App",
  data() {
    return {
      selectedFiles: [],
      summary: "",
      isUploading: false,
      isSummarizing: false
    }
  },
  methods: {
    onFileChange(event) {
      // Convert FileList to an array
      this.selectedFiles = Array.from(event.target.files)
    },

    async uploadFiles() {
      if (!this.selectedFiles.length) {
        alert("No files selected!")
        return
      }

      this.isUploading = true
      try {
        // Upload each file to your Flask endpoint
        for (let file of this.selectedFiles) {
          const formData = new FormData()
          formData.append('file', file)

          await axios.post('http://127.0.0.1:5000/process', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
        }
        alert("All files uploaded successfully!")
        this.selectedFiles = [] // Clear the file list after upload
      } catch (error) {
        console.error("Upload error:", error)
        alert("Upload error:", error)
      } finally {
        this.isUploading = false
      }
    },

    async summarize() {
      // Disables the Summarize button while summarizing
      this.isSummarizing = true
      try {
        const response = await axios.get('http://127.0.0.1:5000/summarize')
        this.summary = response.data.summary || ""
      } catch (error) {
        console.error("Summarization error:", error)
        alert("Summarization error: " + error.message || error);
      } finally {
        this.isSummarizing = false
      }
    }
  }
}
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
</style>
