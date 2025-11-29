from flask import Flask, render_template, request, jsonify, send_file
import pyttsx3
import os
import uuid
import threading

app = Flask(__name__)

# Ses fayllarını saxlamaq üçün qovluq
AUDIO_FOLDER = 'static/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# TTS mühərriki
tts_engine = None
engine_lock = threading.Lock()

def get_tts_engine():
    """TTS mühərrikini al/yarat"""
    global tts_engine
    with engine_lock:
        if tts_engine is None:
            try:
                tts_engine = pyttsx3.init()
                
                # Səs parametrlərini tənzimlə
                voices = tts_engine.getProperty('voices')
                
                # Windows və Linux üçün müxtəlif səs seçimləri
                for voice in voices:
                    # Azərbaycan dili üçün uyğun səs axtar
                    if 'turkish' in voice.name.lower() or 'azerbaijani' in voice.name.lower():
                        tts_engine.setProperty('voice', voice.id)
                        break
                    # Əgər türk səsi tapılsa, onu istifadə et (oxşar dil qrupu)
                    elif 'turk' in voice.name.lower():
                        tts_engine.setProperty('voice', voice.id)
                        break
                
                # Sürəti tənzimlə
                tts_engine.setProperty('rate', 150)  # Orta sürət
                
            except Exception as e:
                print(f"TTS mühərriki yaradılarkən xəta: {e}")
                return None
    return tts_engine

def text_to_speech_az(text, filename):
    """
    Azərbaycan dilində mətni səsə çevirir (pyttsx3 ilə)
    """
    try:
        engine = get_tts_engine()
        if engine is None:
            return None
            
        filepath = os.path.join(AUDIO_FOLDER, filename)
        
        # Səs faylını yadda saxla
        engine.save_to_file(text, filepath)
        engine.runAndWait()
        
        # Mühərriki sıfırla növbəti istifadə üçün
        engine.stop()
        
        return filepath if os.path.exists(filepath) else None
        
    except Exception as e:
        print(f"Səs yaratma xətası: {e}")
        return None

@app.route('/')
def index():
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
        
        if len(text) > 2000:  # pyttsx3 üçün daha kiçik limit
            return jsonify({'success': False, 'error': 'Mətn çox uzundur (maksimum 2000 simvol)'})
        
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
            return jsonify({'success': False, 'error': 'Səs faylı yaradıla bilmədi. Sistem Azərbaycan dilini dəstəkləyə bilmir.'})
            
    except Exception as e:
        print(f"Convert xətası: {e}")
        return jsonify({'success': False, 'error': f'Server xətası: {str(e)}'})

@app.route('/health')
def health_check():
    """Sağlamlıq yoxlaması üçün endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Azərbaycan Text-to-Speech'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
