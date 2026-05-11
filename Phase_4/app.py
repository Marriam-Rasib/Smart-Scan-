from flask import Flask, render_template, request

from inference.classify import classify_contract
from inference.detect_vulnerability import detect_vulnerability

app = Flask(__name__)


@app.route('/')
def home():

    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():

    file = request.files['contract']

    code = file.read().decode('utf-8')

    category = classify_contract(code)

    vulnerability, confidence = detect_vulnerability(code)

    return render_template(
        'result.html',
        category=category,
        vulnerability=vulnerability,
        confidence=round(confidence * 100, 2)
    )


if __name__ == '__main__':

    app.run(debug=True)
