
import joblib

model = joblib.load("models/xgb_model.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
encoder = joblib.load("models/category_encoder.pkl")

def predict(code):
    X = vectorizer.transform([code])
    pred = model.predict(X)[0]
    return encoder.inverse_transform([pred])[0]
