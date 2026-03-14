// Main JavaScript File

// Initialize AOS Animation
AOS.init({
    duration: 1000,
    once: true,
    offset: 100
});

// Navbar Scroll Effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Back to Top Button
const backToTop = document.getElementById('backToTop');

window.addEventListener('scroll', function() {
    if (window.scrollY > 300) {
        backToTop.classList.add('show');
    } else {
        backToTop.classList.remove('show');
    }
});

backToTop.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// Auto Dismiss Alerts
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Save Notice Function
function saveNotice(noticeId, button) {
    fetch(`/save_notice/${noticeId}`)
        .then(response => response.json())
        .then(data => {
            if (data.saved) {
                button.classList.add('saved');
                button.innerHTML = '<i class="fas fa-heart"></i>';
                showNotification('Notice saved successfully!', 'success');
            } else {
                button.classList.remove('saved');
                button.innerHTML = '<i class="far fa-heart"></i>';
                showNotification('Notice removed from saved', 'info');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred. Please try again.', 'danger');
        });
}

// Share Notice Function
function shareNotice(noticeId) {
    fetch(`/share_notice/${noticeId}`)
        .then(response => response.json())
        .then(data => {
            if (navigator.share) {
                navigator.share({
                    title: data.title,
                    text: data.description,
                    url: data.url
                }).catch(console.error);
            } else {
                // Fallback - copy to clipboard
                navigator.clipboard.writeText(data.url).then(() => {
                    showNotification('Notice link copied to clipboard!', 'success');
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to share notice', 'danger');
        });
}

// Show Notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                        type === 'danger' ? 'fa-exclamation-circle' : 
                        'fa-info-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.flash-messages');
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// Image Preview
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            preview.src = e.target.result;
            preview.style.display = 'block';
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Search Function
function searchNotices() {
    const searchInput = document.getElementById('searchInput');
    const searchTerm = searchInput.value.toLowerCase();
    const noticeCards = document.querySelectorAll('.notice-card');
    
    noticeCards.forEach(card => {
        const title = card.querySelector('.notice-title').textContent.toLowerCase();
        const description = card.querySelector('.notice-description').textContent.toLowerCase();
        
        if (title.includes(searchTerm) || description.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Filter by Category
function filterByCategory(category) {
    const noticeCards = document.querySelectorAll('.notice-card');
    
    noticeCards.forEach(card => {
        const cardCategory = card.dataset.category;
        
        if (category === 'all' || cardCategory === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Update active filter
    const filterLinks = document.querySelectorAll('.filter-list a');
    filterLinks.forEach(link => {
        link.classList.remove('active');
        if (link.dataset.category === category) {
            link.classList.add('active');
        }
    });
}

// Load More Notices (Infinite Scroll)
let page = 1;
let loading = false;

window.addEventListener('scroll', function() {
    if (loading) return;
    
    const scrollHeight = document.documentElement.scrollHeight;
    const scrollTop = document.documentElement.scrollTop;
    const clientHeight = document.documentElement.clientHeight;
    
    if (scrollTop + clientHeight >= scrollHeight - 100) {
        loadMoreNotices();
    }
});

function loadMoreNotices() {
    loading = true;
    page++;
    
    fetch(`/api/notices?page=${page}`)
        .then(response => response.json())
        .then(data => {
            if (data.notices.length > 0) {
                appendNotices(data.notices);
                loading = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loading = false;
        });
}

function appendNotices(notices) {
    const container = document.querySelector('.notice-grid');
    
    notices.forEach(notice => {
        const html = createNoticeCard(notice);
        container.insertAdjacentHTML('beforeend', html);
    });
}

// Countdown Timer for Expiring Notices
function updateCountdowns() {
    const countdowns = document.querySelectorAll('.countdown');
    
    countdowns.forEach(countdown => {
        const expiryDate = new Date(countdown.dataset.expiry);
        const now = new Date();
        const diff = expiryDate - now;
        
        if (diff > 0) {
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            
            countdown.innerHTML = `${days}d ${hours}h ${minutes}m remaining`;
        } else {
            countdown.innerHTML = 'Expired';
            countdown.closest('.notice-card').style.opacity = '0.5';
        }
    });
}

// Update countdowns every minute
setInterval(updateCountdowns, 60000);

// Dark Mode Toggle
function toggleDarkMode() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    
    if (currentTheme === 'dark') {
        html.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    } else {
        html.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    }
}

// Load saved theme
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
});

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Initialize popovers
document.addEventListener('DOMContentLoaded', function() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Handle responsive tables
document.addEventListener('DOMContentLoaded', function() {
    const tables = document.querySelectorAll('.table-responsive');
    tables.forEach(table => {
        if (table.scrollWidth > table.clientWidth) {
            table.classList.add('has-scroll');
        }
    });
});

// Print notice function
function printNotice() {
    window.print();
}

// Export to PDF (using browser's print to PDF)
function exportToPDF() {
    window.print();
}

// Mark notification as read
function markAsRead(notificationId) {
    fetch(`/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const notification = document.querySelector(`[data-notification-id="${notificationId}"]`);
            notification.classList.remove('unread');
        }
    });
}

// Mark all notifications as read
function markAllAsRead() {
    fetch('/notifications/read-all', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelectorAll('.notification-item').forEach(item => {
                item.classList.remove('unread');
            });
            document.querySelector('.notification-badge').style.display = 'none';
        }
    });
}

// Delete notice with confirmation
function deleteNotice(noticeId) {
    if (confirm('Are you sure you want to delete this notice? This action cannot be undone.')) {
        fetch(`/admin/delete_notice/${noticeId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`[data-notice-id="${noticeId}"]`).remove();
                showNotification('Notice deleted successfully', 'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to delete notice', 'danger');
        });
    }
}

// Bulk delete notices
function bulkDelete() {
    const selected = document.querySelectorAll('.notice-checkbox:checked');
    const ids = Array.from(selected).map(cb => cb.value);
    
    if (ids.length === 0) {
        showNotification('Please select notices to delete', 'warning');
        return;
    }
    
    if (confirm(`Are you sure you want to delete ${ids.length} notice(s)?`)) {
        fetch('/admin/bulk-delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ids: ids })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

// Export notices to CSV
function exportNotices() {
    fetch('/admin/export-notices')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'notices.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        });
}

// Import notices from CSV
function importNotices() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showNotification('Please select a file to import', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/admin/import-notices', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`${data.count} notices imported successfully`, 'success');
            location.reload();
        } else {
            showNotification('Failed to import notices', 'danger');
        }
    });
}

// Add this to your existing JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const priorityCards = document.querySelectorAll('.priority-card');
    const priorityInputs = document.querySelectorAll('input[name="priority"]');
    
    priorityCards.forEach((card, index) => {
        card.addEventListener('click', function() {
            // Remove selected class from all cards
            priorityCards.forEach(c => c.classList.remove('selected'));
            // Add selected class to clicked card
            this.classList.add('selected');
            // Check the corresponding radio input
            priorityInputs[index].checked = true;
        });
    });
});