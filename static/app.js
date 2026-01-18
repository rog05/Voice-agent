document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const recordBtn = document.getElementById('record-btn');
    const chatHistory = document.getElementById('chat-history');
    const waveformContainer = document.getElementById('waveform');
    const statusText = document.getElementById('status-text');
    const connectionStatus = document.getElementById('connection-status');
    const currentLanguage = document.getElementById('current-language');
    const statCount = document.getElementById('stat-count');
    const statLang = document.getElementById('stat-lang');
    const clinicDetails = document.getElementById('clinic-details');

    // Audio State
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let audioContext;
    let analyser;
    let dataArray;
    let animationId;

    // Initialize Waveform
    for (let i = 0; i < 20; i++) {
        const bar = document.createElement('div');
        bar.className = 'bar';
        waveformContainer.appendChild(bar);
    }
    const bars = document.querySelectorAll('.bar');

    // Fetch initial data
    fetchStats();
    fetchClinicInfo();

    // Event Listeners
    recordBtn.addEventListener('mousedown', startRecording);
    recordBtn.addEventListener('mouseup', stopRecording);
    recordBtn.addEventListener('mouseleave', () => {
        if (isRecording) stopRecording();
    });

    // Mobile touch support
    recordBtn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startRecording();
    });
    recordBtn.addEventListener('touchend', (e) => {
        e.preventDefault();
        stopRecording();
    });

    async function startRecording() {
        if (isRecording) return;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Setup MediaRecorder
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = processAudio;

            mediaRecorder.start();
            
            // Setup Audio Visualization
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 64;
            dataArray = new Uint8Array(analyser.frequencyBinCount);
            
            isRecording = true;
            updateUIState('recording');
            visualize();

        } catch (err) {
            console.error('Error accessing microphone:', err);
            alert('Could not access microphone. Please ensure permission is granted.');
        }
    }

    function stopRecording() {
        if (!isRecording) return;
        
        mediaRecorder.stop();
        isRecording = false;
        
        // Stop visualization
        cancelAnimationFrame(animationId);
        if (audioContext) audioContext.close();
        
        // Stop tracks
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        updateUIState('processing');
    }

    function visualize() {
        if (!isRecording) return;
        
        animationId = requestAnimationFrame(visualize);
        analyser.getByteFrequencyData(dataArray);
        
        bars.forEach((bar, index) => {
            // Map roughly to the frequency data
            const value = dataArray[index] || 0;
            const percentage = Math.max(10, (value / 255) * 100);
            bar.style.height = `${percentage}%`;
        });
    }

    async function processAudio() {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.wav');

        try {
            const response = await fetch('/api/process-audio', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success) {
                // Add user transcript
                addMessage(data.transcript, 'user');
                
                // Add agent response
                setTimeout(() => {
                    addMessage(data.response_text, 'agent');
                    playAudio(data.audio_url);
                    
                    // Update stats
                    currentLanguage.textContent = data.language;
                    updateUIState('ready');
                    fetchStats(); // Refresh stats
                }, 500);
                
            } else {
                console.error('Processing error:', data.error);
                addMessage('Sorry, I encountered an error processing your request.', 'system');
                updateUIState('ready');
            }

        } catch (err) {
            console.error('API Error:', err);
            addMessage('Network error. Please try again.', 'system');
            updateUIState('ready');
        }
    }

    function playAudio(url) {
        const audio = new Audio(url);
        updateUIState('speaking');
        audio.play().catch(e => console.error("Playback failed", e));
        
        audio.onended = () => {
            updateUIState('ready');
        };
    }

    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;
        
        messageDiv.appendChild(contentDiv);
        chatHistory.appendChild(messageDiv);
        
        // Auto scroll
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function updateUIState(state) {
        recordBtn.classList.remove('recording');
        
        switch(state) {
            case 'ready':
                statusText.textContent = 'Hold to Speak';
                connectionStatus.style.background = '#10B981'; // Green
                break;
            case 'recording':
                statusText.textContent = 'Listening...';
                recordBtn.classList.add('recording');
                connectionStatus.style.background = '#EF4444'; // Red
                break;
            case 'processing':
                statusText.textContent = 'Processing...';
                connectionStatus.style.background = '#F59E0B'; // Orange
                break;
            case 'speaking':
                statusText.textContent = 'Speaking...';
                connectionStatus.style.background = '#3B82F6'; // Blue
                break;
        }
    }

    async function fetchStats() {
        try {
            const response = await fetch('/api/session-stats');
            const data = await response.json();
            statCount.textContent = data.total_interactions;
            
            // Find most used language
            if (data.by_language && Object.keys(data.by_language).length > 0) {
                const topLang = Object.entries(data.by_language).sort((a,b) => b[1]-a[1])[0][0];
                statLang.textContent = topLang;
            }
            
        } catch (err) {
            console.error('Stats error:', err);
        }
    }

    async function fetchClinicInfo() {
        try {
            const response = await fetch('/api/clinic-info');
            const data = await response.json();
            
            clinicDetails.innerHTML = `
                <p><strong>${data.clinic_name}</strong></p>
                <p>${data.location}</p>
                <p>Dr. ${data.doctor_name}</p>
                <p class="small text-muted">${data.working_hours.monday_friday}</p>
            `;
            
        } catch (err) {
            console.error('Info error:', err);
        }
    }
});
