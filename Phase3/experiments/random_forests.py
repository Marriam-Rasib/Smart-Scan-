from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from utils.metrics import evaluate_model


def run_random_forest(X, y):

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=500,
        class_weight='balanced',
        n_jobs=-1,
        random_state=42
    )

    print("\nTraining Random Forest...")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    evaluate_model(y_test, y_pred)

    return model
