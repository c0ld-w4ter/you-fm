/**
 * JavaScript for AI Daily Briefing Agent Web Interface
 * Provides enhanced user experience and form interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI Daily Briefing Agent - Web Interface Loaded');
    
    // Initialize all functionality
    initFormValidation();
    initLoadingStates();
    initAudioControls();
    initTooltips();
    initLocalStorage();
    initSettingsSections(); // New for Iteration 4
});

/**
 * Initialize settings sections with collapsible functionality (Iteration 4)
 */
function initSettingsSections() {
    // Restore section states from localStorage
    restoreSectionStates();
    
    // Add keyboard navigation for section headers
    const sectionHeaders = document.querySelectorAll('.section-header');
    sectionHeaders.forEach(header => {
        header.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleSection(this);
            }
        });
        
        // Add tabindex for keyboard navigation
        header.setAttribute('tabindex', '0');
    });
}

/**
 * Toggle section collapse/expand state
 */
function toggleSection(headerElement) {
    const section = headerElement.parentElement;
    const content = section.querySelector('.section-content');
    const indicator = headerElement.querySelector('.collapse-indicator');
    
    if (!content || !indicator) return;
    
    const isExpanded = content.classList.contains('expanded');
    
    if (isExpanded) {
        // Collapse section
        content.classList.remove('expanded');
        content.classList.add('collapsed');
        headerElement.classList.add('collapsed');
        indicator.textContent = '+';
        
        // Save state
        saveSectionState(section, false);
    } else {
        // Expand section
        content.classList.remove('collapsed');
        content.classList.add('expanded');
        headerElement.classList.remove('collapsed');
        indicator.textContent = '−';
        
        // Save state
        saveSectionState(section, true);
    }
    
    // Smooth scroll to section header if it's now out of view
    setTimeout(() => {
        const rect = headerElement.getBoundingClientRect();
        if (rect.top < 0) {
            headerElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 300);
}

/**
 * Save section state to localStorage
 */
function saveSectionState(sectionElement, isExpanded) {
    const sectionClass = Array.from(sectionElement.classList).find(cls => 
        cls.includes('-settings')
    );
    
    if (sectionClass) {
        const states = getSectionStates();
        states[sectionClass] = isExpanded;
        localStorage.setItem('settings_section_states', JSON.stringify(states));
    }
}

/**
 * Restore section states from localStorage
 */
function restoreSectionStates() {
    const states = getSectionStates();
    
    Object.keys(states).forEach(sectionClass => {
        const section = document.querySelector(`.${sectionClass}`);
        if (section) {
            const header = section.querySelector('.section-header');
            const content = section.querySelector('.section-content');
            const indicator = section.querySelector('.collapse-indicator');
            
            if (header && content && indicator) {
                const shouldExpand = states[sectionClass];
                
                if (shouldExpand) {
                    content.classList.remove('collapsed');
                    content.classList.add('expanded');
                    header.classList.remove('collapsed');
                    indicator.textContent = '−';
                } else {
                    content.classList.remove('expanded');
                    content.classList.add('collapsed');
                    header.classList.add('collapsed');
                    indicator.textContent = '+';
                }
            }
        }
    });
}

/**
 * Get section states from localStorage
 */
function getSectionStates() {
    try {
        const states = localStorage.getItem('settings_section_states');
        return states ? JSON.parse(states) : {
            'basic-settings': true,      // Default: expanded
            'content-settings': true,    // Default: expanded
            'audio-settings': true       // Default: expanded
        };
    } catch (error) {
        console.error('Error loading section states:', error);
        return {
            'basic-settings': true,
            'content-settings': true,
            'audio-settings': true
        };
    }
}

/**
 * Collapse all sections
 */
function collapseAllSections() {
    const sections = document.querySelectorAll('.settings-section');
    sections.forEach(section => {
        const header = section.querySelector('.section-header');
        if (header && !header.classList.contains('collapsed')) {
            toggleSection(header);
        }
    });
}

/**
 * Expand all sections
 */
function expandAllSections() {
    const sections = document.querySelectorAll('.settings-section');
    sections.forEach(section => {
        const header = section.querySelector('.section-header');
        if (header && header.classList.contains('collapsed')) {
            toggleSection(header);
        }
    });
}

/**
 * Form validation and enhancement
 */
function initFormValidation() {
    const form = document.querySelector('form[method="POST"]');
    if (!form) return;
    
    // Add real-time validation for required fields
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', validateField);
        field.addEventListener('input', clearFieldError);
    });
    
    // Note: Form submission is handled by HTML onsubmit="return handleFormSubmission(event)"
    // No need to add another event listener here
}

