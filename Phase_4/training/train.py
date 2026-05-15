import os
import json
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

import xgboost as xgb
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# CATEGORY KEYWORDS
# =========================

categories_keywords = {

    "NFT": ["erc721", "non-fungible token"],

    "Multi Token": ["erc1155", "multitoken"],

    "Stablecoins": ["stablecoin", "peg", "usd", "collateral", "oracle"],

    "Gaming": ["game", "player", "avatar", "virtual"],

    "Wallet": ["wallet", "withdraw", "deposit"],

    "DeFi": ["liquidity", "stake", "borrow", "lend"],

    "Governance": ["governance", "vote", "proposal"],

    "Bridge": ["cross-chain", "wrapped"],

    "Utility": ["utility", "redeem", "spend"],

    "ERC20 Token": [
        "erc20",
        "totalsupply",
        "balanceof",
        "transfer",
        "approve"
    ]
}

# =========================
# LOAD JSON FILES (ROBUST)
# =========================

def load_data():
    data = []

    for file in os.listdir("dataset"):
        if file.endswith(".json"):
            path = os.path.join("dataset", file)
            print(f"📂 {file}")

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    data.extend(content)

            except:
                print(f"⚠️ Recovering {file}")
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        try:
                            obj = json.loads(line.strip())
                            data.append(obj)
                        except:
                            continue

    print("✅ Total raw samples:", len(data))
    return data

# =========================
# PREPROCESS + LABEL
# =========================

def preprocess(data):

    source_codes = []
    labels = []

    for contract in data:

        code = contract.get("SourceCode") or contract.get("source_code")

        if not code or not isinstance(code, str):
            continue

        code = code.strip()

        if len(code) < 50:
            continue

        code_lower = code.lower()

        category = "Other"

        for cat, keywords in categories_keywords.items():
            if any(k in code_lower for k in keywords):
                category = cat
                break

        source_codes.append(code)
        labels.append(category)

    print("✅ Clean samples:", len(source_codes))

    return source_codes, labels

# =========================
# LOAD + PROCESS
# =========================

raw_data = load_data()
source_codes, labels = preprocess(raw_data)

# =========================
# ENCODE LABELS
# =========================

encoder = LabelEncoder()
y = encoder.fit_transform(labels)

joblib.dump(encoder, "models/category_encoder.pkl")

# =========================
# SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    source_codes,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

# =========================
# TF-IDF
# =========================

vectorizer = TfidfVectorizer(
    max_features=10000,
    stop_words="english",
    min_df=3,
    max_df=0.95
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

joblib.dump(vectorizer, "models/tfidf_vectorizer.pkl")

# =========================
# XGBOOST
# =========================

model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    eval_metric="mlogloss",
    random_state=42
)

print("\n🚀 Training XGBoost...")
model.fit(X_train_vec, y_train)

# =========================
# EVALUATION
# =========================

y_pred = model.predict(X_test_vec)

report = classification_report(y_test, y_pred)
print("\n📊 REPORT:\n", report)

with open("models/report.txt", "w") as f:
    f.write(report)

cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.savefig("models/confusion_matrix.png")

# =========================
# SAVE MODEL
# =========================

joblib.dump(model, "models/xgb_model.pkl")

print("\n✅ TRAINING COMPLETE")
