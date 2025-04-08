document.addEventListener('DOMContentLoaded', function() {
    // Get duration from meta tag
    const durationMeta = document.querySelector('meta[name="interview-duration"]');
    let durationMinutes = 30; // Default
    
    if (durationMeta) {
        durationMinutes = parseInt(durationMeta.content);
    }
    
    // Initialize timer
    const timerElement = document.getElementById('timer');
    let totalSeconds = durationMinutes * 60;
    let timerInterval;
    
    // Progress bar
    const progressBar = document.getElementById('progress-bar');
    const totalQuestions = document.querySelectorAll('.question-card').length;
    
    // Update progress based on visible question
    function updateProgress() {
        const visibleQuestionIndex = parseInt(document.querySelector('.question-card:not(.d-none)').dataset.questionIndex);
        const progressPercent = ((visibleQuestionIndex + 1) / totalQuestions) * 100;
        progressBar.style.width = `${progressPercent}%`;
        progressBar.setAttribute('aria-valuenow', progressPercent);
    }
    
    // Start timer
    function startTimer() {
        timerInterval = setInterval(function() {
            totalSeconds--;
            
            if (totalSeconds <= 0) {
                clearInterval(timerInterval);
                handleTimeUp();
            } else {
                updateTimerDisplay();
                
                // Show warning at 5 minutes remaining
                if (totalSeconds === 300) {
                    showTimeWarning();
                }
            }
        }, 1000);
    }
    
    // Update timer display
    function updateTimerDisplay() {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        timerElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        
        // Change color based on time remaining
        if (totalSeconds <= 300) {
            timerElement.classList.add('text-danger');
        } else if (totalSeconds <= 600) {
            timerElement.classList.add('text-warning');
        }
    }
    
    // Show time warning modal
    function showTimeWarning() {
        const timeWarningModal = new bootstrap.Modal(document.getElementById('timeWarningModal'));
        timeWarningModal.show();
    }
    
    // Handle time up
    function handleTimeUp() {
        const timeUpModal = new bootstrap.Modal(document.getElementById('timeUpModal'));
        timeUpModal.show();
    }
    
    // Initialize navigation between questions
    document.querySelectorAll('.next-question-btn').forEach(button => {
        button.addEventListener('click', function() {
            const currentQuestion = this.closest('.question-card');
            const nextIndex = parseInt(this.dataset.nextIndex);
            const nextQuestion = document.querySelector(`.question-card[data-question-index="${nextIndex}"]`);
            
            currentQuestion.classList.add('d-none');
            nextQuestion.classList.remove('d-none');
            
            updateProgress();
        });
    });
    
    document.querySelectorAll('.prev-question-btn').forEach(button => {
        button.addEventListener('click', function() {
            const currentQuestion = this.closest('.question-card');
            const prevIndex = parseInt(this.dataset.prevIndex);
            const prevQuestion = document.querySelector(`.question-card[data-question-index="${prevIndex}"]`);
            
            currentQuestion.classList.add('d-none');
            prevQuestion.classList.remove('d-none');
            
            updateProgress();
        });
    });
    
    // Handle submit on timeout
    document.getElementById('submit-on-timeout').addEventListener('click', function() {
        document.getElementById('interview-form').submit();
    });
    
    // Auto-resize textareas
    document.querySelectorAll('.answer-textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
    
    // Add character counter to textareas
    document.querySelectorAll('.answer-textarea').forEach(textarea => {
        const container = textarea.parentElement;
        const counter = document.createElement('div');
        counter.classList.add('text-muted', 'small', 'text-end', 'mt-1');
        counter.innerHTML = `0 characters`;
        container.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const characterCount = this.value.length;
            counter.innerHTML = `${characterCount} characters`;
            
            // Add color indication based on length
            counter.classList.remove('text-danger', 'text-warning', 'text-success');
            
            if (characterCount < 50) {
                counter.classList.add('text-danger');
            } else if (characterCount < 100) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.add('text-success');
            }
        });
    });
    
    // Initialize timer
    startTimer();
    updateTimerDisplay();
    
    // Initialize progress
    updateProgress();
    
    // Warn user before leaving the page
    window.addEventListener('beforeunload', function(e) {
        const confirmationMessage = 'Are you sure you want to leave? Your interview progress will be lost.';
        
        e.returnValue = confirmationMessage;
        return confirmationMessage;
    });
    
    // Remove warning when submitting the form
    document.getElementById('interview-form').addEventListener('submit', function() {
        window.removeEventListener('beforeunload', function() {});
    });
});
