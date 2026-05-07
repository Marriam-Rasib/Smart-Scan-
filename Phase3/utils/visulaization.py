import os
import matplotlib.pyplot as plt
import pandas as pd


def plot_class_distribution(y, save_path="outputs/figures/class_distribution.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    counts = pd.Series(y).value_counts().sort_index()

    plt.figure(figsize=(8, 5))
    bars = plt.bar(counts.index.astype(str), counts.values)

    plt.title("Dataset Class Distribution", fontsize=14)
    plt.xlabel("Class")
    plt.ylabel("Number of Samples")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()
