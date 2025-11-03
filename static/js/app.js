let selectedFiles = null;

class CyberGuardApp {
    constructor() {
        console.log('CyberGuardApp initializing...');
        this.initializeEventListeners();
        this.loadSampleData();
    }

    initializeEventListeners() {
        console.log('Setting up event listeners...');
        
        try {
            const classifyBtn = document.getElementById('classify-btn');
            const loadSampleBtn = document.getElementById('load-sample-btn');
            const clearBtn = document.getElementById('clear-btn');
            
            if (classifyBtn) classifyBtn.addEventListener('click', () => this.classifySingle());
            if (loadSampleBtn) loadSampleBtn.addEventListener('click', () => this.loadSampleData());
            if (clearBtn) clearBtn.addEventListener('click', () => this.clearSingle());

            const processBatchBtn = document.getElementById('process-batch-btn');
            const clearBatchBtn = document.getElementById('clear-batch-btn');
            
            if (processBatchBtn)
                processBatchBtn.addEventListener('click', () => this.processBatch());
            if (clearBatchBtn)
                clearBatchBtn.addEventListener('click', () => this.clearBatch());

            const fileUploadArea = document.getElementById('file-upload-area');
            const fileInput = document.getElementById('file-input');

            if (fileUploadArea && fileInput) {
                fileUploadArea.addEventListener('click', () => fileInput.click());
                fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

                fileUploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
                fileUploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
                fileUploadArea.addEventListener('drop', (e) => this.handleDrop(e));
            } else {
                console.error('File upload elements not found!');
            }
        } catch (error) {
            console.error('Error setting up event listeners:', error);
        }
    }

