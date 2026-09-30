import re
from flask import Flask, jsonify, request, render_template
from pratyahara_engine import PratyaharaEngine, InvalidPratyaharaError, SEQUENCE

app = Flask(__name__)

# "rule_based" = every grammatically valid pratyahara (291).
# "ashtadhyayi" = only the 43 names in the hand-typed list.
engine = PratyaharaEngine(SEQUENCE, convention="rule_based")


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
        except ValueError as e:      # includes InvalidPratyaharaError
            results.append({"input": token, "ok": False, "error": str(e)})

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)