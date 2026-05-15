
from flask import Flask, render_template, request
from inference.predict import predict

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["contract"]
    code = file.read().decode("utf-8")

    category = predict(code)

    return render_template("result.html", category=category)

if __name__ == "__main__":
    app.run(debug=True)
