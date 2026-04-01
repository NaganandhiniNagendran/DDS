// Main JavaScript file for Driver Drowsiness Detection System

// Update current time
function updateCurrentTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    const dateString = now.toLocaleDateString('en-US', { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
    
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = `${dateString} ${timeString}`;
    }
}

// Initialize time updates
document.addEventListener('DOMContentLoaded', function() {
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize sidebar toggle for mobile
    initializeSidebarToggle();
    
    // Initialize smooth scrolling
    initializeSmoothScrolling();
});

// Initialize tooltips
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.position = 'absolute';
            tooltip.style.background = 'var(--card-bg)';
            tooltip.style.color = 'var(--text-primary)';
            tooltip.style.padding = '0.5rem';
            tooltip.style.borderRadius = '0.25rem';
            tooltip.style.fontSize = '0.875rem';
            tooltip.style.whiteSpace = 'nowrap';
            tooltip.style.zIndex = '1000';
            tooltip.style.pointerEvents = 'none';
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
            
            this.tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                this.tooltip.remove();
                this.tooltip = null;
            }
        });
    });
}

// Initialize sidebar toggle for mobile
function initializeSidebarToggle() {
    // Create mobile menu button if it doesn't exist
    if (!document.querySelector('.mobile-menu-toggle')) {
        const mobileMenuButton = document.createElement('button');
        mobileMenuButton.className = 'mobile-menu-toggle';
        mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
        mobileMenuButton.style.cssText = `
            display: none;
            position: fixed;
            top: 1rem;
            left: 1rem;
            z-index: 1001;
            width: 40px;
            height: 40px;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            color: var(--text-primary);
            cursor: pointer;
            align-items: center;
            justify-content: center;
        `;
        
        document.body.appendChild(mobileMenuButton);
        
        mobileMenuButton.addEventListener('click', function() {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('active');
        });
        
        // Show on mobile screens
        const checkScreenSize = () => {
            if (window.innerWidth <= 768) {
                mobileMenuButton.style.display = 'flex';
            } else {
                mobileMenuButton.style.display = 'none';
                document.querySelector('.sidebar').classList.remove('active');
            }
        };
        
        checkScreenSize();
        window.addEventListener('resize', checkScreenSize);
    }
}

// Initialize smooth scrolling
function initializeSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Utility functions
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// API helper functions
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Notification system
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 1rem;
        right: 1rem;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        padding: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        min-width: 300px;
        z-index: 2000;
        animation: slideInRight 0.3s ease;
    `;
    
    // Add notification styles
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                flex: 1;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: var(--text-secondary);
                cursor: pointer;
                padding: 0.25rem;
                border-radius: 0.25rem;
                transition: all 0.2s ease;
            }
            
            .notification-close:hover {
                background: var(--secondary-bg);
                color: var(--text-primary);
            }
            
            .notification-success { border-left: 4px solid var(--accent-green); }
            .notification-warning { border-left: 4px solid var(--accent-yellow); }
            .notification-error { border-left: 4px solid var(--accent-red); }
            .notification-info { border-left: 4px solid var(--accent-blue); }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Auto remove
    const removeNotification = () => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    };
    
    setTimeout(removeNotification, duration);
    
    // Manual close
    notification.querySelector('.notification-close').addEventListener('click', removeNotification);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'warning': return 'exclamation-triangle';
        case 'error': return 'times-circle';
        case 'info': return 'info-circle';
        default: return 'info-circle';
    }
}

// Loading states
function showLoading(element, text = 'Loading...') {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    element.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <span>${text}</span>
        </div>
    `;
    element.disabled = true;
}

function hideLoading(element) {
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    }
    element.disabled = false;
}

// Add loading spinner styles
if (!document.querySelector('#loading-styles')) {
    const style = document.createElement('style');
    style.id = 'loading-styles';
    style.textContent = `
        .loading-spinner {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .fa-spin {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}

// Local storage helpers
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function getLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return defaultValue;
    }
}

function removeLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Error removing from localStorage:', error);
    }
}

// Chart helper functions
function createSimpleLineChart(canvas, data, options = {}) {
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth;
    const height = canvas.height = 200;
    
    const defaults = {
        color: '#3b82f6',
        lineWidth: 2,
        backgroundColor: 'rgba(59, 130, 246, 0.1)'
    };
    
    const config = { ...defaults, ...options };
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw grid
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 0.5;
    
    for (let i = 0; i <= 5; i++) {
        const y = (height / 5) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
    
    // Draw line chart
    if (data.length > 0) {
        const maxValue = Math.max(...data);
        const minValue = Math.min(...data);
        const range = maxValue - minValue || 1;
        
        ctx.strokeStyle = config.color;
        ctx.lineWidth = config.lineWidth;
        ctx.beginPath();
        
        data.forEach((value, index) => {
            const x = (width / (data.length - 1)) * index;
            const y = height - ((value - minValue) / range) * height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Fill area under line
        ctx.fillStyle = config.backgroundColor;
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        ctx.fill();
    }
}

function createSimpleBarChart(canvas, data, options = {}) {
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth;
    const height = canvas.height = 200;
    
    const defaults = {
        barColor: '#3b82f6',
        barSpacing: 10
    };
    
    const config = { ...defaults, ...options };
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    if (data.length > 0) {
        const maxValue = Math.max(...data);
        const barWidth = (width - (config.barSpacing * (data.length + 1))) / data.length;
        
        data.forEach((value, index) => {
            const barHeight = (value / maxValue) * (height - 20);
            const x = config.barSpacing + (index * (barWidth + config.barSpacing));
            const y = height - barHeight - 10;
            
            ctx.fillStyle = config.barColor;
            ctx.fillRect(x, y, barWidth, barHeight);
        });
    }
}

// Export functions for use in other scripts
window.DDDS = {
    apiRequest,
    showNotification,
    showLoading,
    hideLoading,
    formatDuration,
    formatBytes,
    debounce,
    throttle,
    setLocalStorage,
    getLocalStorage,
    removeLocalStorage,
    createSimpleLineChart,
    createSimpleBarChart
};
