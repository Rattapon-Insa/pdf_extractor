\<template>
  <div class="app-container">
    <header>
      <h1>Gemini + GPT Summarization</h1>
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

      <!-- Prompt Message Editor -->
      <section class="prompt-editor">
        <h3>Customize Summarization Prompt</h3>
        <textarea v-model="customPrompt" :disabled="isSummarizing"></textarea>
      </section>

      <!-- Action Buttons -->
      <section class="action-buttons">
        <button :disabled="isUploading || isSummarizing || !selectedFiles.length" @click="uploadFiles">
          {{ isUploading ? `Uploading (${uploadedCount}/${selectedFiles.length})` : "Upload Files" }}
        </button>
        <button :disabled="isUploading || isSummarizing" @click="summarize">
          {{ isSummarizing ? "Summarizing..." : "Summarize" }}
        </button>
        <button :disabled="isUploading || isSummarizing" @click="clearSession" class="clear-button">
          Clear Session
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
      customPrompt: "Summarize the following information from the uploaded files.", // Default prompt message
      isUploading: false, // Tracks if upload is in progress
      isSummarizing: false, // Tracks if summarization is in progress
      isDragOver: false, // Tracks if a file is being dragged over the drop zone
      notification: { message: "", type: "" }, // For success/error notifications
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
        const response = await axios.post("http://127.0.0.1:5000/summarize", {
          prompt: this.customPrompt, // Pass custom prompt to the backend
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

        // Clear frontend data
        this.selectedFiles = [];
        this.summary = "";
        this.uploadedCount = 0;
        this.uploadProgress = 0;
      } catch (error) {
        console.error("Error clearing session:", error);
        this.showNotification("Failed to clear session.", "error");
      }
    },
    showNotification(message, type) {
      this.notification = { message, type };
      setTimeout(() => (this.notification.message = ""), 3000); // Clear notification after 3 seconds
    },
    formatSummary(summary) {
      return summary.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>").replace(/- /g, "• ");
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
  justify-content: center;
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

/* Prompt Editor */
.prompt-editor {
  margin-top: 1rem;
}
.prompt-editor textarea {
  width: 100%;
  height: 100px;
  padding: 0.5rem;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* Other Styles */
/* (same as previous App.vue example for buttons, notifications, etc.) */
</style>
