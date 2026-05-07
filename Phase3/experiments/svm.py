from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split

from utils.metrics import evaluate_model


def run_svm(X, y):

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = LinearSVC()

    print("\nTraining SVM...")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    evaluate_model(y_test, y_pred)

    return model
