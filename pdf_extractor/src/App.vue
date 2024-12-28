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
      />
    </div>

    <div class="upload-buttons">
      <button @click="uploadFiles">Upload Files</button>
      <button @click="summarize">Summarize</button>
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
      summary: ""
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
        alert("Error uploading files.")
      }
    },

    async summarize() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/summarize')
        // The Flask endpoint should return JSON: { "summary": "<text>" }
        this.summary = response.data.summary || ""
      } catch (error) {
        console.error("Summarization error:", error)
        alert("Error fetching summary.")
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