/**
 * Validate individual form field
 */
function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Remove existing error styling
    field.classList.remove('border-red-500', 'border-green-500');
    
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    // Specific validation rules
    if (field.name === 'location_country' && value) {
        if (!/^[A-Z]{2}$/.test(value.toUpperCase())) {
            showFieldError(field, 'Please enter a 2-letter country code (e.g., US)');
            return false;
        }
        field.value = value.toUpperCase();
    }
    
    if (field.type === 'number') {
        const num = parseInt(value);
        const min = parseInt(field.getAttribute('min')) || 0;
        const max = parseInt(field.getAttribute('max')) || Infinity;
        
        if (num < min || num > max) {
            showFieldError(field, `Value must be between ${min} and ${max}`);
            return false;
        }
    }
    
    // Field is valid
    field.classList.add('border-green-500');
    clearFieldError(field);
    return true;
}

/**
 * Show field validation error
 */
function showFieldError(field, message) {
    field.classList.add('border-red-500');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorElement = document.createElement('p');
    errorElement.className = 'field-error mt-1 text-sm text-red-600';
    errorElement.textContent = message;
    field.parentNode.appendChild(errorElement);
}

/**
 * Clear field validation error
 */
function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('border-red-500');
    
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.remove();
    }
    
    if (field.value.trim()) {
        field.classList.add('border-green-500');
    } else {
        field.classList.remove('border-green-500');
    }
}

/**
 * Handle form submission with validation
 */
function handleFormSubmission(event) {
    console.log('🔍 handleFormSubmission called');
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
    
    // Validate all required fields
    const requiredFields = form.querySelectorAll('input[required], select[required]');
    let isValid = true;
    let missingFields = [];
    
    requiredFields.forEach(field => {
        if (!validateField({ target: field })) {
            isValid = false;
            // Get human-readable field name from label
            const label = form.querySelector(`label[for="${field.id}"]`) || form.querySelector(`label[for="${field.name}"]`);
            const fieldName = label ? label.textContent.replace('*', '').trim() : field.name;
            missingFields.push(fieldName);
        }
    });
    
    if (!isValid) {
        event.preventDefault();
        console.log('❌ Form validation failed - preventing submission');
        
        // Ensure loading indicator is hidden
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.classList.add('hidden');
            loadingIndicator.style.display = 'none';
        }
        
        // Show specific error message about missing API keys
        if (missingFields.length > 0) {
            const apiKeyFields = missingFields.filter(name => 
                name.toLowerCase().includes('key') || name.toLowerCase().includes('id')
            );
            
            if (apiKeyFields.length > 0) {
                showNotification(`Please fill in all required API keys: ${apiKeyFields.join(', ')}`, 'error');
            } else {
                showNotification(`Please fill in required fields: ${missingFields.join(', ')}`, 'error');
            }
        } else {
            showNotification('Please correct the errors in the form', 'error');
        }
        
        // Scroll to first error field
        const firstErrorField = form.querySelector('.border-red-500');
        if (firstErrorField) {
            firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstErrorField.focus();
        }
        
        return false;
    }
    
    // Validation passed - proceed with form submission
    console.log('✅ Form validation passed - proceeding with submission');
    
    // Save form data to localStorage for recovery
    saveFormData(form);
    
    // Show loading state
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Generating...';
    }
    
    // Show loading indicator with progress (only when validation passes)
    console.log('🚀 About to show loading indicator...');
    showLoadingWithProgress();
    
    showNotification('Generating your briefing... This may take a few minutes.', 'info');
}

