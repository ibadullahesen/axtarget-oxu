# app.py
import os
import tempfile
import subprocess
from flask import Flask, request, send_file, render_template_string, jsonify

# Config from env
MODEL_NAME = os.environ.get("MODEL_NAME", "")  # set this in Render settings (see README below)
VOICE_GIRL = os.environ.get("VOICE_GIRL", "voice_girl")  # optional speaker token for advanced models
VOICE_BOY  = os.environ.get("VOICE_BOY",  "voice_boy")
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)

HTML_HOME = """
<!doctype html>
<html lang="az">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>AzTTS — Pulsuz TTS</title>
  <meta name="description" content="Azərbaycanca mətn → insan tərzi səs (pulsuz, Render üzərində)."/>
  <meta name="keywords" content="Azerbaijan TTS, Azərbaycan səsi, text to speech, pulsuz tts"/>
</head>
<body>
  <h1>AzTTS</h1>
  <form action="/speak" method="post">
    <textarea name="text" rows="6" cols="60" placeholder="Mətni buraya yaz..."></textarea><br/>
    <label><input type="radio" name="voice" value="girl" checked/> Qız səsi</label>
    <label><input type="radio" name="voice" value="boy"/> Oğlan səsi</label><br/>
    <button type="submit">Səsləndir</button>
  </form>
  <p>Qeyd: server Coqui TTS istifadə edir. Əgər MODEL_NAME boşdursa, admin modeli təyin etməlidir.</p>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_HOME)

def synthesize_with_tts(model_name: str, text: str, speaker: str=None):
    """
    Uses Coqui TTS CLI to synthesize text to a temporary mp3 file, returns path.
    Requires `tts` to be installed and model available (it will auto-download first time).
    MODEL_NAME should be a valid model name from `tts --list_models`.
    """
    if not model_name:
        raise RuntimeError("MODEL_NAME not configured. Set MODEL_NAME environment variable.")
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(tmp_fd)
    cmd = ["tts", "--model_name", model_name, "--text", text, "--out_path", tmp_path]
    if speaker:
        # many Coqui models accept --speaker_wav or --speaker_idx depending on model
        # we try a generic speaker param (may be ignored if model doesn't support).
        cmd += ["--speaker_wav", speaker]  # best-effort; if not supported, CLI ignores or errors
    # Run the CLI (blocking)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"TTS failed: {proc.returncode}\nstdout:{proc.stdout}\nstderr:{proc.stderr}")
    return tmp_path

@app.route("/speak", methods=["POST"])
def speak():
    text = request.form.get("text") or request.json.get("text","")
    voice = request.form.get("voice") or request.json.get("voice","girl")
    if not text:
        return jsonify({"error":"No text provided"}), 400

    # basic safety / length limit (avoid abuse)
    if len(text) > 3000:
        return jsonify({"error":"Text too long (limit 3000 chars)"}), 400

    model = MODEL_NAME
    speaker = VOICE_GIRL if voice == "girl" else VOICE_BOY
    try:
        mp3_path = synthesize_with_tts(model, text, speaker=speaker)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return send_file(mp3_path, mimetype="audio/mpeg", as_attachment=False, download_name="speech.mp3")

if __name__ == "__main__":
    # for local dev only; Render will use Gunicorn
    app.run(host="0.0.0.0", port=PORT)
