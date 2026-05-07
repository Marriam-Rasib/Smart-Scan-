import joblib


def save_model(model, filepath):

    joblib.dump(model, filepath)

    print(f"Saved model to {filepath}")
