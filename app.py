from flask import Flask, request, send_file, render_template_string
import torch
from torch import inference_mode
from transformers import pipeline
import uuid
import os

app = Flask(__name__)

# Az dilində yüngül model
pipe = pipeline("text-to-speech", model="facebook/mms-tts-az", device="cpu")

HTML = """
<!DOCTYPE html>
<html lang="az">
<head>
<meta charset="UTF-8">
<title>AxtarGet TTS</title>
<style>
body {font-family: Arial; background:#111; color:#eee; text-align:center; padding:40px;}
input, textarea {width:90%%; padding:12px; border-radius:12px; border:none; margin-top:10px;}
button {margin-top:20px; padding:15px 40px; background:#00ff88; border:none; border-radius:12px; font-size:18px; cursor:pointer;}
.container {max-width:500px; margin:auto; background:#222; padding:30px; border-radius:20px;}
</style>
</head>
<body>
<div class="container">
<h2>AxtarGet – Mətn → Səs</h2>
<form action="/tts" method="post">
<textarea name="text" rows="5" placeholder="Mətni yaz..."></textarea>
<button type="submit">Səsi Yarat</button>
</form>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/tts", methods=["POST"])
def tts():
    text = request.form.get("text")
    if not text:
        return "Mətn tapılmadı"

    out = pipe(text)
    file_id = str(uuid.uuid4()) + ".mp3"
    with open(file_id, "wb") as f:
        f.write(out["audio"])

    return send_file(file_id, mimetype="audio/mpeg")
