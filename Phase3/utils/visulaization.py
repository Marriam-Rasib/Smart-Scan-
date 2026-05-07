import os
import matplotlib.pyplot as plt
import pandas as pd


def plot_class_distribution(
    y,
    class_names=None,
    save_path="outputs/figures/class_distribution.png"
):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    counts = pd.Series(y).value_counts().sort_index()

    if class_names is None:
        labels = counts.index.astype(str)
    else:
        labels = [class_names[i] for i in counts.index]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(labels, counts.values)

    plt.title("Contract Category Distribution", fontsize=14)
    plt.xlabel("Category")
    plt.ylabel("Number of Contracts")
    plt.xticks(rotation=25)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            str(int(height)),
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.show()
