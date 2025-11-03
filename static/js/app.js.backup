// Beautiful CyberGuard Frontend JavaScript
class CyberGuardApp {
    constructor() {
        this.initializeEventListeners();
        this.loadSampleData();
    }

    initializeEventListeners() {
        // Single classification
        document.getElementById('classify-btn').addEventListener('click', () => this.classifySingle());
        document.getElementById('load-sample-btn').addEventListener('click', () => this.loadSampleData());
        document.getElementById('clear-btn').addEventListener('click', () => this.clearSingle());

        // Batch processing
        document.getElementById('process-batch-btn').addEventListener('click', () => this.processBatch());
        document.getElementById('clear-batch-btn').addEventListener('click', () => this.clearBatch());

        // File upload
        const fileUploadArea = document.getElementById('file-upload-area');
        const fileInput = document.getElementById('file-input');

        fileUploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop
        fileUploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        fileUploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        fileUploadArea.addEventListener('drop', (e) => this.handleDrop(e));
    }

    async loadSampleData() {
        try {
            const response = await fetch('/api/sample-data');
            const data = await response.json();
            
            document.getElementById('activity-input').value = data.sample_csv;
            this.showNotification('Sample data loaded! ✨', 'success');
        } catch (error) {
            this.showNotification('Failed to load sample data', 'error');
        }
    }

