from flask import Flask, request, send_file, render_template_string
from gtts import gTTS
import tempfile
import os

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="az">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>AzTTS — Azərbaycan dilində TTS</title>
  <meta name="description" content="Azərbaycan dilində mətnin səsə çevrilməsi — pulsuz TTS.">
  <meta name="keywords" content="tts, azerbaijan tts, text to speech, azərbaycanca səs">
</head>
<body>
  <h1>AzTTS</h1>
  <form action="/speak" method="post">
    <textarea name="text" rows="6" cols="60" placeholder="Mətni yaz..."></textarea><br>
    <label><input type="radio" name="voice" value="girl" checked> Qız səsi</label>
    <label><input type="radio" name="voice" value="boy"> Oğlan səsi</label><br><br>
    <button type="submit">Səsləndir</button>
  </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return HTML

@app.route("/speak", methods=["POST"])
def speak():
    text = request.form.get("text", "").strip()
    voice = request.form.get("voice", "girl")

    if not text:
        return "Mətn daxil edilməyib."

    if len(text) > 3000:
        return "Mətn çox uzundur. Limit: 3000."

    # Qız səsi → Azərbaycan
    # Oğlan səsi → Türkiyə ləhcəsi kimi fərqli ton (Google workaround)
    lang = "az" if voice == "girl" else "tr"

    tts = gTTS(text=text, lang=lang, slow=False)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)

    return send_file(tmp.name, mimetype="audio/mpeg", as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
