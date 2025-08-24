// Main JavaScript file for E-Library System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Search form enhancement
    const searchForm = document.querySelector('form[action*="books"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="query"]');
        const categorySelect = searchForm.querySelector('select[name="category"]');
        
        // Auto-submit on category change
        if (categorySelect) {
            categorySelect.addEventListener('change', function() {
                searchForm.submit();
            });
        }

        // Enter key support for search
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    searchForm.submit();
                }
            });
        }
    }

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const fileName = file.name;
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                
                // Create or update file info display
                let fileInfo = input.parentNode.querySelector('.file-info');
                if (!fileInfo) {
                    fileInfo = document.createElement('div');
                    fileInfo.className = 'file-info mt-2 p-2 bg-secondary rounded';
                    input.parentNode.appendChild(fileInfo);
                }
                
                fileInfo.innerHTML = `
                    <small>
                        <i class="fas fa-file me-1"></i>
                        <strong>${fileName}</strong> (${fileSize} MB)
                    </small>
                `;
            }
        });
    });

    // Confirmation dialogs
    const deleteLinks = document.querySelectorAll('a[onclick*="confirm"]');
    deleteLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const confirmed = confirm('Are you sure you want to delete this item? This action cannot be undone.');
            if (confirmed) {
                window.location.href = link.href;
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Add loading state to submit buttons
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            submitButtons.forEach(function(button) {
                button.disabled = true;
                const originalText = button.textContent || button.value;
                
                if (button.tagName === 'BUTTON') {
                    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                } else {
                    button.value = 'Processing...';
                }

                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    button.disabled = false;
                    if (button.tagName === 'BUTTON') {
                        button.textContent = originalText;
                    } else {
                        button.value = originalText;
                    }
                }, 10000);
            });
        });
    });

    // Download tracking
    const downloadLinks = document.querySelectorAll('a[href*="/download/"]');
    downloadLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Add visual feedback
            const originalText = link.innerHTML;
            link.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Downloading...';
            link.classList.add('disabled');
            
            // Reset after 3 seconds
            setTimeout(function() {
                link.innerHTML = originalText;
                link.classList.remove('disabled');
            }, 3000);
        });
    });

    // Search suggestions (simple implementation)
    const searchInputs = document.querySelectorAll('input[name="query"]');
    searchInputs.forEach(function(input) {
        let searchTimeout;
        
        input.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                hideSuggestions(input);
                return;
            }
            
            searchTimeout = setTimeout(function() {
                // In a real implementation, this would make an AJAX call
                // For now, we'll just show a simple message
                showSearchHint(input, query);
            }, 300);
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target)) {
                hideSuggestions(input);
            }
        });
    });

    function showSearchHint(input, query) {
        hideSuggestions(input);
        
        const hint = document.createElement('div');
        hint.className = 'search-hint position-absolute bg-dark border rounded p-2 mt-1';
        hint.style.zIndex = '1000';
        hint.style.fontSize = '0.875rem';
        hint.innerHTML = `<small class="text-muted">Searching for "${query}"... Press Enter to search</small>`;
        
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(hint);
        
        setTimeout(function() {
            hideSuggestions(input);
        }, 3000);
    }

    function hideSuggestions(input) {
        const existing = input.parentNode.querySelector('.search-hint');
        if (existing) {
            existing.remove();
        }
    }

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Lazy loading for images (if any)
    const images = document.querySelectorAll('img[data-src]');
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // Table sorting (basic implementation)
    const sortableHeaders = document.querySelectorAll('th[data-sortable]');
    sortableHeaders.forEach(function(header) {
        header.style.cursor = 'pointer';
        header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
        
        header.addEventListener('click', function() {
            // This is a simplified implementation
            // In a real app, you'd want to implement proper table sorting
            console.log('Sorting by:', header.textContent);
        });
    });

    // Print functionality
    const printButtons = document.querySelectorAll('[data-print]');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    // Back to top button
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle';
    backToTopButton.style.display = 'none';
    backToTopButton.style.zIndex = '1000';
    backToTopButton.setAttribute('title', 'Back to top');
    
    document.body.appendChild(backToTopButton);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

// Utility functions
function showToast(message, type = 'info') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(function() {
        toast.remove();
    }, 3000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Export functions for use in other scripts
window.ELibrary = {
    showToast,
    formatFileSize
};
