from utils.data_loader import load_all_contracts
from utils.preprocessing import preprocess_contracts
from utils.preprocessing import vectorize_text

from utils.model_utils import save_model
from utils.visualization import plot_class_distribution

from experiments.random_forests import run_random_forest
from experiments.svm import run_svm
from experiments.lr import run_logistic_regression
from experiments.xgboost import run_xgboost


def main():

    files = [
        "data/PolygonContracts1.json",
        "data/PolygonContracts2.json",
        "data/OptimismContracts2.json",
        "data/OptimismContracts1.json",
        "data/new_ether_contract_details_part2.json",
        "data/new_etherscan_contract_details_part1.json",
        
    ]

    print("\nLoading contracts...")
    contracts = load_all_contracts(files)

    source_codes, y, label_encoder, valid_contracts = preprocess_contracts(
        contracts
    )

    print(f"\nValid contracts: {len(valid_contracts)}")
    print(f"Number of classes: {len(label_encoder.classes_)}")
    print("Classes:", list(label_encoder.classes_))

    plot_class_distribution(
        y,
        class_names=label_encoder.classes_
    )

    X, vectorizer = vectorize_text(source_codes)

    print("\nTF-IDF Matrix Shape:", X.shape)

    # =========================
    # RANDOM FOREST
    # =========================
    rf_model = run_random_forest(X, y)
    save_model(rf_model, "models/random_forest.pkl")

    # =========================
    # SVM
    # =========================
    svm_model = run_svm(X, y)
    save_model(svm_model, "models/svm.pkl")

    # =========================
    # LOGISTIC REGRESSION
    # =========================
    lr_model = run_logistic_regression(X, y)
    save_model(lr_model, "models/logistic_regression.pkl")

    # =========================
    # XGBOOST
    # =========================
    xgb_model = run_xgboost(X, y)
    save_model(xgb_model, "models/xgboost.pkl")


if __name__ == "__main__":
    main()
