import re
from flask import Flask, jsonify, request, render_template
from pratyahara_engine import PratyaharaEngine, InvalidPratyaharaError, SEQUENCE

app = Flask(__name__)
engine = PratyaharaEngine(SEQUENCE, convention="ashtadhyayi")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/pratyahara", methods=["POST"])
def pratyahara():
    text = (request.get_json(silent=True) or {}).get("text", "")
    tokens = [t for t in re.split(r"[,\s]+", text) if t]
    results = []

    for token in tokens:
        if token.lower() == "all":
            for r in engine.generate_all():
                results.append({"input": r["notation"], "sounds": r["sounds"], "ok": True})
            continue
        try:
            results.append({"input": token,
                            "sounds": engine.get_pratyahara(token),
                            "ok": True})
        except InvalidPratyaharaError:
            results.append({"input": token, "ok": False,
                            "error": "Not a recognized Paninian pratyahara"})
        except ValueError as e:
            results.append({"input": token, "ok": False, "error": str(e)})

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)