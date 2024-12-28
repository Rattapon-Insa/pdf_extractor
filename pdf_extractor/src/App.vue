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
          <ul v-if="selectedFiles.length">
            <li v-for="(file, index) in selectedFiles" :key="index">{{ file.name }}</li>
          </ul>
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
      } catch (error) {
        console.error("Error clearing session:", error);
        this.showNotification("Failed to clear session.", "error");
      }
    },
    showNotification(message, type) {
      this.notification = { message, type };
      setTimeout(() => (this.notification.message = ""), 3000);
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

/* Progress Bar */
.progress-container {
  width: 100%;
  background-color: #f3f3f3;
  border-radius: 4px;
  margin-top: 1rem;
  overflow: hidden;
}
.progress-bar {
  height: 10px;
  background-color: #007bff;
  transition: width 0.3s;
}

/* Textarea */
.prompt-editor textarea {
  width: 100%;
  min-height: 120px; /* Fixed */
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

/* Summary Section */
.summary-section h2 {
  margin-bottom: 1rem;
}
.summary-content {
  font-size: 1rem;
  line-height: 1.5;
}
</style>
