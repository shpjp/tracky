// Real-time duplicate checking for registration form
// Add this to your registration template for better user experience

function checkDuplicateAccount() {
    const usernameField = document.querySelector('input[name="username"]');
    const emailField = document.querySelector('input[name="email"]');
    
    // Create feedback elements
    function createFeedbackElement(field) {
        const existing = field.parentElement.querySelector('.duplicate-feedback');
        if (existing) existing.remove();
        
        const feedback = document.createElement('div');
        feedback.className = 'duplicate-feedback text-sm mt-1 flex items-center';
        field.parentElement.appendChild(feedback);
        return feedback;
    }
    
    // Check username availability
    if (usernameField) {
        let usernameTimeout;
        usernameField.addEventListener('input', function() {
            clearTimeout(usernameTimeout);
            const feedback = createFeedbackElement(this);
            const username = this.value.trim();
            
            if (username.length < 3) {
                feedback.innerHTML = '';
                return;
            }
            
            feedback.innerHTML = '<i class="fas fa-spinner fa-spin mr-2 text-gray-400"></i><span class="text-gray-500">Checking availability...</span>';
            
            usernameTimeout = setTimeout(() => {
                fetch(`/api/check-username/?username=${encodeURIComponent(username)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.available) {
                            feedback.innerHTML = '<i class="fas fa-check mr-2 text-green-500"></i><span class="text-green-600">Username available</span>';
                        } else {
                            feedback.innerHTML = '<i class="fas fa-times mr-2 text-red-500"></i><span class="text-red-600">' + data.message + '</span>';
                        }
                    })
                    .catch(error => {
                        feedback.innerHTML = '<i class="fas fa-exclamation-triangle mr-2 text-yellow-500"></i><span class="text-yellow-600">Could not check availability</span>';
                    });
            }, 800);
        });
    }
    
    // Check email availability
    if (emailField) {
        let emailTimeout;
        emailField.addEventListener('input', function() {
            clearTimeout(emailTimeout);
            const feedback = createFeedbackElement(this);
            const email = this.value.trim();
            
            if (!email.includes('@')) {
                feedback.innerHTML = '';
                return;
            }
            
            feedback.innerHTML = '<i class="fas fa-spinner fa-spin mr-2 text-gray-400"></i><span class="text-gray-500">Checking email...</span>';
            
            emailTimeout = setTimeout(() => {
                fetch(`/api/check-email/?email=${encodeURIComponent(email)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.available) {
                            feedback.innerHTML = '<i class="fas fa-check mr-2 text-green-500"></i><span class="text-green-600">Email available</span>';
                        } else {
                            feedback.innerHTML = '<i class="fas fa-times mr-2 text-red-500"></i><span class="text-red-600">' + data.message + ' - <a href="/login/" class="underline">try logging in</a></span>';
                        }
                    })
                    .catch(error => {
                        feedback.innerHTML = '<i class="fas fa-exclamation-triangle mr-2 text-yellow-500"></i><span class="text-yellow-600">Could not check availability</span>';
                    });
            }, 800);
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', checkDuplicateAccount);