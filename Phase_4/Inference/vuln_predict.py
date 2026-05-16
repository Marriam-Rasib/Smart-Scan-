import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

# ==========================================
# SWC LABELS + HUMAN READABLE NAMES
# ==========================================
SWC_LABELS = [
    'SWC-101',
    'SWC-104',
    'SWC-107',
    'SWC-113',
    'SWC-114',
    'SWC-115',
    'SWC-116',
    'SWC-128'
]

SWC_NAMES = {
    'SWC-101': 'Integer Overflow / Underflow',
    'SWC-104': 'Unchecked Call Return Value',
    'SWC-107': 'Reentrancy',
    'SWC-113': 'DoS with Failed Call',
    'SWC-114': 'Transaction Order Dependence',
    'SWC-115': 'Authorization through tx.origin',
    'SWC-116': 'Block Timestamp Manipulation',
    'SWC-128': 'DoS With Block Gas Limit'
}

NUM_LABELS = len(SWC_LABELS)

# ==========================================
# MODEL CLASS
# ==========================================
class CodeBERTVulnDetector(nn.Module):

    def __init__(self, num_labels=8):

        super().__init__()

        self.bert = AutoModel.from_pretrained(
            "microsoft/codebert-base"
        )

        self.dropout = nn.Dropout(0.3)

        self.classifier = nn.Linear(768, num_labels)

    def forward(self, input_ids, attention_mask):

        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        pooled = outputs.last_hidden_state[:, 0, :]

        pooled = self.dropout(pooled)

        logits = self.classifier(pooled)

        return logits


# ==========================================
# DEVICE
# ==========================================
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Using device: {device}")

# ==========================================
# TOKENIZER
# ==========================================
tokenizer = AutoTokenizer.from_pretrained(
    "microsoft/codebert-base"
)

# ==========================================
# LOAD TRAINED MODEL
# ==========================================
model = CodeBERTVulnDetector(num_labels=NUM_LABELS)

model.load_state_dict(
    torch.load(
        "/content/Smart-Scan-/Phase_4/models/best_model.pt",
        map_location=device
    )
)

model.to(device)

model.eval()

print("✅ Vulnerability model loaded successfully!")

# ==========================================
# PREDICTION FUNCTION
# ==========================================
def predict_vulnerability(code, threshold=0.3):

    try:

        # ==================================
        # TOKENIZATION
        # ==================================
        encoding = tokenizer(
            code,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        input_ids = encoding["input_ids"].to(device)

        attention_mask = encoding["attention_mask"].to(device)

        # ==================================
        # MODEL PREDICTION
        # ==================================
        with torch.no_grad():

            logits = model(
                input_ids,
                attention_mask
            )

            probs = torch.sigmoid(
                logits
            ).cpu().numpy()[0]

        # ==================================
        # STORE RESULTS
        # ==================================
        all_scores = {}

        detected = []

        for label, prob in zip(SWC_LABELS, probs):

            prob = float(prob)

            # Human readable scores
            readable_label = f"{label} - {SWC_NAMES[label]}"

            all_scores[readable_label] = round(
                prob * 100,
                2
            )

            # Threshold check
            if prob > threshold:

                detected.append(
                    (label, prob)
                )

        # ==================================
        # VULNERABILITIES FOUND
        # ==================================
        if detected:

            detected.sort(
                key=lambda x: x[1],
                reverse=True
            )

            top_label, top_prob = detected[0]

            return {
                "status": "Vulnerable",

                "top_vulnerability":
                    SWC_NAMES[top_label],

                "swc_id":
                    top_label,

                "confidence":
                    round(top_prob * 100, 2),

                "all_scores":
                    all_scores
            }

        # ==================================
        # SAFE CONTRACT
        # ==================================
        return {
            "status": "Safe",

            "top_vulnerability":
                "None",

            "swc_id":
                "N/A",

            "confidence":
                0,

            "all_scores":
                all_scores
        }

    # ======================================
    # ERROR HANDLING
    # ======================================
    except Exception as e:

        print("❌ Vulnerability Prediction Error:", e)

        return {
            "status": "Error",

            "top_vulnerability":
                "Error",

            "swc_id":
                "Error",

            "confidence":
                0,

            "all_scores":
                {}
        }
