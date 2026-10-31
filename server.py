# "Yeni video ne zaman?" -> sana WhatsApp'tan sorulur, cevabın web sohbetinde görünür.
# Bu dosya whatsapp_bot.py'nin yerini alır (hem destek botu hem sahip cevabı).
# Kurulum: pip install flask twilio
# Ortam değişkenleri:
#   TWILIO_SID, TWILIO_TOKEN
#   TWILIO_WHATSAPP_FROM  örn: whatsapp:+14155238886 (Twilio sandbox numarası)
#   OWNER_WHATSAPP        senin numaran, örn: whatsapp:+905XXXXXXXXX
# Çalıştır: python server.py  -> ngrok vb. ile dışarı aç
# Twilio WhatsApp "When a message comes in": https://SENIN-ADRESIN/whatsapp
# Web sayfası aynı adresin ana sayfasında açılır (static/index.html).
import os, threading
from flask import Flask, request, jsonify, send_from_directory
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from werkzeug.middleware.proxy_fix import ProxyFix
from bot_core import reply

app = Flask(__name__, static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

OWNER = os.environ["OWNER_WHATSAPP"]
FROM = os.environ["TWILIO_WHATSAPP_FROM"]
twilio = Client(os.environ["TWILIO_SID"], os.environ["TWILIO_TOKEN"])
validator = RequestValidator(os.environ["TWILIO_TOKEN"])

questions = {}   # id -> {"q": str, "answer": str | None}
counter = 0
lock = threading.Lock()

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.post("/ask")
def ask():
    global counter
    q = (request.get_json(silent=True) or {}).get("q", "").strip()[:200]
    if not q:
        return jsonify(error="bos"), 400
    with lock:
        if sum(1 for v in questions.values() if v["answer"] is None) >= 20:
            return jsonify(error="cok-fazla"), 429
        counter += 1
        qid = counter
        questions[qid] = {"q": q, "answer": None}
    twilio.messages.create(
        from_=FROM, to=OWNER,
        body=f'Web sitesinde soruldu #{qid}: "{q}"\n\nCevaplamak için şöyle yaz:\n{qid} Cuma günü geliyor',
    )
    return jsonify(id=qid)

@app.get("/answer/<int:qid>")
def answer(qid):
    item = questions.get(qid)
    if not item:
        return jsonify(error="yok"), 404
    return jsonify(answer=item["answer"])

@app.post("/whatsapp")
def whatsapp():
    if not validator.validate(request.url, request.form, request.headers.get("X-Twilio-Signature", "")):
        return "", 403
    sender, body = request.form.get("From", ""), request.form.get("Body", "").strip()
    resp = MessagingResponse()
    if sender != OWNER:                      # herkes için normal destek botu
        resp.message(reply(body))
        return str(resp)
    with lock:                               # sahibin cevabı
        pending = [i for i, v in questions.items() if v["answer"] is None]
        first, _, rest = body.partition(" ")
        if first.isdigit() and int(first) in questions and rest:
            qid, text = int(first), rest
        elif pending:
            qid, text = max(pending), body   # numara yazmazsan en son soruya gider
        else:
            resp.message("Bekleyen soru yok.")
            return str(resp)
        questions[qid]["answer"] = text
    resp.message(f"#{qid} için cevabın web sohbetine gönderildi.")
    return str(resp)

if __name__ == "__main__":
    app.run(port=5000)
