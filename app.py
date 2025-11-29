from flask import Flask, render_template, request, jsonify, send_file
from gtts import gTTS
import os
import uuid

app = Flask(__name__)

# Ses fayllarını saxlamaq üçün qovluq
AUDIO_FOLDER = 'static/audio'
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
