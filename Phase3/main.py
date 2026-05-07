from utils.data_loader import load_all_contracts
from utils.preprocessing import preprocess_contracts
from utils.preprocessing import vectorize_text

from utils.model_utils import save_model

from experiments.random_forest import run_random_forest
from experiments.svm_classifier import run_svm
from experiments.logistic_regression import run_logistic_regression


def main():

    files = [

        'data/PolygonContracts1.json',
        'data/PolygonContracts2.json',
        'data/PolygonContracts3.json',
        'data/PolygonContracts4.json'
    ]

    contracts = load_all_contracts(files)

    source_codes, y, label_encoder, valid_contracts = preprocess_contracts(
        contracts
    )

    X, vectorizer = vectorize_text(source_codes)

    print("\nTF-IDF Matrix Shape:", X.shape)

    # =========================
    # RANDOM FOREST
    # =========================

    rf_model = run_random_forest(X, y)

    save_model(rf_model, 'models/random_forest.pkl')

    # =========================
    # SVM
    # =========================

    svm_model = run_svm(X, y)

    save_model(svm_model, 'models/svm.pkl')

    # =========================
    # LOGISTIC REGRESSION
    # =========================

    lr_model = run_logistic_regression(X, y)

    save_model(lr_model, 'models/logistic_regression.pkl')


if __name__ == "__main__":
    main()
