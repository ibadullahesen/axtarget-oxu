from flask import Flask, request, send_file, render_template_string, after_this_request
from TTS.api import TTS
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "temp_audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 2 real Azərbaycan səsi (əvvəlcədən yüklənir)
print("Aygün və İbad səsləri yüklənir...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False, progress_bar=True)

HTML = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Pulsuz Azərbaycan mətn səsləndirmə – kitab oxuyan AI. Aygün (qız) və İbad (oğlan) səsi ilə mükəmməl tələffüz, nəfəs, vurğu. PDF, Word, kitab oxutmaq üçün ən yaxşı alət.">
    <meta name="keywords" content="azərbaycan səs, kitab oxu, mətn səsləndirmə, AI səs, pulsuz tts, azeri tts, aygün səsi, ibad səsi">
    <meta name="author" content="AxtarGet">
    <title>oxu.axtarget.xyz – Pulsuz Kitab Oxuyan AI (Azərbaycan)</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="icon" href="https://axtarget.xyz/favicon.ico">
</head>
<body class="bg-gradient-to-br from-purple-900 via-black to-indigo-900 min-h-screen text-white">
    <div class="container mx-auto px-6 py-12 max-w-5xl">
        <h1 class="text-5xl md:text-7xl font-black text-center bg-gradient-to-r from-cyan-400 to-pink-500 bg-clip-text text-transparent mb-6">
            oxu.axtarget.xyz
        </h1>
        <p class="text-xl md:text-2xl text-center text-gray-300 mb-12">
            Azərbaycanın ən real kitab oxuyan AI-si<br>
            <span class="text-cyan-400 font-bold">Aygün (qız)</span> və <span class="text-pink-400 font-bold">İbad (oğlan)</span> səsi ilə
        </p>

        <form method="post" class="bg-white/10 backdrop-blur-xl rounded-3xl p-8 md:p-12 shadow-2xl border border-white/20">
            <div class="mb-8">
                <label class="block text-2xl font-bold mb-4 text-cyan-300">Mətni bura yaz və ya yapışdır</label>
                <textarea name="text" rows="10" required placeholder="Buraya kitab mətnini, dərsliyi və ya istənilən mətni yaz..." class="w-full px-6 py-5 rounded-2xl bg-white/10 border border-white/30 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 text-lg"></textarea>
            </div>

            <div class="grid md:grid-cols-2 gap-6 mb-8">
                <div>
                    <label class="block text-xl font-bold mb-3">Səs seçin</label>
                    <select name="voice" class="w-full px-6 py-4 rounded-xl bg-white/10 border border-white/30 text-white text-lg">
                        <option value="aygun">♀️ Aygün (Qız səsi – yumşaq, gözəl)</option>
                        <option value="ibad" selected>♂️ İbad (Oğlan səsi – dərin, güclü)</option>
                    </select>
                </div>
                <div class="flex items-end">
                    <button type="submit" class="w-full py-6 bg-gradient-to-r from-cyan-500 to-pink-600 text-white text-2xl md:text-3xl font-black rounded-2xl hover:scale-105 transition shadow-xl">
                        OXUTDUR
                    </button>
                </div>
            </div>
        </form>

        {% if audio_file %}
        <div class="mt-12 bg-green-600/20 border-4 border-green-400 rounded-3xl p-10 text-center">
            <p class="text-3xl font-bold text-green-300 mb-8">Mətn uğurla oxundu!</p>
            <audio controls class="w-full mb-6">
                <source src="{{ url_for('play', filename=audio_file) }}" type="audio/wav">
            </audio>
            <br>
            <a href="{{ url_for('download', filename=audio_file) }}" class="inline-block px-12 py-6 bg-green-600 text-white text-2xl font-bold rounded-2xl hover:bg-green-700">
                MP3 ENDİR
            </a>
        </div>
        {% endif %}

        <footer class="text-center mt-20 text-gray-500">
            © 2025 <a href="https://axtarget.xyz" class="text-cyan-400 font-bold">AxtarGet</a> – Azərbaycanın pulsuz AI xidmətləri
        </footer>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form["text"].strip()
        voice_choice = request.form["voice"]
        
        speaker_wav = "voices/aygun.wav" if voice_choice == "aygun" else "voices/ibad.wav"
        output_file = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.wav")
        
        tts.tts_to_file(text=text, speaker_wav=speaker_wav, language="az", file_path=output_file)
        
        filename = os.path.basename(output_file)
        return render_template_string(HTML, audio_file=filename)
    
    return render_template_string(HTML)

@app.route("/play/<filename>")
def play(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    response = send_file(file_path, as_attachment=True, download_name="oxunan_metn.mp3")
    @after_this_request
    def delete_file(resp):
        try: os.remove(file_path)
        except: pass
        return resp
    return response

# Procfile ilə işləyəcək – heç nə yazma
