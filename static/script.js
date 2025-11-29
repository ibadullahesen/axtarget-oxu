class TextToSpeechApp {
    constructor() {
        this.audioPlayer = document.getElementById('audioPlayer');
        this.textInput = document.getElementById('textInput');
        this.convertBtn = document.getElementById('convertBtn');
        this.playBtn = document.getElementById('playBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.statusMessage = document.getElementById('statusMessage');
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        this.convertBtn.addEventListener('click', () => this.convertTextToSpeech());
        this.playBtn.addEventListener('click', () => this.playAudio());
        this.clearBtn.addEventListener('click', () => this.clearAll());
        
        this.audioPlayer.addEventListener('ended', () => {
            this.playBtn.textContent = 'Dinlə';
        });
        
        this.audioPlayer.addEventListener('play', () => {
            this.playBtn.textContent = 'Dayandır';
        });
        
        this.audioPlayer.addEventListener('pause', () => {
            this.playBtn.textContent = 'Dinlə';
        });
    }
    
    async convertTextToSpeech() {
        const text = this.textInput.value.trim();
        
        if (!text) {
            this.showMessage('Zəhmət olmasa mətn daxil edin', 'error');
            return;
        }
        
        if (text.length > 1000) {
            this.showMessage('Mətn çox uzundur (maksimum 1000 simvol)', 'error');
            return;
        }
        
        this.showMessage('Mətn səsə çevrilir...', 'success');
        this.convertBtn.disabled = true;
        this.convertBtn.textContent = 'Çevrilir...';
        
        try {
            const response = await fetch('/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.audioPlayer.src = data.audio_url;
                this.audioPlayer.style.display = 'block';
                this.playBtn.disabled = false;
                this.showMessage('Mətn uğurla səsə çevrildi!', 'success');
            } else {
                this.showMessage('Xəta: ' + data.error, 'error');
            }
            
        } catch (error) {
            this.showMessage('Şəbəkə xətası: ' + error.message, 'error');
        } finally {
            this.convertBtn.disabled = false;
            this.convertBtn.textContent = 'Səsə Çevir';
        }
    }
    
    playAudio() {
        if (this.audioPlayer.paused) {
            this.audioPlayer.play();
        } else {
            this.audioPlayer.pause();
        }
    }
    
    clearAll() {
        this.textInput.value = '';
        this.audioPlayer.src = '';
        this.audioPlayer.style.display = 'none';
        this.playBtn.disabled = true;
        this.hideMessage();
    }
    
    showMessage(message, type) {
        this.statusMessage.textContent = message;
        this.statusMessage.className = `status-message ${type}`;
        this.statusMessage.style.display = 'block';
    }
    
    hideMessage() {
        this.statusMessage.style.display = 'none';
    }
}

// Tətbiqi işə sal
document.addEventListener('DOMContentLoaded', () => {
    new TextToSpeechApp();
});
