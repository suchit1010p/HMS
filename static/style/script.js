// Enhanced Carousel functionality with animated progress indicators
function initCarousel() {
    const images = document.getElementById('carousel-images');
    if (!images) return;

    const progressIndicators = document.querySelectorAll('.progress-indicator');
    const prevButton = document.getElementById('prev');
    const nextButton = document.getElementById('next');
    let currentIndex = 0;
    let autoSlideInterval;
    let progressTimeout;

    function updateCarousel() {
        // Update carousel position
        images.style.transform = `translateX(-${currentIndex * 100}%)`;

        // Update progress indicators
        progressIndicators.forEach((indicator, index) => {
            indicator.classList.remove('active');
            indicator.style.width = '10px';
            indicator.style.borderRadius = '50%';

            if (index === currentIndex) {
                indicator.classList.add('active');

                // Clear any existing progress animation
                clearTimeout(progressTimeout);

                // Start new progress animation
                progressTimeout = setTimeout(() => {
                    nextImage();
                }, 3000);
            }
        });
    }

    function nextImage() {
        currentIndex = (currentIndex + 1) % progressIndicators.length;
        updateCarousel();
    }

    function prevImage() {
        currentIndex = (currentIndex - 1 + progressIndicators.length) % progressIndicators.length;
        updateCarousel();
    }

    function startAutoSlide() {
        autoSlideInterval = setInterval(nextImage, 3000);
    }

    function resetAutoSlide() {
        clearInterval(autoSlideInterval);
        startAutoSlide();
    }

    // Click on indicators to navigate
    progressIndicators.forEach(indicator => {
        indicator.addEventListener('click', function() {
            currentIndex = parseInt(this.getAttribute('data-index'));
            updateCarousel();
            resetAutoSlide();
        });
    });

    // Navigation buttons
    if (nextButton) {
        nextButton.addEventListener('click', () => {
            nextImage();
            resetAutoSlide();
        });
    }

    if (prevButton) {
        prevButton.addEventListener('click', () => {
            prevImage();
            resetAutoSlide();
        });
    }

    // Initialize carousel and auto slide
    updateCarousel();
    startAutoSlide();
}

// Mobile menu functionality
function initMobileMenu() {
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            mobileMenu.classList.toggle('hidden');
            document.body.classList.toggle('overflow-hidden', !mobileMenu.classList.contains('hidden'));
        });

        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!mobileMenu.classList.contains('hidden') && 
                !e.target.closest('.mobile-menu') && 
                !e.target.closest('.mobile-menu-button')) {
                mobileMenu.classList.add('hidden');
                document.body.classList.remove('overflow-hidden');
            }
        });

        // Close menu when clicking links
        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.add('hidden');
                document.body.classList.remove('overflow-hidden');
            });
        });
    }
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                const mobileMenu = document.querySelector('.mobile-menu');
                if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
                    mobileMenu.classList.add('hidden');
                }
            }
        });
    });
}

// Dark mode toggle functionality
function initDarkMode() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeToggleMobile = document.getElementById('theme-toggle-mobile');
    const themeIcon = document.getElementById('theme-icon');

    // Function to set theme
    function setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            if (themeIcon) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            }
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            if (themeIcon) {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        }
    }

    // Check for saved theme preference or use system preference
    function checkTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            setTheme(savedTheme);
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setTheme('dark');
        } else {
            setTheme('light');
        }
    }

    // Toggle theme
    function toggleTheme() {
        if (document.documentElement.classList.contains('dark')) {
            setTheme('light');
        } else {
            setTheme('dark');
        }
    }

    // Event listeners for theme toggle buttons
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    if (themeToggleMobile) {
        themeToggleMobile.addEventListener('click', toggleTheme);
    }

    // Check theme on load
    checkTheme();

    // Watch for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

// Scroll animation
function initScrollAnimations() {
    function checkVisibility() {
        const elements = document.querySelectorAll('.fade-in');

        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;

            if (elementTop < windowHeight - 100) {
                element.classList.add('visible');
            }
        });
    }

    // Initial check
    checkVisibility();

    // Check on scroll
    window.addEventListener('scroll', checkVisibility);
}

