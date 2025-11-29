from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
import os
import tempfile
import uuid
from datetime import datetime

app = Flask(__name__)

# Ses fayllarını saxlamaq üçün müvəqqəti qovluq
AUDIO_FOLDER = 'static/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

def text_to_speech_az(text, filename):
    """
    Azərbaycan dilində mətni səsə çevirir
    """
    try:
        tts = gTTS(text=text, lang='az', slow=False)
        filepath = os.path.join(AUDIO_FOLDER, filename)
        tts.save(filepath)
        return filepath
    except Exception as e:
        print(f"Xəta: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'success': False, 'error': 'Boş mətn daxil edildi'})
        
        # Unikal fayl adı yarat
        filename = f"speech_{uuid.uuid4().hex}.mp3"
        filepath = text_to_speech_az(text, filename)
        
        if filepath:
            return jsonify({
                'success': True, 
                'audio_url': f'/{filepath}',
                'filename': filename
            })
        else:
            return jsonify({'success': False, 'error': 'Səs yaradılarkən xəta baş verdi'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    return send_file(f'static/audio/{filename}')

# Təmizlik: köhnə audio fayllarını sil
def cleanup_old_files():
    try:
        current_time = datetime.now()
        for filename in os.listdir(AUDIO_FOLDER):
            filepath = os.path.join(AUDIO_FOLDER, filename)
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if (current_time - file_time).seconds > 3600:  # 1 saatdan köhnə faylları sil
                os.remove(filepath)
    except Exception as e:
        print(f"Təmizlik xətası: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