/**
 * Initialize loading states and progress indicators
 */
function initLoadingStates() {
    // Remove the button click handler that immediately shows progress bar
    // Progress bar will only be shown after validation passes in handleFormSubmission()
    console.log('Loading states initialized - progress bar will show only after validation');
}

/**
 * Show loading indicator with progress updates
 */
function showLoadingWithProgress() {
    console.log('🎯 showLoadingWithProgress called');
    
    const loadingIndicator = document.getElementById('loading-indicator');
    const progressBar = document.getElementById('progress-bar');
    const loadingStatus = document.getElementById('loading-status');
    const progressSteps = document.getElementById('progress-steps');
    
    console.log('🔍 Elements found:', {
        loadingIndicator: !!loadingIndicator,
        progressBar: !!progressBar,
        loadingStatus: !!loadingStatus,
        progressSteps: !!progressSteps
    });
    
    if (!loadingIndicator) {
        console.error('❌ Loading indicator not found!');
        return;
    }
    
    console.log('✅ Showing loading indicator with progress...');
    
    // Show the loading indicator immediately
    loadingIndicator.classList.remove('hidden');
    loadingIndicator.style.display = 'flex';
    
    // Set initial progress state immediately
    if (loadingStatus) {
        loadingStatus.textContent = 'Validating configuration...';
        console.log('✅ Set loading status text');
    }
    if (progressSteps) {
        progressSteps.innerHTML = '<p>Step 1 of 5: Validating configuration...</p>';
        console.log('✅ Set progress steps text');
    }
    if (progressBar) {
        progressBar.style.width = '15%';
        console.log('✅ Set progress bar to 15%');
    }
    
    console.log('🎉 Loading indicator should now be visible');
    
    // Progress steps with messages, progress percentages, and timing
    const steps = [
        { message: 'Fetching weather data...', step: 'Step 2 of 5', progress: 30, delay: 2000 },
        { message: 'Gathering news articles...', step: 'Step 3 of 5', progress: 50, delay: 6000 },
        { message: 'Generating AI briefing script...', step: 'Step 4 of 5', progress: 80, delay: 12000 },
        { message: 'Converting to audio...', step: 'Step 5 of 5', progress: 95, delay: 20000 }
    ];
    
    // Start progress updates (only if we're still on the same page)
    steps.forEach(({ message, step, progress, delay }) => {
        setTimeout(() => {
            // Check if elements still exist (user hasn't navigated away)
            if (loadingStatus && document.contains(loadingStatus)) {
                loadingStatus.textContent = message;
                console.log(`🔄 Updated status: ${message}`);
            }
            if (progressSteps && document.contains(progressSteps)) {
                progressSteps.innerHTML = `<p>${step}: ${message}</p>`;
                console.log(`🔄 Updated steps: ${step}`);
            }
            if (progressBar && document.contains(progressBar)) {
                progressBar.style.width = `${progress}%`;
                console.log(`🔄 Updated progress: ${progress}%`);
            }
        }, delay);
    });
}

/**
 * Initialize audio player enhancements
 */
function initAudioControls() {
    const audioPlayers = document.querySelectorAll('audio');
    
    audioPlayers.forEach(audio => {
        // Add custom controls and features
        audio.addEventListener('loadstart', () => {
            console.log('Audio loading started');
        });
        
        audio.addEventListener('canplay', () => {
            console.log('Audio ready to play');
            // Could add play button styling here
        });
        
        audio.addEventListener('error', (e) => {
            console.error('Audio playback error:', e);
            showNotification('Error playing audio file', 'error');
        });
        
        // Add keyboard shortcuts
        audio.addEventListener('keydown', (e) => {
            switch(e.key) {
                case ' ':
                    e.preventDefault();
                    audio.paused ? audio.play() : audio.pause();
                    break;
                case 'ArrowLeft':
                    audio.currentTime = Math.max(0, audio.currentTime - 10);
                    break;
                case 'ArrowRight':
                    audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
                    break;
            }
        });
    });
}

