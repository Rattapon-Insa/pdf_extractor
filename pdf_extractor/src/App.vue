<template>
  <div :class="['app-container', { dark: isDarkMode }]">
    <header>
      <h1>Gemini + GPT Summarization</h1>
      <button class="dark-mode-toggle" @click="toggleDarkMode">
        {{ isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode" }}
      </button>
    </header>

    <main>
      <!-- Drag-and-Drop Upload Section -->
      <section class="upload-section">
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
          <ul v-if="selectedFiles.length">
            <li v-for="(file, index) in selectedFiles" :key="index">{{ file.name }}</li>
          </ul>
        </div>

        <!-- Progress Bar -->
        <div class="progress-container" v-if="isUploading">
          <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
        </div>
      </section>

      <!-- Action Buttons -->
      <section class="action-buttons">
        <button :disabled="isUploading || isSummarizing || !selectedFiles.length" @click="uploadFiles">
          {{ isUploading ? `Uploading (${uploadedCount}/${selectedFiles.length})` : "Upload Files" }}
        </button>
        <button :disabled="isUploading || isSummarizing" @click="summarize">
          {{ isSummarizing ? "Summarizing..." : "Summarize" }}
        </button>
      </section>

      <!-- Notification -->
      <div v-if="notification.message" :class="['notification', notification.type]">
        {{ notification.message }}
      </div>

      <!-- Summary Display -->
      <section v-if="summary" class="summary-section">
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
      selectedFiles: [], // Tracks selected files for upload
      uploadProgress: 0, // Tracks upload progress percentage
      uploadedCount: 0, // Tracks how many files have been uploaded
      summary: "", // Stores summarized text
      isUploading: false, // Tracks if upload is in progress
      isSummarizing: false, // Tracks if summarization is in progress
      isDragOver: false, // Tracks if a file is being dragged over the drop zone
      notification: { message: "", type: "" }, // For success/error notifications
      isDarkMode: false, // Tracks dark mode state
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
        const response = await axios.get("http://127.0.0.1:5000/summarize");
        this.summary = response.data.summary || "No summary available.";
        this.showNotification("Summarization complete!", "success");
      } catch (error) {
        console.error("Summarization error:", error);
        this.showNotification("Error summarizing files.", "error");
      } finally {
        this.isSummarizing = false;
      }
    },
    showNotification(message, type) {
      this.notification = { message, type };
      setTimeout(() => (this.notification.message = ""), 3000); // Clear notification after 3 seconds
    },
    formatSummary(summary) {
      return summary.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>").replace(/- /g, "• ");
    },
    toggleDarkMode() {
      this.isDarkMode = !this.isDarkMode;
      document.body.classList.toggle("dark", this.isDarkMode);
    },
  },
};
</script>

<style scoped>
/* General Layout */
.app-container {
  font-family: Arial, sans-serif;
  padding: 1rem;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
main {
  display: grid;
  gap: 1rem;
}

/* Drop Zone */
.drop-zone {
  border: 2px dashed #007bff;
  padding: 1rem;
  text-align: center;
  border-radius: 8px;
  background-color: #f9f9f9;
  transition: background-color 0.3s;
}
.drop-zone.drag-over {
  background-color: #e6f7ff;
}

/* Dark Mode */
.app-container.dark {
  background-color: #121212;
  color: #e0e0e0;
}
.app-container.dark .drop-zone {
  background-color: #333;
  border-color: #007bff;
}
.app-container.dark .drop-zone.drag-over {
  background-color: #444;
}

/* Progress Bar */
.progress-container {
  width: 100%;
  background-color: #f3f3f3;
  border-radius: 4px;
  overflow: hidden;
}
.progress-bar {
  height: 10px;
  background-color: #007bff;
  transition: width 0.3s;
}

/* Notifications */
.notification {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 1rem 2rem;
  border-radius: 8px;
  color: white;
  font-size: 1rem;
}
.notification.success {
  background-color: #28a745;
}
.notification.error {
  background-color: #dc3545;
}

/* Summary Section */
.summary-section {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.app-container.dark .summary-section {
  background-color: #333;
}
</style>
