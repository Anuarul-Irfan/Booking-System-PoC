console.log('Script.js loaded');

// Add fade-in animation to main content
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    
    const mainContent = document.querySelector('.container');
    if (mainContent) {
        console.log('Main content found');
        mainContent.classList.add('fade-in');
    } else {
        console.log('Main content not found');
    }

    // Handle add slot form
    const addSlotForm = document.getElementById('addSlotForm');
    console.log('Looking for add slot form...');
    if (addSlotForm) {
        console.log('Add slot form found');
        
        // Log form elements
        console.log('Form action:', addSlotForm.action);
        console.log('Form method:', addSlotForm.method);
        console.log('Form elements:', {
            time: addSlotForm.querySelector('#time'),
            product: addSlotForm.querySelector('#product'),
            submitButton: addSlotForm.querySelector('button[type="submit"]')
        });
        
        // Handle form submission
        addSlotForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission
            console.log('Form submitted');
            
            const formData = new FormData(this);
            const time = formData.get('time');
            const product = formData.get('product');
            console.log('Form data:', { time, product });
            
            if (!time || !product) {
                console.error('Missing required fields');
                showToast('Please select both time and product type', 'error');
                return;
            }
            
            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                console.log('Submit button found');
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Adding...';
                submitButton.disabled = true;
                
                // Submit form using fetch
                console.log('Sending request to:', this.action);
                fetch(this.action, {
                    method: this.method,
                    body: formData
                })
                .then(response => {
                    console.log('Response status:', response.status);
                    console.log('Response headers:', Object.fromEntries(response.headers.entries()));
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.text();
                })
                .then(html => {
                    console.log('Response received, length:', html.length);
                    // Show success toast
                    showToast('Slot added successfully!', 'success');
                    
                    // Clear form
                    this.reset();
                    console.log('Form cleared');
                    
                    // Reload the page after a short delay
                    setTimeout(() => {
                        console.log('Reloading page...');
                        window.location.reload();
                    }, 1500);
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error adding slot. Please try again.', 'error');
                })
                .finally(() => {
                    // Reset button state
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                    console.log('Button state reset');
                });
            } else {
                console.error('Submit button not found');
                showToast('Error: Submit button not found', 'error');
            }
        });
    } else {
        console.error('Add slot form not found');
        // Log all forms on the page
        const allForms = document.querySelectorAll('form');
        console.log('All forms on page:', allForms.length);
        allForms.forEach((form, index) => {
            console.log(`Form ${index + 1}:`, {
                id: form.id,
                action: form.action,
                method: form.method,
                elements: Array.from(form.elements).map(el => ({
                    type: el.type,
                    name: el.name,
                    id: el.id
                }))
            });
        });
    }

    // Handle flash messages and show toast
    const flashMessages = document.querySelectorAll('.flash-message');
    console.log('Flash messages found:', flashMessages.length);
    flashMessages.forEach(message => {
        const category = message.dataset.category;
        const messageText = message.dataset.message;
        console.log('Flash message:', category, messageText);
        
        if (category === 'success') {
            const toast = new bootstrap.Toast(document.getElementById('successToast'));
            document.getElementById('toastMessage').textContent = messageText;
            toast.show();
        }
    });
});

// Add confirmation for logout
document.querySelectorAll('a[href="/logout"]').forEach(link => {
    console.log('Setting up logout confirmation');
    link.addEventListener('click', function(e) {
        console.log('Logout link clicked');
        if (!confirm('Are you sure you want to logout?')) {
            console.log('Logout cancelled');
            e.preventDefault();
        } else {
            console.log('Logout confirmed');
        }
    });
});

// Add hover effect to table rows
document.querySelectorAll('table tbody tr').forEach(row => {
    row.addEventListener('mouseenter', function() {
        this.style.backgroundColor = '#f8fafc';
        this.style.transition = 'background-color 0.2s ease';
    });
    
    row.addEventListener('mouseleave', function() {
        this.style.backgroundColor = '';
    });
});

// Auto-dismiss alerts after 5 seconds
document.querySelectorAll('.alert').forEach(alert => {
    console.log('Setting up auto-dismiss for alert');
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity 0.5s ease';
        setTimeout(() => alert.remove(), 500);
    }, 5000);
});

// Helper function to show toasts
function showToast(message, type = 'success') {
    console.log('Showing toast:', { message, type });
    const toast = new bootstrap.Toast(document.getElementById('successToast'));
    const toastElement = document.getElementById('successToast');
    const messageElement = document.getElementById('toastMessage');
    
    // Set message
    messageElement.textContent = message;
    
    // Set styling
    toastElement.classList.remove('bg-success', 'bg-danger');
    toastElement.classList.add(type === 'success' ? 'bg-success' : 'bg-danger');
    
    // Show toast
    toast.show();
    console.log('Toast shown');
} 