    async classifySingle() {
        const input = document.getElementById('activity-input').value.trim();
        
        if (!input) {
            this.showNotification('Please enter activity data', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch('/api/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ data: input })
            });

            const result = await response.json();
            this.displaySingleResult(result);
            
            if (result.success) {
                this.showNotification('Activity classified successfully! 🎉', 'success');
            } else {
                this.showNotification('Classification failed: ' + result.reason, 'error');
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displaySingleResult(result) {
        const resultContainer = document.getElementById('single-result');
        const resultContent = document.getElementById('single-result-content');

        if (result.success) {
            const statusClass = result.status.toLowerCase().replace(' ', '-');
            const statusIcon = result.status === 'Malicious' ? '🚨' : '✅';
            
            resultContent.innerHTML = `
                <div class="result-item ${statusClass}">
                    <div class="result-status ${statusClass}">
                        <i class="fas fa-${result.status === 'Malicious' ? 'exclamation-triangle' : 'check-circle'}"></i>
                        ${statusIcon} ${result.status}
                    </div>
                    ${result.attack_type ? `<div class="result-attack-type">🎯 ${result.attack_type}</div>` : ''}
                    <div class="result-reason">💭 ${result.reason}</div>
                </div>
            `;
        } else {
            resultContent.innerHTML = `
                <div class="result-item error">
                    <div class="result-status error">
                        <i class="fas fa-times-circle"></i>
                        ❌ Error
                    </div>
                    <div class="result-reason">💭 ${result.reason}</div>
                </div>
            `;
        }

        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    async processBatch() {
        const fileInput = document.getElementById('file-input');
        const hasHeader = document.getElementById('has-header').checked;

        if (!fileInput.files || fileInput.files.length === 0) {
            this.showNotification('Please select files first', 'warning');
            return;
        }

        // Show progress container
        const progressContainer = document.getElementById('batch-progress');
        const resultContainer = document.getElementById('batch-result');
        progressContainer.style.display = 'block';
        resultContainer.style.display = 'none';

        try {
            const formData = new FormData();
            
            // Add all files
            for (let i = 0; i < fileInput.files.length; i++) {
                formData.append('files', fileInput.files[i]);
            }
            formData.append('has_header', hasHeader);

            const response = await fetch('/api/classify/batch', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                this.showNotification(`Batch processing started for ${result.total_files} files! 🚀`, 'success');
                this.trackBatchProgress(result.task_id);
            } else {
                this.showNotification('Failed to start batch processing: ' + result.error, 'error');
                progressContainer.style.display = 'none';
            }
        } catch (error) {
            this.showNotification('Network error: ' + error.message, 'error');
            progressContainer.style.display = 'none';
        }
    }

    async trackBatchProgress(taskId) {
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const currentFile = document.getElementById('current-file');
        
        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/batch/status/${taskId}`);
                const result = await response.json();
                
                if (result.success) {
                    const task = result.task;
                    
                    // Update progress bar
                    progressFill.style.width = `${task.progress}%`;
                    progressText.textContent = `${task.progress}% Complete (${task.processed_files}/${task.total_files} files)`;
                    currentFile.textContent = task.current_file ? `Processing: ${task.current_file}` : '';
                    
                    if (task.status === 'completed') {
                        // Get final results
                        await this.getBatchResults(taskId);
                        return;
                    } else if (task.status === 'error') {
                        this.showNotification('Batch processing failed: ' + task.error, 'error');
                        document.getElementById('batch-progress').style.display = 'none';
                        return;
                    }
                    
                    // Continue checking
                    setTimeout(checkProgress, 1000);
                } else {
                    this.showNotification('Failed to track progress: ' + result.error, 'error');
                    document.getElementById('batch-progress').style.display = 'none';
                }
            } catch (error) {
                this.showNotification('Error tracking progress: ' + error.message, 'error');
                document.getElementById('batch-progress').style.display = 'none';
            }
        };
        
        checkProgress();
    }

    async getBatchResults(taskId) {
        try {
            const response = await fetch(`/api/batch/results/${taskId}`);
            const result = await response.json();
            
            if (result.success) {
                this.displayBatchResult(result);
                this.showNotification(`Batch processing completed! Processed ${result.total_count} activities from ${result.files_processed} files 🎉`, 'success');
            } else {
                this.showNotification('Failed to get results: ' + result.error, 'error');
            }
        } catch (error) {
            this.showNotification('Error getting results: ' + error.message, 'error');
        } finally {
            document.getElementById('batch-progress').style.display = 'none';
        }
    }

    displayBatchResult(result) {
        const resultContainer = document.getElementById('batch-result');
        const resultContent = document.getElementById('batch-result-content');
        const batchStats = document.getElementById('batch-stats');

        if (!result.success) {
            resultContent.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>${result.error}</p>
                </div>
            `;
            resultContainer.style.display = 'block';
            return;
        }

        // Display statistics
        batchStats.innerHTML = `
            <div class="stat-item">
                <span class="stat-number">${result.total_count}</span>
                <span class="stat-label">Total Activities</span>
            </div>
            <div class="stat-item">
                <span class="stat-number malicious">${result.malicious_count}</span>
                <span class="stat-label">Malicious</span>
            </div>
            <div class="stat-item">
                <span class="stat-number non-malicious">${result.total_count - result.malicious_count - result.error_count}</span>
                <span class="stat-label">Non-Malicious</span>
            </div>
            <div class="stat-item">
                <span class="stat-number error">${result.error_count}</span>
                <span class="stat-label">Errors</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${result.files_processed || 1}</span>
                <span class="stat-label">Files Processed</span>
            </div>
        `;

        // Group results by file for better organization
        const resultsByFile = {};
        result.results.forEach(item => {
            const filename = item.filename || 'Unknown File';
            if (!resultsByFile[filename]) {
                resultsByFile[filename] = [];
            }
            resultsByFile[filename].push(item);
        });

        // Display results grouped by file
        resultContent.innerHTML = Object.entries(resultsByFile).map(([filename, fileResults]) => {
            const fileHeader = `
                <div class="file-results-header">
                    <h4><i class="fas fa-file"></i> ${filename}</h4>
                    <span class="file-result-count">${fileResults.length} activities</span>
                </div>
            `;
            
            const fileResultsHtml = fileResults.map(item => {
                if (!item.success) {
                    return `
                        <div class="result-item error">
                            <div class="result-filename">
                                <i class="fas fa-file"></i>
                                ${filename}
                            </div>
                            ${item.line_number ? `<div class="result-line-number">Line ${item.line_number}</div>` : ''}
                            <div class="result-status error">
                                <i class="fas fa-exclamation-triangle"></i>
                                Error
                            </div>
                            <div class="result-reason">${item.error}</div>
                        </div>
                    `;
                }

                const statusClass = item.status.toLowerCase().replace(' ', '-');
                const statusIcon = item.status === 'Malicious' ? 'fa-shield-alt' : 'fa-check-circle';
                
                return `
                    <div class="result-item ${statusClass}">
                        <div class="result-filename">
                            <i class="fas fa-file"></i>
                            ${filename}
                        </div>
                        ${item.line_number ? `<div class="result-line-number">Line ${item.line_number}</div>` : ''}
                        <div class="result-status ${statusClass}">
                            <i class="fas ${statusIcon}"></i>
                            ${item.status}
                        </div>
                        ${item.attack_type ? `<div class="result-attack-type">${item.attack_type}</div>` : ''}
                        <div class="result-reason">${item.reason}</div>
                    </div>
                `;
            }).join('');
            
            return fileHeader + fileResultsHtml;
        }).join('');

        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    handleFileSelect(event) {
        const files = Array.from(event.target.files);
        if (files.length > 0) {
            this.updateFileUploadArea(files);
            document.getElementById('process-batch-btn').disabled = false;
        }
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }

    handleDragLeave(event) {
        event.currentTarget.classList.remove('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = Array.from(event.dataTransfer.files);
        if (files.length > 0) {
            // Create a new FileList-like object
            const dt = new DataTransfer();
            files.forEach(file => dt.items.add(file));
            document.getElementById('file-input').files = dt.files;
            
            this.updateFileUploadArea(files);
            document.getElementById('process-batch-btn').disabled = false;
        }
    }

    updateFileUploadArea(files) {
        const uploadContent = document.querySelector('.upload-content');
        const fileList = document.getElementById('file-list');
        const fileListItems = document.getElementById('file-list-items');
        
        if (files.length === 1) {
            uploadContent.innerHTML = `
                <i class="fas fa-file-check"></i>
                <h3>File Selected: ${files[0].name}</h3>
                <p>Ready to process! Click "Process Batch" to analyze.</p>
            `;
            fileList.style.display = 'none';
        } else {
            uploadContent.innerHTML = `
                <i class="fas fa-files"></i>
                <h3>${files.length} Files Selected</h3>
                <p>Ready to process! Click "Process Batch" to analyze all files.</p>
            `;
            
            // Show file list
            fileListItems.innerHTML = '';
            files.forEach(file => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <i class="fas fa-file"></i>
                    <span>${file.name}</span>
                    <span class="file-size">(${this.formatFileSize(file.size)})</span>
                `;
                fileListItems.appendChild(li);
            });
            fileList.style.display = 'block';
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    clearSingle() {
        document.getElementById('activity-input').value = '';
        document.getElementById('single-result').style.display = 'none';
        this.showNotification('Single analysis cleared! ✨', 'info');
    }

    clearBatch() {
        document.getElementById('file-input').value = '';
        document.getElementById('process-batch-btn').disabled = true;
        document.getElementById('batch-result').style.display = 'none';
        
        // Reset upload area
        const uploadContent = document.querySelector('.upload-content');
        uploadContent.innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i>
            <h3>Drop your file here or click to browse</h3>
            <p>Supports CSV and JSON files</p>
        `;
        
        this.showNotification('Batch processing cleared! ✨', 'info');
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1001;
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
            animation: slideIn 0.3s ease;
            max-width: 400px;
        `;

        document.body.appendChild(notification);

        // Auto remove after 4 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'times-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getNotificationColor(type) {
        const colors = {
            'success': 'linear-gradient(45deg, #28a745, #20c997)',
            'error': 'linear-gradient(45deg, #dc3545, #e74c3c)',
            'warning': 'linear-gradient(45deg, #ffc107, #fd7e14)',
            'info': 'linear-gradient(45deg, #17a2b8, #6f42c1)'
        };
        return colors[type] || colors['info'];
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
`;
document.head.appendChild(style);

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CyberGuardApp();
});




