// AI Buddy - Modern Web Interface
class AIBuddyApp {
    constructor() {
        this.currentSection = 'register';
        this.recordingState = {
            isRecording: false,
            currentSample: 0,
            samples: [],
            mediaRecorder: null,
            audioChunks: []
        };
        this.buddyState = {
            emotion: 'happy',
            isProcessing: false,
            currentUser: null,
            isDancing: false
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadUsers();
        this.setupBuddyStatePolling();
        this.initializeCustomization();
        this.setupMobileOptimizations();
        this.showToast('Welcome to AI Buddy!', 'success');
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('register-tab').addEventListener('click', () => this.switchSection('register'));
        document.getElementById('auth-tab').addEventListener('click', () => this.switchSection('auth'));
        document.getElementById('customize-tab').addEventListener('click', () => this.switchSection('customize'));

        // Registration form
        document.getElementById('register-form').addEventListener('submit', (e) => this.handleRegistration(e));
        
        // Recording buttons
        document.querySelectorAll('.record-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleRecording(e));
        });

        // Authentication
        document.getElementById('start-btn').addEventListener('click', () => this.startAuthentication());

        // Form validation
        document.getElementById('username').addEventListener('input', (e) => this.validateUsername(e.target.value));
        document.getElementById('password-phrase').addEventListener('input', (e) => this.validatePassword(e.target.value));

        // Customization
        this.setupCustomizationListeners();

        // Modal
        document.querySelector('.modal-close').addEventListener('click', () => this.closeModal());
        document.getElementById('instructions-modal').addEventListener('click', (e) => {
            if (e.target.id === 'instructions-modal') this.closeModal();
        });
    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`${section}-tab`).classList.add('active');

        // Update content
        document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
        document.getElementById(`${section}-section`).classList.add('active');

        this.currentSection = section;

