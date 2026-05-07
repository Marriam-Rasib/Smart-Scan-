from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)


def evaluate_model(y_test, y_pred):

    print("\n===== MODEL RESULTS =====")

    print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")

    print(f"Precision: {precision_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")

    print(f"Recall   : {recall_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")

    print(f"F1 Score : {f1_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")

    print("\nClassification Report:\n")

    print(classification_report(y_test, y_pred, zero_division=0))
