%%writefile /content/Smart-Scan-/Phase_4/inference/vuln_predict.py

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

# ==========================================
# LABELS
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

# ==========================================
# TOKENIZER
# ==========================================
tokenizer = AutoTokenizer.from_pretrained(
    "microsoft/codebert-base"
)

# ==========================================
# MODEL LOAD
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

print("✅ Vulnerability model loaded!")


# ==========================================
# PREDICTION FUNCTION
# ==========================================
def predict_vulnerability(code, threshold=0.3):

    try:

        encoding = tokenizer(
            code,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        input_ids = encoding["input_ids"].to(device)

        attention_mask = encoding["attention_mask"].to(device)

        with torch.no_grad():

            logits = model(
                input_ids,
                attention_mask
            )

            probs = torch.sigmoid(
                logits
            ).cpu().numpy()[0]

        all_scores = {}

        detected = []

        for label, prob in zip(SWC_LABELS, probs):

            prob = float(prob)

            all_scores[label] = round(prob * 100, 2)

            if prob > threshold:

                detected.append((label, prob))

        if detected:

            detected.sort(
                key=lambda x: x[1],
                reverse=True
            )

            top_label, top_prob = detected[0]

            return {
                "status": "Vulnerable",
                "top_vulnerability": top_label,
                "confidence": round(top_prob * 100, 2),
                "all_scores": all_scores
            }

        return {
            "status": "Safe",
            "top_vulnerability": "None",
            "confidence": 0,
            "all_scores": all_scores
        }

    except Exception as e:

        print("❌ Vulnerability Prediction Error:", e)

        return {
            "status": "Error",
            "top_vulnerability": "Error",
            "confidence": 0,
            "all_scores": {}
        }
