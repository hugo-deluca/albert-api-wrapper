// Shared JavaScript utilities for Albert API Manager

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Toast notification system
function showToast(message, type = 'success') {
    // Remove any existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    
    const icon = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    }[type] || 'ℹ';
    
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('toast-show'), 10);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('toast-show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Custom confirm dialog
function showConfirm(message, onConfirm, onCancel = null) {
    const overlay = document.createElement('div');
    overlay.className = 'custom-modal-overlay';
    overlay.innerHTML = `
        <div class="custom-modal custom-confirm">
            <div class="custom-modal-header">
                <h3>Confirmation</h3>
            </div>
            <div class="custom-modal-body">
                <p>${message}</p>
            </div>
            <div class="custom-modal-footer">
                <button class="btn btn-secondary" onclick="this.closest('.custom-modal-overlay').remove(); ${onCancel ? 'window.modalCancelCallback()' : ''}">
                    Annuler
                </button>
                <button class="btn btn-danger" onclick="this.closest('.custom-modal-overlay').remove(); window.modalConfirmCallback()">
                    Confirmer
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    setTimeout(() => overlay.classList.add('show'), 10);
    
    // Store callbacks globally (simple approach)
    window.modalConfirmCallback = () => {
        if (onConfirm) onConfirm();
        delete window.modalConfirmCallback;
        delete window.modalCancelCallback;
    };
    
    if (onCancel) {
        window.modalCancelCallback = () => {
            onCancel();
            delete window.modalConfirmCallback;
            delete window.modalCancelCallback;
        };
    }
    
    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
            if (onCancel) onCancel();
        }
    });
}

// Custom prompt dialog
function showPrompt(message, defaultValue = '', onSubmit, onCancel = null) {
    const overlay = document.createElement('div');
    overlay.className = 'custom-modal-overlay';
    overlay.innerHTML = `
        <div class="custom-modal custom-prompt">
            <div class="custom-modal-header">
                <h3>Saisie requise</h3>
            </div>
            <div class="custom-modal-body">
                <p>${message}</p>
                <input type="text" class="prompt-input" value="${defaultValue}" autofocus>
            </div>
            <div class="custom-modal-footer">
                <button class="btn btn-secondary prompt-cancel">Annuler</button>
                <button class="btn btn-primary prompt-submit">OK</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    setTimeout(() => overlay.classList.add('show'), 10);
    
    const input = overlay.querySelector('.prompt-input');
    const submitBtn = overlay.querySelector('.prompt-submit');
    const cancelBtn = overlay.querySelector('.prompt-cancel');
    
    const submit = () => {
        const value = input.value;
        overlay.remove();
        if (onSubmit) onSubmit(value);
    };
    
    const cancel = () => {
        overlay.remove();
        if (onCancel) onCancel();
    };
    
    submitBtn.addEventListener('click', submit);
    cancelBtn.addEventListener('click', cancel);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submit();
    });
    
    // Focus input
    setTimeout(() => input.focus(), 100);
    
    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) cancel();
    });
}

// Loading overlay
function showLoading(message = 'Chargement...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'globalLoadingOverlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p>${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
    setTimeout(() => overlay.classList.add('show'), 10);
    return overlay;
}

function hideLoading() {
    const overlay = document.getElementById('globalLoadingOverlay');
    if (overlay) {
        overlay.classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    }
}

// Utility function for API calls with error handling
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format date
function formatDate(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export utilities
window.AlbertUtils = {
    showToast,
    showConfirm,
    showPrompt,
    showLoading,
    hideLoading,
    apiCall,
    formatFileSize,
    formatDate,
    debounce
};

// Legacy aliases for backward compatibility
window.showNotification = showToast;
window.confirmAction = (message) => new Promise(resolve => {
    showConfirm(message, () => resolve(true), () => resolve(false));
});