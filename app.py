from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
import os
import tempfile
import uuid
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Ses fayllarını saxlamaq üçün qovluq
AUDIO_FOLDER = 'static/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# Global dəyişən
cleanup_thread_started = False

def cleanup_old_files():
    """Köhnə audio fayllarını təmizlə"""
    try:
        current_time = time.time()
        if os.path.exists(AUDIO_FOLDER):
            for filename in os.listdir(AUDIO_FOLDER):
                filepath = os.path.join(AUDIO_FOLDER, filename)
                if os.path.isfile(filepath):
                    # 1 saatdan köhnə faylları sil
                    if os.path.getctime(filepath) < current_time - 3600:
                        os.remove(filepath)
                        print(f"Silindi: {filename}")
    except Exception as e:
        print(f"Təmizlik xətası: {e}")

def cleanup_loop():
    """Təmizlik dövrüsü"""
    while True:
        cleanup_old_files()
        time.sleep(3600)  # Hər saat bir dəfə təmizlə

def start_cleanup_thread():
    """Təmizlik thread-ni başlat"""
    global cleanup_thread_started
    if not cleanup_thread_started:
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        cleanup_thread_started = True
        print("Təmizlik thread-i başladı")

def text_to_speech_az(text, filename):
    """
    Azərbaycan dilində mətni səsə çevirir
    """
    try:
        # gTTS ilə Azərbaycan dilində səs yarat
        tts = gTTS(text=text, lang='az', slow=False)
        filepath = os.path.join(AUDIO_FOLDER, filename)
        tts.save(filepath)
        return filepath
    except Exception as e:
        print(f"Səs yaratma xətası: {e}")
        return None

@app.route('/')
def index():
    # İlk requestdə təmizlik thread-ni başlat
    if not cleanup_thread_started:
        start_cleanup_thread()
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'JSON məlumatı alınmadı'})
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'error': 'Boş mətn daxil edildi'})
        
        if len(text) > 5000:
            return jsonify({'success': False, 'error': 'Mətn çox uzundur (maksimum 5000 simvol)'})
        
        # Unikal fayl adı yarat
        filename = f"speech_{uuid.uuid4().hex}.mp3"
        filepath = text_to_speech_az(text, filename)
        
        if filepath and os.path.exists(filepath):
            return jsonify({
                'success': True, 
                'audio_url': f'/static/audio/{filename}',
                'filename': filename
            })
        else:
            return jsonify({'success': False, 'error': 'Səs faylı yaradıla bilmədi'})
            
    except Exception as e:
        print(f"Convert xətası: {e}")
        return jsonify({'success': False, 'error': f'Server xətası: {str(e)}'})

@app.route('/health')
def health_check():
    """Sağlamlıq yoxlaması üçün endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Azərbaycan Text-to-Speech'})

@app.before_request
def before_first_request():
    """İlk requestdən əvvəl təmizlik thread-ni başlat"""
    global cleanup_thread_started
    if not cleanup_thread_started:
        start_cleanup_thread()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'False').lower() == 'true'
    # Server başlayanda təmizlik thread-ni başlat
    if not debug_mode:
        start_cleanup_thread()
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
