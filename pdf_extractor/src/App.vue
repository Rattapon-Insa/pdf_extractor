<template>
  <div class="app-container">
    <header>
      <h1>Gemini + GPT Summarization</h1>
    </header>

    <main>
      <!-- Upload Section -->
      <section class="card upload-section">
        <h2>Upload Files</h2>
        <div
          class="drop-zone"
          @dragover.prevent
          @drop.prevent="handleDrop"
          :class="{ 'drag-over': isDragOver }"
          @dragenter="isDragOver = true"
          @dragleave="isDragOver = false"
        >
          <p v-if="!selectedFiles.length">Drag and drop files here, or click to select files</p>
          <input id="files" type="file" multiple @change="onFileChange" :disabled="isUploading || isSummarizing" />
          <div v-if="selectedFiles.length" class="file-list">
            <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
              {{ file.name }}
            </div>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="progress-container" v-if="isUploading">
          <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
        </div>
      </section>

      <!-- Prompt Section -->
      <section class="card prompt-editor">
        <h2>Customize Summarization Prompt</h2>
        <textarea v-model="customPrompt" :disabled="isSummarizing"></textarea>
      </section>

      <!-- Action Buttons -->
      <section class="card action-buttons">
        <button :disabled="isUploading || isSummarizing || !selectedFiles.length" @click="uploadFiles">
          {{ isUploading ? `Uploading (${uploadedCount}/${selectedFiles.length})` : "Upload Files" }}
        </button>
        <button :disabled="isUploading || isSummarizing || !textFilesAvailable" @click="summarize">
          {{ isSummarizing ? "Summarizing..." : "Summarize" }}
        </button>
        <button :disabled="isUploading || isSummarizing" @click="clearSession" class="clear-button">
          Clear Session
        </button>
      </section>

      <!-- Loading Animation -->
      <div v-if="isSummarizing" class="loading-overlay">
        <div class="spinner"></div>
        <p>Summarizing... Please wait.</p>
      </div>

      <!-- Notification -->
      <div v-if="notification.message" :class="['notification', notification.type]">
        {{ notification.message }}
      </div>

      <!-- Summary Display -->
      <section v-if="summary" class="card summary-section">
        <h2>Summary</h2>
        <div class="summary-content" v-html="formatSummary(summary)"></div>
      </section>
    </main>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "App",
  data() {
    return {
      selectedFiles: [],
      uploadProgress: 0,
      uploadedCount: 0,
      summary: "",
      customPrompt: "Summarize the following information from the uploaded files.",
      isUploading: false,
      isSummarizing: false,
      isDragOver: false,
      notification: { message: "", type: "" },
      textFilesAvailable: false,
    };
  },
  methods: {
    onFileChange(event) {
      this.selectedFiles = Array.from(event.target.files);
      this.uploadedCount = 0;
    },
    handleDrop(event) {
      this.selectedFiles = Array.from(event.dataTransfer.files);
      this.isDragOver = false;
      this.uploadedCount = 0;
    },
    async uploadFiles() {
      if (!this.selectedFiles.length) {
        this.showNotification("No files selected!", "error");
        return;
      }

      this.isUploading = true;
      this.uploadProgress = 0;

      try {
        const totalFiles = this.selectedFiles.length;
        for (let i = 0; i < totalFiles; i++) {
          const formData = new FormData();
          formData.append("file", this.selectedFiles[i]);

          await axios.post("http://127.0.0.1:5000/process", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });

          this.uploadedCount++;
          this.uploadProgress = Math.round(((i + 1) / totalFiles) * 100);
        }

        this.showNotification("All files uploaded successfully!", "success");
        this.selectedFiles = [];
        this.checkTextFiles();
      } catch (error) {
        console.error("Upload error:", error);
        this.showNotification("Error uploading files.", "error");
      } finally {
        this.isUploading = false;
        this.uploadProgress = 0;
      }
    },
    async summarize() {
      this.isSummarizing = true;

      try {
        const response = await axios.post("http://127.0.0.1:5000/summarize", {
          prompt: this.customPrompt,
        });
        this.summary = response.data.summary || "No summary available.";
        this.showNotification("Summarization complete!", "success");
      } catch (error) {
        console.error("Summarization error:", error);
        this.showNotification("Error summarizing files.", "error");
      } finally {
        this.isSummarizing = false;
      }
    },
    async clearSession() {
      try {
        const response = await axios.post("http://127.0.0.1:5000/clear");
        this.showNotification(response.data.message, "success");
        this.selectedFiles = [];
        this.summary = "";
        this.uploadedCount = 0;
        this.uploadProgress = 0;
        this.textFilesAvailable = false;
      } catch (error) {
        console.error("Error clearing session:", error);
        this.showNotification("Failed to clear session.", "error");
      }
    },
    async checkTextFiles() {
      try {
        const response = await axios.get("http://127.0.0.1:5000/check_text_files");
        this.textFilesAvailable = response.data.text_files_available;
      } catch (error) {
        console.error("Error checking text files:", error);
        this.textFilesAvailable = false;
      }
    },
    showNotification(message, type) {
      this.notification = { message, type };
      setTimeout(() => (this.notification.message = ""), 3000);
    },
    formatSummary(summary) {
      return summary
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // Bold
        .replace(/### (.*?)\n/g, "<h3>$1</h3>") // Headings
        .replace(/- /g, "• ") // Bullet points
        .replace(/\n/g, "<br>"); // Line breaks
    },
  },
  created() {
    this.checkTextFiles();
  },
};
</script>

<style scoped>
/* General Layout */
.app-container {
  font-family: "Arial", sans-serif;
  padding: 1rem;
  background-color: #f5f5f5;
}

/* Header */
header {
  text-align: center;
  margin-bottom: 2rem;
}
header h1 {
  font-size: 2rem;
  color: #333;
}

/* Card Styles */
.card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

/* Drop Zone */
.drop-zone {
  border: 2px dashed #007bff;
  padding: 2rem;
  text-align: center;
  border-radius: 8px;
  background-color: #ffffff;
  transition: background-color 0.3s;
}
.drop-zone.drag-over {
  background-color: #e6f7ff;
}

/* File List */
.file-list {
  margin-top: 1rem;
}
.file-item {
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  background-color: #f1f1f1;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* Loading Animation */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 1.2rem;
  z-index: 1000;
}
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 255, 255, 0.2);
  border-top: 5px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Prompt Editor */
.prompt-editor textarea {
  width: 100%;
  min-height: 150px;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  box-sizing: border-box;
}

/* Buttons */
button {
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 0.7rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-right: 1rem;
}
button:hover {
  background-color: #0056b3;
}
button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