// Modal functions
function openRegistrationModal() {
    document.getElementById('registrationModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

function closeRegistrationModal() {
    document.getElementById('registrationModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}

function openLoginModal() {
    document.getElementById('loginModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

function closeLoginModal() {
    document.getElementById('loginModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}

function switchToRegistration() {
    closeLoginModal();
    openRegistrationModal();
}

// Password visibility toggle
function togglePasswordVisibility(passwordFieldId, iconId) {
    const passwordField = document.getElementById(passwordFieldId);
    const icon = document.getElementById(iconId);
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        passwordField.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const registrationModal = document.getElementById('registrationModal');
    const loginModal = document.getElementById('loginModal');
    
    if (event.target === registrationModal) {
        closeRegistrationModal();
    }
    if (event.target === loginModal) {
        closeLoginModal();
    }
});

// Form submission
document.getElementById('registrationForm')?.addEventListener('submit', function(e) {
    // Validate passwords match
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        e.preventDefault();
        return;
    }
    
    alert('Registration successful!');
    closeRegistrationModal();
});

// Initialize all functions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCarousel();
    initMobileMenu();
    initSmoothScrolling();
    initDarkMode();
    initScrollAnimations();
});
// Modal functions
function openLoginModal() {
    document.getElementById('loginModal').classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
}

function closeLoginModal() {
    document.getElementById('loginModal').classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
}

// Password toggle
function togglePasswordVisibility(passwordFieldId, iconId) {
    const passwordField = document.getElementById(passwordFieldId);
    const icon = document.getElementById(iconId);
    
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        passwordField.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

// Close modal when clicking outside
window.addEventListener('click', function(event) {
    const loginModal = document.getElementById('loginModal');
    if (event.target === loginModal) {
        closeLoginModal();
    }
});
// DOM Elements
const registrationModal = document.getElementById('registrationModal');
const loginModal = document.getElementById('loginModal');
const progressBar = document.getElementById('progressBar');

// Form step navigation
function validateStep(currentStepNumber) {
    const currentStep = document.querySelector(`.form-step[data-step="${currentStepNumber}"]`);
    const inputs = currentStep.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('invalid');
            isValid = false;
            
            // Remove shake animation after it completes
            setTimeout(() => {
                input.classList.remove('invalid');
            }, 500);
        }
    });
    
    if (isValid) {
        nextStep(currentStepNumber + 1);
    }
}

function nextStep(step) {
    // Hide current step
    const currentActive = document.querySelector('.form-step.active');
    if (currentActive) {
        currentActive.classList.remove('active');
        currentActive.classList.add('hidden');
    }
    
    // Show next step
    const nextStep = document.querySelector(`.form-step[data-step="${step}"]`);
    if (nextStep) {
        nextStep.classList.remove('hidden');
        nextStep.classList.add('active');
        
        // Update progress indicators
        updateProgressIndicators(step);
        
        // Scroll to top of form
        nextStep.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function prevStep(step) {
    // Hide current step
    document.querySelector('.form-step.active').classList.remove('active');
    document.querySelector('.form-step.active').classList.add('hidden');
    
    // Show previous step
    document.querySelector(`.form-step[data-step="${step}"]`).classList.remove('hidden');
    document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');
    
    // Update progress indicators
    updateProgressIndicators(step);
}

function updateProgressIndicators(step) {
    // Update step indicators
    document.querySelectorAll('.step-indicator').forEach(indicator => {
        indicator.classList.remove('active');
        const indicatorStep = indicator.getAttribute('data-step');
        if (indicatorStep <= step) {
            indicator.classList.add('active');
        }
    });
    
    // Update progress bar
    const progressPercentage = ((step - 1) / 2) * 100;
    if (progressBar) {
        progressBar.style.width = `${progressPercentage}%`;
    }
}

// Modal control functions
function closeRegistrationModal() {
    if (registrationModal) {
        registrationModal.classList.add('hidden');
        resetRegistrationForm();
    }
}

function openRegistrationModal() {
    if (registrationModal) {
        registrationModal.classList.remove('hidden');
    }
}

function closeLoginModal() {
    if (loginModal) {
        loginModal.classList.add('hidden');
    }
}

function openLoginModal() {
    if (loginModal) {
        loginModal.classList.remove('hidden');
    }
}

function switchToRegistration() {
    closeLoginModal();
    openRegistrationModal();
}

function togglePasswordVisibility(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (input && icon) {
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.replace('fa-eye', 'fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.replace('fa-eye-slash', 'fa-eye');
        }
    }
}

function resetRegistrationForm() {
    // Reset to first step
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.remove('active');
        step.classList.add('hidden');
    });
    const firstStep = document.querySelector('.form-step[data-step="1"]');
    if (firstStep) {
        firstStep.classList.remove('hidden');
        firstStep.classList.add('active');
    }
    
    // Reset progress indicators
    updateProgressIndicators(1);
}

// Initialize form when modal opens
document.addEventListener('DOMContentLoaded', function() {
    // Make step indicators clickable
    document.querySelectorAll('.step-indicator').forEach(indicator => {
        indicator.addEventListener('click', function() {
            const step = parseInt(this.getAttribute('data-step'));
            const currentStep = parseInt(document.querySelector('.form-step.active').getAttribute('data-step'));
            
            if (step < currentStep) {
                prevStep(step);
            }
        });
    });
    
    // Password match validation
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    
    if (password && confirmPassword) {
        function validatePassword() {
            if (password.value !== confirmPassword.value) {
                confirmPassword.setCustomValidity("Passwords don't match");
                confirmPassword.classList.add('invalid');
            } else {
                confirmPassword.setCustomValidity('');
                confirmPassword.classList.remove('invalid');
            }
        }
        
        password.addEventListener('change', validatePassword);
        confirmPassword.addEventListener('keyup', validatePassword);
    }
    
    // Close modals when clicking outside
    [registrationModal, loginModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    if (modal.id === 'registrationModal') {
                        closeRegistrationModal();
                    } else {
                        closeLoginModal();
                    }
                }
            });
        }
    });
});

// Expose functions to global scope for HTML onclick handlers
window.validateStep = validateStep;
window.prevStep = prevStep;
window.nextStep = nextStep;
window.closeRegistrationModal = closeRegistrationModal;
window.openRegistrationModal = openRegistrationModal;
window.closeLoginModal = closeLoginModal;
window.openLoginModal = openLoginModal;
window.switchToRegistration = switchToRegistration;
window.togglePasswordVisibility = togglePasswordVisibility;