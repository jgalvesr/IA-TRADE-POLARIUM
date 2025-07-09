from flask import Flask, render_template, request, jsonify
from polariumapi.stable_api import PolariumAPI

class ExtraSuperGPTEnhancer:
    def generate_response(self, prompt):
        closes = [float(s) for s in prompt.split("[")[-1].split("]")[0].split(",")]
        if closes[-1] > closes[0]:
            return "DECISÃO: COMPRAR. O preço subiu."
        elif closes[-1] < closes[0]:
            return "DECISÃO: VENDER. O preço caiu."
        else:
            return "DECISÃO: MANTER. O preço está estável."

app = Flask(__name__)
ai = ExtraSuperGPTEnhancer()

# Login na Polarium
polarium = import os

polarium = PolariumAPI(
    email=os.getenv("POLARIUM_EMAIL"),
    password=os.getenv("POLARIUM_PASSWORD")
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/candles")
def get_candles():
    symbol = request.args.get("symbol", "BTCUSD")
    interval = request.args.get("interval", "1m")
    candles = polarium.get_candles(symbol=symbol, interval=interval, limit=60)
    closes = [float(c['close']) for c in candles]
    timestamps = [c['timestamp'] for c in candles]
    return jsonify({"timestamps": timestamps, "closes": closes})

@app.route("/api/ia-decision")
def ia_decision():
    symbol = request.args.get("symbol", "BTCUSD")
    interval = request.args.get("interval", "1m")
    candles = polarium.get_candles(symbol=symbol, interval=interval, limit=60)
    closes = [float(c['close']) for c in candles]
    prompt = (
        f"Com base nos últimos 60 fechamentos de {symbol} com intervalo {interval}: {closes}, "
        "a IA deve decidir COMPRAR, VENDER ou MANTER, com raciocínio lógico e técnico."
    )
    result = ai.generate_response(prompt)
    return jsonify({"decision": result})

@app.route("/api/trade", methods=["POST"])
def trade():
    data = request.json
    symbol = data.get("symbol", "BTCUSD")
    side = data.get("side")
    amount = data.get("amount", 10)
    try:
        response = polarium.place_order(symbol=symbol, side=side, amount=amount, type="market")
        return jsonify({"status": "ok", "response": response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