/**
 * Initialize tooltips and help text
 */
function initTooltips() {
    const helpTexts = {
        'newsapi_key': 'Get a free API key from NewsAPI.org. Required for fetching news articles.',
        'taddy_api_key': 'Taddy provides podcast data. Sign up at taddy.org for free API access.',
        'gemini_api_key': 'Google Gemini API is used for AI summarization. Get key from Google AI Studio.',
        'elevenlabs_api_key': 'ElevenLabs provides text-to-speech conversion. Sign up for free credits.'
    };
    
    Object.keys(helpTexts).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.setAttribute('title', helpTexts[fieldName]);
        }
    });
}

/**
 * Save and restore form data using localStorage
 */
function initLocalStorage() {
    restoreFormData();
    
    // Auto-save form data as user types (for non-sensitive fields)
    const nonSensitiveFields = document.querySelectorAll(
        'input[name="listener_name"], input[name="location_city"], input[name="location_country"], ' +
        'input[name="news_topics"], input[name="podcast_categories"], select[name="elevenlabs_voice_id"]'
    );
    
    nonSensitiveFields.forEach(field => {
        field.addEventListener('input', debounce(saveNonSensitiveData, 1000));
    });
}

/**
 * Save form data to localStorage (excluding sensitive API keys)
 */
function saveNonSensitiveData() {
    const formData = {};
    const nonSensitiveFields = document.querySelectorAll(
        'input[name="listener_name"], input[name="location_city"], input[name="location_country"], ' +
        'input[name="news_topics"], input[name="podcast_categories"], select[name="elevenlabs_voice_id"], ' +
        'input[name="briefing_duration_minutes"], input[name="max_articles_per_topic"]'
    );
    
    nonSensitiveFields.forEach(field => {
        if (field.value.trim()) {
            formData[field.name] = field.value;
        }
    });
    
    localStorage.setItem('briefing_preferences', JSON.stringify(formData));
}

/**
 * Restore form data from localStorage
 */
function restoreFormData() {
    try {
        const savedData = localStorage.getItem('briefing_preferences');
        if (savedData) {
            const formData = JSON.parse(savedData);
            
            Object.keys(formData).forEach(fieldName => {
                const field = document.querySelector(`[name="${fieldName}"]`);
                if (field && !field.value) {
                    field.value = formData[fieldName];
                }
            });
        }
    } catch (error) {
        console.error('Error restoring form data:', error);
    }
}

/**
 * Save complete form data before submission (for recovery)
 */
function saveFormData(form) {
    const formData = new FormData(form);
    const data = {};
    
    // Only save non-sensitive data for recovery
    const nonSensitiveFields = [
        'listener_name', 'location_city', 'location_country',
        'news_topics', 'podcast_categories', 'elevenlabs_voice_id',
        'briefing_duration_minutes', 'max_articles_per_topic'
    ];
    
    nonSensitiveFields.forEach(field => {
        if (formData.has(field)) {
            data[field] = formData.get(field);
        }
    });
    
    localStorage.setItem('last_briefing_config', JSON.stringify(data));
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'success' ? 'bg-green-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

/**
 * Debounce function to limit function calls
 */
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

/**
 * Utility functions for form handling
 */
const FormUtils = {
    /**
     * Clear all form data
     */
    clearForm: function() {
        const form = document.querySelector('form[method="POST"]');
        if (form) {
            form.reset();
            localStorage.removeItem('briefing_preferences');
            localStorage.removeItem('last_briefing_config');
            showNotification('Form cleared successfully', 'success');
        }
    },
    
    /**
     * Copy configuration to clipboard
     */
    copyConfig: function() {
        const config = localStorage.getItem('last_briefing_config');
        if (config && navigator.clipboard) {
            navigator.clipboard.writeText(config).then(() => {
                showNotification('Configuration copied to clipboard', 'success');
            });
        }
    }
};

// Make FormUtils available globally for potential use in templates
window.FormUtils = FormUtils; 