        if (section === 'auth') {
            this.loadUsers();
        } else if (section === 'customize') {
            this.loadCustomizationSettings();
        }
    }

    async handleRegistration(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const passwordPhrase = document.getElementById('password-phrase').value.trim();
        
        if (!this.validateForm(username, passwordPhrase)) {
            return;
        }

        if (this.recordingState.samples.length < 3) {
            this.showToast('Please record all 3 voice samples', 'error');
            return;
        }

        try {
            this.showLoading(true);
            
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password_phrase', passwordPhrase);
            
            // Add audio samples
            this.recordingState.samples.forEach((audioBlob, index) => {
                formData.append(`audio_${index}`, audioBlob, `sample_${index}.wav`);
            });

            const response = await fetch('/register_user', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showToast('User registered successfully!', 'success');
                this.resetRegistrationForm();
                this.switchSection('auth');
            } else {
                this.showToast(result.message || 'Registration failed', 'error');
            }
        } catch (error) {
            console.error('Registration error:', error);
            this.showToast('Registration failed. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    validateForm(username, passwordPhrase) {
        let isValid = true;

        if (!username) {
            this.showFieldError('username-error', 'Username is required');
            isValid = false;
        } else if (username.length < 3) {
            this.showFieldError('username-error', 'Username must be at least 3 characters');
            isValid = false;
        } else {
            this.clearFieldError('username-error');
        }

        if (!passwordPhrase) {
            this.showFieldError('password-error', 'Password phrase is required');
            isValid = false;
        } else if (passwordPhrase.length < 5) {
            this.showFieldError('password-error', 'Password phrase must be at least 5 characters');
            isValid = false;
        } else {
            this.clearFieldError('password-error');
        }

        return isValid;
    }

    validateUsername(username) {
        if (username.length > 0 && username.length < 3) {
            this.showFieldError('username-error', 'Username must be at least 3 characters');
        } else {
            this.clearFieldError('username-error');
        }
    }

    validatePassword(password) {
        if (password.length > 0 && password.length < 5) {
            this.showFieldError('password-error', 'Password phrase must be at least 5 characters');
        } else {
            this.clearFieldError('password-error');
        }
    }

    showFieldError(fieldId, message) {
        const errorElement = document.getElementById(fieldId);
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }

    clearFieldError(fieldId) {
        const errorElement = document.getElementById(fieldId);
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }

    async handleRecording(e) {
        const sampleNumber = parseInt(e.target.dataset.sample);
        
        if (this.recordingState.isRecording) {
            await this.stopRecording();
        } else {
            await this.startRecording(sampleNumber);
        }
    }

    async startRecording(sampleNumber) {
        try {
            // Request high-quality audio with specific constraints
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: false,  // Disable to preserve voice characteristics
                    noiseSuppression: false,  // Disable to preserve voice characteristics
                    autoGainControl: false,   // Disable to preserve voice characteristics
                    latency: 0.01             // Low latency
                } 
            });
            
            // Try to use WAV format first, fallback to WebM
            let mimeType = 'audio/wav';
            if (!MediaRecorder.isTypeSupported('audio/wav')) {
                mimeType = 'audio/webm;codecs=opus';
            }
            
            this.recordingState.mediaRecorder = new MediaRecorder(stream, {
                mimeType: mimeType,
                audioBitsPerSecond: 128000  // High quality
            });
            this.recordingState.audioChunks = [];

            this.recordingState.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.recordingState.audioChunks.push(event.data);
                }
            };

            this.recordingState.mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(this.recordingState.audioChunks, { type: mimeType });
                
                // Convert to WAV format with better quality
                const wavBlob = await this.convertToWav(audioBlob, 16000);
                this.recordingState.samples[sampleNumber - 1] = wavBlob;
                
                this.updateRecordingUI(sampleNumber, true);
                this.updateProgress();
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };

            this.recordingState.mediaRecorder.start(100); // Collect data every 100ms
            this.recordingState.isRecording = true;
            this.recordingState.currentSample = sampleNumber;

            this.updateRecordingUI(sampleNumber, true, true);
            this.showToast(`Recording sample ${sampleNumber}... Speak clearly!`, 'info');
            
            // Auto-stop recording after 3 seconds (matching reference files)
            setTimeout(() => {
                if (this.recordingState.isRecording) {
                    this.stopRecording();
                }
            }, 3000);

        } catch (error) {
            console.error('Error accessing microphone:', error);
            this.showToast('Microphone access denied. Please allow microphone access.', 'error');
        }
    }

    async convertToWav(audioBlob, targetSampleRate = 16000) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = async () => {
                try {
                    const arrayBuffer = reader.result;
                    const audioContext = new (window.AudioContext || window.webkitAudioContext)({
                        sampleRate: targetSampleRate
                    });
                    
                    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                    
                    // Resample to target sample rate if needed
                    let processedBuffer = audioBuffer;
                    if (audioBuffer.sampleRate !== targetSampleRate) {
                        processedBuffer = await this.resampleAudio(audioBuffer, targetSampleRate);
                    }
                    
                    // Convert to 16kHz mono WAV
                    const length = processedBuffer.length;
                    const wavBuffer = new ArrayBuffer(44 + length * 2);
                    const view = new DataView(wavBuffer);
                    
                    // WAV header
                    const writeString = (offset, string) => {
                        for (let i = 0; i < string.length; i++) {
                            view.setUint8(offset + i, string.charCodeAt(i));
                        }
                    };
                    
                    writeString(0, 'RIFF');
                    view.setUint32(4, 36 + length * 2, true);
                    writeString(8, 'WAVE');
                    writeString(12, 'fmt ');
                    view.setUint32(16, 16, true);
                    view.setUint16(20, 1, true);  // PCM format
                    view.setUint16(22, 1, true);  // Mono
                    view.setUint32(24, targetSampleRate, true);
                    view.setUint32(28, targetSampleRate * 2, true);
                    view.setUint16(32, 2, true);  // Block align
                    view.setUint16(34, 16, true); // Bits per sample
                    writeString(36, 'data');
                    view.setUint32(40, length * 2, true);
                    
                    // Convert audio data with better quality
                    const channelData = processedBuffer.getChannelData(0);
                    let offset = 44;
                    for (let i = 0; i < length; i++) {
                        // Apply gentle compression to prevent clipping while preserving dynamics
                        let sample = channelData[i];
                        sample = Math.max(-0.95, Math.min(0.95, sample)); // Prevent clipping
                        sample = sample * 0.8; // Slight volume reduction for safety
                        view.setInt16(offset, Math.round(sample * 0x7FFF), true);
                        offset += 2;
                    }
                    
                    resolve(new Blob([wavBuffer], { type: 'audio/wav' }));
                } catch (error) {
                    console.error('Error converting audio to WAV:', error);
                    reject(error);
                }
            };
            reader.readAsArrayBuffer(audioBlob);
        });
    }

    async resampleAudio(audioBuffer, targetSampleRate) {
        const sourceSampleRate = audioBuffer.sampleRate;
        const ratio = sourceSampleRate / targetSampleRate;
        const newLength = Math.floor(audioBuffer.length / ratio);
        
        const newBuffer = new AudioBuffer({
            numberOfChannels: 1,
            length: newLength,
            sampleRate: targetSampleRate
        });
        
        const sourceData = audioBuffer.getChannelData(0);
        const targetData = newBuffer.getChannelData(0);
        
        // Simple linear interpolation resampling
        for (let i = 0; i < newLength; i++) {
            const sourceIndex = i * ratio;
            const index = Math.floor(sourceIndex);
            const fraction = sourceIndex - index;
            
            if (index + 1 < sourceData.length) {
                targetData[i] = sourceData[index] * (1 - fraction) + sourceData[index + 1] * fraction;
            } else {
                targetData[i] = sourceData[index];
            }
        }
        
        return newBuffer;
    }

    async stopRecording() {
        if (this.recordingState.mediaRecorder && this.recordingState.isRecording) {
            this.recordingState.mediaRecorder.stop();
            this.recordingState.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            this.recordingState.isRecording = false;
            
            this.updateRecordingUI(this.recordingState.currentSample, true, false);
            this.showToast('Recording completed!', 'success');
        }
    }

    updateRecordingUI(sampleNumber, isRecorded, isRecording = false) {
        const button = document.getElementById(`record-sample-${sampleNumber}`);
        const indicator = document.getElementById('recording-indicator');
        const text = document.getElementById('recording-text');

        if (isRecording) {
            button.classList.add('recording');
            button.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
            indicator.classList.add('recording');
            text.textContent = 'Recording...';
        } else if (isRecorded) {
            button.classList.remove('recording');
            button.innerHTML = '<i class="fas fa-check"></i> Recorded';
            button.disabled = true;
            indicator.classList.remove('recording');
            text.textContent = 'Ready to record';
            
            // Enable next button
            if (sampleNumber < 3) {
                const nextButton = document.getElementById(`record-sample-${sampleNumber + 1}`);
                nextButton.disabled = false;
            }
        } else {
            button.classList.remove('recording');
            button.innerHTML = '<i class="fas fa-microphone"></i> Record Sample ' + sampleNumber;
            indicator.classList.remove('recording');
            text.textContent = 'Ready to record';
        }
    }

    updateProgress() {
        const recordedCount = this.recordingState.samples.filter(s => s).length;
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        const submitBtn = document.getElementById('register-submit');

        const percentage = (recordedCount / 3) * 100;
        progressFill.style.width = `${percentage}%`;
        progressText.textContent = `${recordedCount}/3 samples recorded`;

        submitBtn.disabled = recordedCount < 3;
    }

    resetRegistrationForm() {
        document.getElementById('register-form').reset();
        this.recordingState.samples = [];
        this.recordingState.currentSample = 0;
        this.recordingState.isRecording = false;

        // Reset all recording buttons
        for (let i = 1; i <= 3; i++) {
            const button = document.getElementById(`record-sample-${i}`);
            button.disabled = i > 1;
            button.classList.remove('recording');
            button.innerHTML = `<i class="fas fa-microphone"></i> Record Sample ${i}`;
        }

        this.updateProgress();
        this.clearFieldError('username-error');
        this.clearFieldError('password-error');
    }

    async startAuthentication() {
        try {
            this.showLoading(true);
            this.setBuddyEmotion('thinking');
            this.updateStatus('Starting authentication...', '');

            const response = await fetch('/start_authentication', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();
            
            if (result.status === 'started') {
                this.showToast('Authentication started! Please say your secret passcode after the beep.', 'info');
            } else {
                this.showToast('Failed to start authentication', 'error');
            }
        } catch (error) {
            console.error('Authentication error:', error);
            this.showToast('Authentication failed. Please try again.', 'error');
            this.setBuddyEmotion('sad');
        } finally {
            this.showLoading(false);
        }
    }

    setupBuddyStatePolling() {
        setInterval(async () => {
            try {
                const response = await fetch('/get_buddy_state');
                const state = await response.json();
                
                this.buddyState = state;
                this.updateBuddyDisplay();
            } catch (error) {
                console.error('Error fetching buddy state:', error);
            }
        }, 1000);
    }

    updateBuddyDisplay() {
        this.setBuddyEmotion(this.buddyState.emotion);
        
        if (this.buddyState.currentUser) {
            this.updateStatus(`Welcome, ${this.buddyState.currentUser}!`, 'Access granted');
        } else if (this.buddyState.isProcessing) {
            this.updateStatus('Processing your voice...', 'Please wait');
        } else {
            this.updateStatus('Ready to identify you!', '');
        }
    }

    setBuddyEmotion(emotion) {
        const robot = document.getElementById('ai-robot');
        if (robot) {
            robot.className = `robot ${emotion}`;
        }
    }

    updateStatus(statusText, userInfo) {
        const statusElement = document.getElementById('status-text');
        const userInfoElement = document.getElementById('user-info');
        
        if (statusElement) statusElement.textContent = statusText;
        if (userInfoElement) userInfoElement.textContent = userInfo;
    }

    async loadUsers() {
        try {
            const response = await fetch('/get_users');
            const users = await response.json();
            this.displayUsers(users);
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    displayUsers(users) {
        const usersList = document.getElementById('users-list');
        if (!usersList) return;

        if (users.length === 0) {
            usersList.innerHTML = '<p style="color: rgba(255,255,255,0.7); text-align: center;">No users registered yet</p>';
            return;
        }

        usersList.innerHTML = users.map(user => `
            <div class="user-card">
                <h4><i class="fas fa-user"></i> ${user}</h4>
                <p>Registered user</p>
            </div>
        `).join('');
    }

    showLoading(show) {
        const submitBtn = document.getElementById('register-submit');
        const startBtn = document.getElementById('start-btn');
        
        if (submitBtn) {
            submitBtn.disabled = show;
            submitBtn.innerHTML = show ? 
                '<i class="fas fa-spinner fa-spin"></i> Processing...' : 
                '<i class="fas fa-user-check"></i> Complete Registration';
        }
        
        if (startBtn) {
            startBtn.disabled = show;
            startBtn.innerHTML = show ? 
                '<i class="fas fa-spinner fa-spin"></i> Processing...' : 
                '<i class="fas fa-microphone"></i> Start Voice Authentication';
        }
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    getToastIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    closeModal() {
        document.getElementById('instructions-modal').classList.remove('active');
    }

    openModal() {
        document.getElementById('instructions-modal').classList.add('active');
    }

    // Customization functionality
    setupCustomizationListeners() {
        // Face design selection
        document.querySelectorAll('.face-option').forEach(option => {
            option.addEventListener('click', (e) => this.selectFaceDesign(e.currentTarget.dataset.face));
        });

        // Color scheme selection
        document.querySelectorAll('.color-option').forEach(option => {
            option.addEventListener('click', (e) => this.selectColorScheme(e.currentTarget.dataset.color));
        });

        // Size control
        const sizeSlider = document.getElementById('size-slider');
        if (sizeSlider) {
            sizeSlider.addEventListener('input', (e) => this.updateSize(e.target.value));
        }

        // Animation speed control
        const speedSlider = document.getElementById('speed-slider');
        if (speedSlider) {
            speedSlider.addEventListener('input', (e) => this.updateAnimationSpeed(e.target.value));
        }

        // Personality selection
        document.querySelectorAll('.personality-option').forEach(option => {
            option.addEventListener('click', (e) => this.selectPersonality(e.currentTarget.dataset.personality));
        });

        // Special effects toggles
        document.getElementById('glow-effect')?.addEventListener('change', (e) => this.toggleGlowEffect(e.target.checked));
        document.getElementById('particles-effect')?.addEventListener('change', (e) => this.toggleParticleEffect(e.target.checked));
        document.getElementById('sound-effects')?.addEventListener('change', (e) => this.toggleSoundEffects(e.target.checked));

        // Test emotions button
        document.getElementById('test-emotion')?.addEventListener('click', () => this.testEmotions());

        // Action buttons
        document.getElementById('reset-customization')?.addEventListener('click', () => this.resetCustomization());
        document.getElementById('save-customization')?.addEventListener('click', () => this.saveCustomization());
    }

    selectFaceDesign(faceType) {
        // Update selection
        document.querySelectorAll('.face-option').forEach(option => option.classList.remove('selected'));
        document.querySelector(`[data-face="${faceType}"]`).classList.add('selected');

        // Apply to preview robot
        const previewRobot = document.getElementById('preview-robot');
        const mainRobot = document.getElementById('ai-robot');
        
        // Remove existing face classes
        ['classic-face', 'friendly-face', 'modern-face', 'minimal-face'].forEach(cls => {
            previewRobot?.classList.remove(cls);
            if (mainRobot) mainRobot.classList.remove(cls);
        });

        // Add new face class
        previewRobot?.classList.add(`${faceType}-face`);
        if (mainRobot) mainRobot.classList.add(`${faceType}-face`);

        this.showToast(`Face design changed to ${faceType}`, 'info');
    }

    selectColorScheme(colorScheme) {
        // Update selection
        document.querySelectorAll('.color-option').forEach(option => option.classList.remove('selected'));
        document.querySelector(`[data-color="${colorScheme}"]`).classList.add('selected');

        // Apply color scheme
        this.applyColorScheme(colorScheme);
        this.showToast(`Color scheme changed to ${colorScheme}`, 'info');
    }

    applyColorScheme(colorScheme) {
        const colorSchemes = {
            'purple-pink': { primary: '#8b5cf6', secondary: '#ec4899' },
            'blue-cyan': { primary: '#3b82f6', secondary: '#06b6d4' },
            'green-emerald': { primary: '#10b981', secondary: '#34d399' },
            'orange-red': { primary: '#f59e0b', secondary: '#ef4444' },
            'purple-indigo': { primary: '#7c3aed', secondary: '#4f46e5' },
            'pink-rose': { primary: '#ec4899', secondary: '#f43f5e' }
        };

        const colors = colorSchemes[colorScheme];
        if (!colors) return;

        // Update CSS custom properties
        document.documentElement.style.setProperty('--accent-purple', colors.primary);
        document.documentElement.style.setProperty('--accent-pink', colors.secondary);

        // Apply colors directly to robot elements
        this.updateRobotColors(colors);
    }

    updateRobotColors(colors) {
        const previewRobot = document.getElementById('preview-robot');
        const mainRobot = document.getElementById('ai-robot');
        
        const robots = [previewRobot, mainRobot].filter(robot => robot);
        
        robots.forEach(robot => {
            // Update eyes
            const eyes = robot.querySelectorAll('.eye');
            eyes.forEach(eye => {
                eye.style.background = `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`;
                eye.style.boxShadow = `0 0 15px ${colors.primary}, 0 0 25px ${colors.primary}, inset 0 0 5px #fff`;
            });

            // Update mouth
            const mouth = robot.querySelector('.mouth');
            if (mouth) {
                mouth.style.background = `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`;
                mouth.style.boxShadow = `0 0 10px ${colors.primary}`;
            }

            // Update chest light
            const chestLight = robot.querySelector('.chest-light');
            if (chestLight) {
                chestLight.style.background = `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`;
                chestLight.style.boxShadow = `0 0 10px ${colors.primary}`;
            }

            // Update antenna tips
            const antennaTips = robot.querySelectorAll('.antenna::after');
            // Note: CSS pseudo-elements can't be directly styled with JS, so we use CSS custom properties
        });
    }

    updateSize(value) {
        const percentage = parseInt(value);
        const sizeClass = `size-${value}`;
        
        // Update display
        document.getElementById('size-display').textContent = `${percentage}%`;

        // Apply to robot containers
        const previewContainer = document.getElementById('preview-robot-container');
        const mainContainer = document.querySelector('.robot-container');
        
        // Remove existing size classes
        ['size-60', 'size-70', 'size-80', 'size-90', 'size-100', 'size-110', 'size-120', 'size-130', 'size-140'].forEach(cls => {
            previewContainer?.classList.remove(cls);
            mainContainer?.classList.remove(cls);
        });

        // Add new size class
        previewContainer?.classList.add(sizeClass);
        mainContainer?.classList.add(sizeClass);
    }

    updateAnimationSpeed(value) {
        const speed = parseInt(value);
        let speedText = 'Normal';
        
        if (speed < 75) speedText = 'Slow';
        else if (speed > 125) speedText = 'Fast';

        // Update display
        document.getElementById('speed-display').textContent = speedText;

        // Apply to robots
        const previewRobot = document.getElementById('preview-robot');
        const mainRobot = document.getElementById('ai-robot');

        // Remove existing speed classes
        ['slow-animation', 'fast-animation'].forEach(cls => {
            previewRobot?.classList.remove(cls);
            mainRobot?.classList.remove(cls);
        });

        // Add speed class
        if (speed < 75) {
            previewRobot?.classList.add('slow-animation');
            mainRobot?.classList.add('slow-animation');
        } else if (speed > 125) {
            previewRobot?.classList.add('fast-animation');
            mainRobot?.classList.add('fast-animation');
        }
    }

    selectPersonality(personality) {
        // Update selection
        document.querySelectorAll('.personality-option').forEach(option => option.classList.remove('selected'));
        document.querySelector(`[data-personality="${personality}"]`).classList.add('selected');

        this.showToast(`Personality changed to ${personality}`, 'info');
    }

    toggleGlowEffect(enabled) {
        const previewRobot = document.getElementById('preview-robot');
        const mainRobot = document.getElementById('ai-robot');

        console.log('Toggle glow effect:', enabled);

        if (enabled) {
            previewRobot?.classList.add('enhanced-glow');
            mainRobot?.classList.add('enhanced-glow');
            
            // Apply enhanced glow styles directly
            this.applyEnhancedGlow([previewRobot, mainRobot].filter(robot => robot));
            this.showToast('Enhanced glow effect enabled', 'info');
        } else {
            previewRobot?.classList.remove('enhanced-glow');
            mainRobot?.classList.remove('enhanced-glow');
            
            // Remove enhanced glow styles
            this.removeEnhancedGlow([previewRobot, mainRobot].filter(robot => robot));
            this.showToast('Enhanced glow effect disabled', 'info');
        }
    }

    applyEnhancedGlow(robots) {
        robots.forEach(robot => {
            const eyes = robot.querySelectorAll('.eye');
            const mouth = robot.querySelector('.mouth');
            const chestLight = robot.querySelector('.chest-light');

            eyes.forEach(eye => {
                const currentBg = getComputedStyle(eye).background;
                eye.style.boxShadow = `0 0 20px currentColor, 0 0 40px currentColor, 0 0 60px currentColor, 0 0 80px currentColor`;
            });

            if (mouth) {
                mouth.style.boxShadow = `0 0 20px currentColor, 0 0 40px currentColor, 0 0 60px currentColor`;
            }

            if (chestLight) {
                chestLight.style.boxShadow = `0 0 20px currentColor, 0 0 40px currentColor, 0 0 60px currentColor`;
            }
        });
    }

    removeEnhancedGlow(robots) {
        robots.forEach(robot => {
            const eyes = robot.querySelectorAll('.eye');
            const mouth = robot.querySelector('.mouth');
            const chestLight = robot.querySelector('.chest-light');

            eyes.forEach(eye => {
                eye.style.boxShadow = '';
            });

            if (mouth) {
                mouth.style.boxShadow = '';
            }

            if (chestLight) {
                chestLight.style.boxShadow = '';
            }
        });
    }

    toggleParticleEffect(enabled) {
        const previewContainer = document.getElementById('preview-robot-container');
        const mainContainer = document.querySelector('.robot-container');

        console.log('Toggle particle effect:', enabled);

        if (enabled) {
            previewContainer?.classList.add('particles');
            mainContainer?.classList.add('particles');
            
            // Create particle elements
            this.createParticles([previewContainer, mainContainer].filter(container => container));
            this.showToast('Particle effects enabled', 'info');
        } else {
            previewContainer?.classList.remove('particles');
            mainContainer?.classList.remove('particles');
            
            // Remove particle elements
            this.removeParticles([previewContainer, mainContainer].filter(container => container));
            this.showToast('Particle effects disabled', 'info');
        }
    }

    createParticles(containers) {
        containers.forEach(container => {
            // Remove existing particles
            this.removeParticles([container]);
            
            // Create particle container
            const particleContainer = document.createElement('div');
            particleContainer.className = 'particle-container';
            particleContainer.style.cssText = `
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                overflow: hidden;
            `;
            
            // Create particles
            for (let i = 0; i < 20; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.cssText = `
                    position: absolute;
                    width: 2px;
                    height: 2px;
                    background: linear-gradient(135deg, var(--accent-purple), var(--accent-pink));
                    border-radius: 50%;
                    opacity: 0.6;
                    animation: float-particle ${3 + Math.random() * 4}s linear infinite;
                    left: ${Math.random() * 100}%;
                    top: ${Math.random() * 100}%;
                    animation-delay: ${Math.random() * 2}s;
                `;
                particleContainer.appendChild(particle);
            }
            
            container.appendChild(particleContainer);
        });
    }

    removeParticles(containers) {
        containers.forEach(container => {
            const existingParticles = container.querySelector('.particle-container');
            if (existingParticles) {
                existingParticles.remove();
            }
        });
    }

    toggleSoundEffects(enabled) {
        // This would integrate with the TTS system
        this.showToast(`Sound effects ${enabled ? 'enabled' : 'disabled'}`, 'info');
    }

    testEmotions() {
        const emotions = ['happy', 'sad', 'thinking', 'surprised', 'dancing'];
        const previewRobot = document.getElementById('preview-robot');
        
        if (!previewRobot) return;

        let currentIndex = 0;
        const interval = setInterval(() => {
            if (currentIndex >= emotions.length) {
                clearInterval(interval);
                previewRobot.className = 'robot happy';
                return;
            }

            const emotion = emotions[currentIndex];
            previewRobot.className = `robot ${emotion}`;
            currentIndex++;
        }, 1000);
    }

    resetCustomization() {
        // Reset all settings to default
        this.selectFaceDesign('classic');
        this.selectColorScheme('purple-pink');
        this.updateSize(100);
        this.updateAnimationSpeed(100);
        this.selectPersonality('cheerful');
        
        // Reset toggles
        const glowEffect = document.getElementById('glow-effect');
        const particlesEffect = document.getElementById('particles-effect');
        const soundEffects = document.getElementById('sound-effects');
        
        if (glowEffect) glowEffect.checked = false;
        if (particlesEffect) particlesEffect.checked = false;
        if (soundEffects) soundEffects.checked = false;
        
        this.toggleGlowEffect(false);
        this.toggleParticleEffect(false);
        this.toggleSoundEffects(false);

        // Clear saved settings
        localStorage.removeItem('aiBuddyCustomization');

        this.showToast('Customization reset to default', 'info');
    }

    saveCustomization() {
        // Get current settings
        const settings = {
            faceDesign: document.querySelector('.face-option.selected')?.dataset.face || 'classic',
            colorScheme: document.querySelector('.color-option.selected')?.dataset.color || 'purple-pink',
            size: document.getElementById('size-slider')?.value || 100,
            animationSpeed: document.getElementById('speed-slider')?.value || 100,
            personality: document.querySelector('.personality-option.selected')?.dataset.personality || 'cheerful',
            glowEffect: document.getElementById('glow-effect')?.checked || false,
            particleEffect: document.getElementById('particles-effect')?.checked || false,
            soundEffects: document.getElementById('sound-effects')?.checked || false
        };

        // Save to localStorage
        localStorage.setItem('aiBuddyCustomization', JSON.stringify(settings));
        
        this.showToast('Customization saved successfully!', 'success');
    }

    loadCustomizationSettings() {
        const savedSettings = localStorage.getItem('aiBuddyCustomization');
        if (!savedSettings) return;

        try {
            const settings = JSON.parse(savedSettings);
            
            // Apply saved settings
            this.selectFaceDesign(settings.faceDesign);
            this.selectColorScheme(settings.colorScheme);
            this.updateSize(settings.size);
            this.updateAnimationSpeed(settings.animationSpeed);
            this.selectPersonality(settings.personality);
            
            // Apply toggles
            document.getElementById('glow-effect').checked = settings.glowEffect;
            document.getElementById('particles-effect').checked = settings.particleEffect;
            document.getElementById('sound-effects').checked = settings.soundEffects;
            
            this.toggleGlowEffect(settings.glowEffect);
            this.toggleParticleEffect(settings.particleEffect);
            this.toggleSoundEffects(settings.soundEffects);

        } catch (error) {
            console.error('Error loading customization settings:', error);
        }
    }

    initializeCustomization() {
        // Set default selections if none are selected
        setTimeout(() => {
            if (!document.querySelector('.face-option.selected')) {
                this.selectFaceDesign('classic');
            }
            if (!document.querySelector('.color-option.selected')) {
                this.selectColorScheme('purple-pink');
            }
            if (!document.querySelector('.personality-option.selected')) {
                this.selectPersonality('cheerful');
            }
        }, 100);
    }

    // Mobile-specific optimizations
    setupMobileOptimizations() {
        // Detect mobile device
        this.isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        this.isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        if (this.isMobile || this.isTouch) {
            // Add mobile-specific classes
            document.body.classList.add('mobile-device');
            
            // Optimize touch interactions
            this.setupTouchOptimizations();
            
            // Handle orientation changes
            this.setupOrientationHandling();
            
            // Optimize viewport for mobile
            this.optimizeViewport();
            
            // Add mobile-specific event listeners
            this.setupMobileEventListeners();
        }
    }

    setupTouchOptimizations() {
        // Prevent double-tap zoom on buttons
        document.querySelectorAll('button, .nav-btn, .record-btn').forEach(btn => {
            btn.addEventListener('touchend', (e) => {
                e.preventDefault();
                btn.click();
            });
        });

        // Optimize touch targets (minimum 44px)
        document.querySelectorAll('.nav-btn, .record-btn, .btn').forEach(btn => {
            btn.style.minHeight = '44px';
            btn.style.minWidth = '44px';
        });

        // Add touch feedback
        document.querySelectorAll('button, .nav-btn, .record-btn, .face-option, .color-option, .personality-option').forEach(element => {
            element.addEventListener('touchstart', () => {
                element.classList.add('touch-active');
            });
            
            element.addEventListener('touchend', () => {
                setTimeout(() => {
                    element.classList.remove('touch-active');
                }, 150);
            });
        });
    }

    setupOrientationHandling() {
        window.addEventListener('orientationchange', () => {
            // Delay to allow orientation change to complete
            setTimeout(() => {
                this.handleOrientationChange();
            }, 100);
        });

        // Also handle resize events
        window.addEventListener('resize', () => {
            this.handleOrientationChange();
        });
    }

    handleOrientationChange() {
        // Refresh robot positioning
        const robotContainer = document.querySelector('.robot-container');
        if (robotContainer) {
            robotContainer.style.transform = 'scale(1)';
            setTimeout(() => {
                robotContainer.style.transform = '';
            }, 50);
        }

        // Refresh customization preview
        const previewRobot = document.getElementById('preview-robot');
        if (previewRobot) {
            previewRobot.style.transform = 'scale(1)';
            setTimeout(() => {
                previewRobot.style.transform = '';
            }, 50);
        }
    }

    optimizeViewport() {
        // Ensure proper viewport meta tag
        let viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            viewport = document.createElement('meta');
            viewport.name = 'viewport';
            document.head.appendChild(viewport);
        }
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
    }

    setupMobileEventListeners() {
        // Prevent context menu on long press
        document.addEventListener('contextmenu', (e) => {
            if (this.isMobile) {
                e.preventDefault();
            }
        });

        // Handle back button on mobile
        window.addEventListener('popstate', (e) => {
            if (this.isMobile) {
                this.handleMobileBack();
            }
        });
    }

    handleMobileBack() {
        // Handle mobile back button navigation
        if (this.currentSection !== 'register') {
            this.switchSection('register');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.aiBuddyApp = new AIBuddyApp();
});

// Utility functions for external use
function setBuddyEmotion(emotion) {
    if (window.aiBuddyApp) {
        window.aiBuddyApp.setBuddyEmotion(emotion);
    }
}

function showToast(message, type) {
    if (window.aiBuddyApp) {
        window.aiBuddyApp.showToast(message, type);
    }
}
