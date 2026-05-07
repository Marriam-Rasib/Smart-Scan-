from xgboost import XGBClassifier
from utils.metrics import evaluate_model


def run_xgboost(X_train, X_test, y_train, y_test):

    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="mlogloss",
        random_state=42
    )

    print("\nTraining XGBoost...")

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    evaluate_model(y_test, y_pred)

    return model
