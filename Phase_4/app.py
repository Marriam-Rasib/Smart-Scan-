from flask import Flask, render_template, request
from inference.predict import predict
from inference.vuln_predict import predict_vulnerability
from pyngrok import ngrok

# ⚠️ Replace with your real token if needed
ngrok.set_auth_token("2wJFwPm2ucpHN33doGCjEkWuJOe_81h28gBC7Qk1yLsZK6zdL")

app = Flask(__name__)

# ✅ Allowed file types
ALLOWED_EXTENSIONS = {"sol", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("contract")

    # ❌ No file selected
    if not file or file.filename == "":
        return "No file selected"

    # ❌ Invalid file type
    if not allowed_file(file.filename):
        return "Invalid file type. Upload .sol or .txt"

    # ❌ File reading error
    try:
        code = file.read().decode("utf-8")
    except Exception:
        return "Error reading file. Make sure it's a valid text file."

    # 🔹 Smart Contract Classification
    try:
        category = predict(code)
    except Exception as e:
        print("Classification error:", e)
        category = "Unknown"

    # 🔹 Vulnerability Detection
    try:
        vuln_result = predict_vulnerability(code)

    except Exception as e:
        print("Vulnerability error:", e)

        vuln_result = {
            "status": "Error",
            "top_vulnerability": "Error",
            "confidence": 0,
            "all_scores": {}
        }

    # ✅ Render results page
    return render_template(
        "result.html",
        category=category,
        vuln_status=vuln_result["status"],
        vulnerability=vuln_result["top_vulnerability"],
        confidence=vuln_result["confidence"],
        all_scores=vuln_result["all_scores"]
    )


if __name__ == "__main__":
    # 🔹 Start ngrok tunnel
    public_url = ngrok.connect(5000)
    print("Public URL:", public_url)

    # 🔹 Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
