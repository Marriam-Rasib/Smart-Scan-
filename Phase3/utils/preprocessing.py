from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer


categories_keywords = {

    "NFT": ["erc721", "non-fungible token"],

    "Multi Token": ["erc1155", "multitoken"],

    "Stablecoins": [
        "stablecoin",
        "peg",
        "usd",
        "collateral",
        "oracle"
    ],

    "Gaming/Metaverse": [
        "game",
        "player",
        "metaverse",
        "avatar",
        "virtual"
    ],

    "Wallets": [
        "wallet",
        "withdraw",
        "deposit",
        "transaction"
    ],

    "DEFI": [
        "liquidity",
        "stake",
        "borrow",
        "lend"
    ],

    "Governance Tokens": [
        "governance",
        "vote",
        "proposal",
        "delegate"
    ],

    "Bridge": [
        "cross-chain",
        "wrapped"
    ],

    "Utility Tokens": [
        "utility",
        "access",
        "redeem",
        "spendable"
    ],

    "Other Fungible Token": [
        "erc20",
        "totalsupply",
        "balanceof",
        "transfer",
        "transferfrom",
        "allowance",
        "approve"
    ]
}


def preprocess_contracts(contracts):

    source_codes = []
    labels = []
    valid_contracts = []

    for contract in contracts:

        source_code = contract.get('source_code', '')

        if not isinstance(source_code, str):
            continue

        source_code = source_code.strip()

        if not source_code:
            continue

        source_lower = source_code.lower()

        category = "Uncategorized"

        for cat, keywords in categories_keywords.items():

            if any(keyword in source_lower for keyword in keywords):

                category = cat
                break

        source_codes.append(source_code)
        labels.append(category)
        valid_contracts.append(contract)

    label_encoder = LabelEncoder()

    y = label_encoder.fit_transform(labels)

    return source_codes, y, label_encoder, valid_contracts


def vectorize_text(source_codes):

    vectorizer = TfidfVectorizer(
        max_features=10000,
        stop_words='english',
        min_df=3,
        max_df=0.95
    )

    X = vectorizer.fit_transform(source_codes)

    return X, vectorizer