    async loadSampleData() {
        try {
            const response = await fetch('/api/sample-data');
            const data = await response.json();
            const activityInput = document.getElementById('activity-input');
            if (activityInput) {
                activityInput.value = data.sample_csv;
                this.showNotification('Sample data loaded! ✨', 'success');
            }
        } catch (error) {
            console.error('Error loading sample data:', error);
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
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data: input })
            });

            const result = await response.json();
            this.displaySingleResult(result);
            if (result.success)
                this.showNotification('Activity classified successfully! 🎉', 'success');
            else
                this.showNotification('Classification failed: ' + result.reason, 'error');
        } catch (error) {
            console.error('Classification error:', error);
            this.showNotification('Network error: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displaySingleResult(result) {
        const resultContainer = document.getElementById('single-result');
        const resultContent = document.getElementById('single-result-content');

        if (!resultContainer || !resultContent) {
            console.error('Result containers not found');
            return;
        }

        let statusClass = 'status-error';
        let statusIcon = 'fa-exclamation-triangle';
        
        if (result.success && result.status === 'Malicious') {
            statusClass = 'status-malicious';
            statusIcon = 'fa-skull-crossbones';
        } else if (result.success && result.status === 'Non-malicious') {
            statusClass = 'status-non-malicious';
            statusIcon = 'fa-shield-alt';
        }

        resultContent.innerHTML = `
            <div class="result-item ${statusClass}">
                <div class="result-header">
                    <div class="result-status">
                        <i class="fas ${statusIcon}"></i>
                        ${result.status || 'Error'}
                    </div>
                    ${result.attack_type ? `<div class="result-attack-type">${result.attack_type}</div>` : ''}
                </div>
                <div class="result-reason">${result.reason || 'Unknown error'}</div>
            </div>
        `;

        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    async processBatch() {
        console.log('processBatch called!');
        const hasHeader = document.getElementById('has-header').checked;

        if (!selectedFiles || selectedFiles.length === 0) {
            this.showNotification('Please select files first', 'warning');
            return;
        }

        console.log(`Processing ${selectedFiles.length} files...`);

        const progressContainer = document.getElementById('batch-progress');
        const resultContainer = document.getElementById('batch-result');
        if (progressContainer) progressContainer.style.display = 'block';
        if (resultContainer) resultContainer.style.display = 'none';

        try {
            const formData = new FormData();
            for (let i = 0; i < selectedFiles.length; i++) {
                formData.append('files', selectedFiles[i]);
                console.log(`Added file: ${selectedFiles[i].name}`);
            }
            formData.append('has_header', hasHeader);

            const response = await fetch('/api/classify/batch', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            console.log('Batch response:', result);
            
            if (result.success) {
                this.showNotification(`Batch processing started for ${result.total_files} files! 🚀`, 'success');
                this.trackBatchProgress(result.task_id);
            } else {
                this.showNotification('Failed to start batch processing: ' + result.error, 'error');
                if (progressContainer) progressContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Batch processing error:', error);
            this.showNotification('Network error: ' + error.message, 'error');
            if (progressContainer) progressContainer.style.display = 'none';
        }
    }

    async trackBatchProgress(taskId) {
        console.log(`Tracking progress for task: ${taskId}`);
        
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const currentFile = document.getElementById('current-file');
        
        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/batch/status/${taskId}`);
                const result = await response.json();
                
                if (result.success) {
                    const task = result.task;
                    console.log('Progress update:', task);
                    
                    if (progressFill) progressFill.style.width = `${task.progress}%`;
                    if (progressText)
                        progressText.textContent = `${task.progress}% Complete (${task.processed_files}/${task.total_files} files)`;
                    if (currentFile)
                        currentFile.textContent = task.current_file ? `Processing: ${task.current_file}` : '';
                    
                    if (task.status === 'completed') {
                        await this.getBatchResults(taskId);
                        return;
                    } else if (task.status === 'error') {
                        this.showNotification('Batch processing failed: ' + task.error, 'error');
                        document.getElementById('batch-progress').style.display = 'none';
                        return;
                    }
                    setTimeout(checkProgress, 1000);
                } else {
                    this.showNotification('Failed to track progress: ' + result.error, 'error');
                    document.getElementById('batch-progress').style.display = 'none';
                }
            } catch (error) {
                console.error('Progress tracking error:', error);
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
                this.showNotification(`Batch completed! Processed ${result.total_count} activities 🎉`, 'success');
            } else {
                this.showNotification('Failed to get results: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Error getting results:', error);
            this.showNotification('Error getting results: ' + error.message, 'error');
        } finally {
            const progressContainer = document.getElementById('batch-progress');
            if (progressContainer) progressContainer.style.display = 'none';
        }
    }

    displayBatchResult(result) {
        const resultContainer = document.getElementById('batch-result');
        const resultContent = document.getElementById('batch-result-content');
        const batchStats = document.getElementById('batch-stats');

        if (!resultContainer || !resultContent || !batchStats) {
            console.error('Batch result containers not found');
            return;
        }

        const nonMaliciousCount = result.total_count - result.malicious_count - result.error_count;
        batchStats.innerHTML = `
            <div class="stat-item"><span class="stat-number">${result.total_count}</span><span class="stat-label">Total</span></div>
            <div class="stat-item"><span class="stat-number malicious">${result.malicious_count}</span><span class="stat-label">Malicious</span></div>
            <div class="stat-item"><span class="stat-number non-malicious">${nonMaliciousCount}</span><span class="stat-label">Non-Malicious</span></div>
            <div class="stat-item"><span class="stat-number error">${result.error_count}</span><span class="stat-label">Errors</span></div>
        `;

        const fileGroups = {};
        result.results.forEach(item => {
            if (!fileGroups[item.filename]) fileGroups[item.filename] = [];
            fileGroups[item.filename].push(item);
        });

        resultContent.innerHTML = Object.keys(fileGroups).map(filename => {
            const items = fileGroups[filename].map(item => `
                <div class="result-item ${item.status === 'Malicious' ? 'status-malicious' : 'status-non-malicious'}">
                    <div class="result-header">
                        <div class="result-line-number">Line ${item.line_number || ''}</div>
                        <div class="result-status">
                            <i class="fas ${item.status === 'Malicious' ? 'fa-skull-crossbones' : 'fa-shield-alt'}"></i>
                            ${item.status}
                        </div>
                    </div>
                    <div class="result-reason">${item.reason || ''}</div>
                </div>
            `).join('');
            return `<h4><i class="fas fa-file"></i> ${filename}</h4>${items}`;
        }).join('');

        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
    }

    handleFileSelect(event) {
        console.log('File selection event:', event.target.files);
        selectedFiles = event.target.files; 
        const files = Array.from(selectedFiles);
        if (files.length > 0) {
            this.updateFileUploadArea(files);
            const processBtn = document.getElementById('process-batch-btn');
            if (processBtn) processBtn.disabled = false;
        }
    }

    handleDragOver(event) { event.preventDefault(); event.currentTarget.classList.add('dragover'); }
    handleDragLeave(event) { event.currentTarget.classList.remove('dragover'); }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        const files = Array.from(event.dataTransfer.files);
        if (files.length > 0) {
            selectedFiles = files; 
            this.updateFileUploadArea(files);
            const processBtn = document.getElementById('process-batch-btn');
            if (processBtn) processBtn.disabled = false;
        }
    }

    updateFileUploadArea(files) {
        const uploadContent = document.querySelector('.upload-content');
        const fileList = document.getElementById('file-list');
        const fileListItems = document.getElementById('file-list-items');
        
        if (!uploadContent) return;

        if (files.length === 1) {
            uploadContent.innerHTML = `
                <i class="fas fa-file-check"></i>
                <h3>File Selected: ${files[0].name}</h3>
                <p>Ready to process! Click "Process Batch" to analyze.</p>
            `;
            if (fileList) fileList.style.display = 'none';
        } else {
            uploadContent.innerHTML = `
                <i class="fas fa-files"></i>
                <h3>${files.length} Files Selected</h3>
                <p>Ready to process! Click "Process Batch" to analyze all files.</p>
            `;
            if (fileList && fileListItems) {
                fileListItems.innerHTML = '';
                files.forEach(file => {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-file"></i><span>${file.name}</span>`;
                    fileListItems.appendChild(li);
                });
                fileList.style.display = 'block';
            }
        }
    }

    clearSingle() {
        const activityInput = document.getElementById('activity-input');
        const singleResult = document.getElementById('single-result');
        if (activityInput) activityInput.value = '';
        if (singleResult) singleResult.style.display = 'none';
        this.showNotification('Single analysis cleared! ✨', 'info');
    }

    clearBatch() {
        console.log('clearBatch called!');
        selectedFiles = null; 
        const fileInput = document.getElementById('file-input');
        const processBtn = document.getElementById('process-batch-btn');
        const batchResult = document.getElementById('batch-result');
        const fileList = document.getElementById('file-list');
        const uploadContent = document.querySelector('.upload-content');
        
        if (fileInput) fileInput.value = '';
        if (processBtn) processBtn.disabled = true;
        if (batchResult) batchResult.style.display = 'none';
        if (fileList) fileList.style.display = 'none';
        if (uploadContent)
            uploadContent.innerHTML = `
                <i class="fas fa-cloud-upload-alt"></i>
                <h3>Drop your files here or click to browse</h3>
                <p>Supports CSV and JSON files (multiple files allowed)</p>
            `;
        this.showNotification('Batch processing cleared! ✨', 'info');
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = show ? 'flex' : 'none';
    }

    showNotification(message, type = 'info') {
        console.log(`Notification: ${message} (${type})`);
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white; padding: 15px 20px; border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1001; font-family: 'Poppins', sans-serif;
            animation: slideIn 0.3s ease; max-width: 400px;
        `;
        document.body.appendChild(notification);
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-circle';
            case 'warning': return 'exclamation-triangle';
            default: return 'info-circle';
        }
    }

    getNotificationColor(type) {
        switch (type) {
            case 'success': return 'linear-gradient(135deg, #4CAF50, #45a049)';
            case 'error': return 'linear-gradient(135deg, #f44336, #da190b)';
            case 'warning': return 'linear-gradient(135deg, #ff9800, #f57c00)';
            default: return 'linear-gradient(135deg, #2196F3, #1976D2)';
        }
    }
}

const style = document.createElement('style');
style.textContent = `
@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
@keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
.notification-content { display: flex; align-items: center; gap: 10px; }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing CyberGuardApp...');
    new CyberGuardApp();
});