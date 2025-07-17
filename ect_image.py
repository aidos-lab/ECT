"""Visualize the Euler Characteristic Transform as an image"""

import argparse

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import gaussian_kde
from scipy.spatial.distance import pdist


def select_thresholds(T, num_thresholds, method="linspace"):
    T = np.sort(T)

    if method == "linspace":
        T = np.linspace(T.min(), T.max(), num_thresholds)
    elif method == "kde":
        kde = gaussian_kde(T)
        samples = kde.resample(num_thresholds, seed=42).flatten()
        samples = np.sort(samples)

        T = np.clip(samples, T.min(), T.max())

    return T


def total_variation(X, axis=None):
    differences = np.abs(np.diff(X, axis=axis))
    tv = np.sum(differences, axis=axis)

    return tv


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("FILE", type=str, help="Input file containing the ECT")
    parser.add_argument(
        "-T",
        "--num-thresholds",
        type=int,
        default=256,
        help="Number of thresholds to select",
    )
    parser.add_argument(
        "-t",
        "--threshold-selection-method",
        type=str,
        choices=["linspace", "kde"],
        default="linspace",
        help="Method for selecting thresholds",
    )
    parser.add_argument(
        "-n",
        "--normalize",
        action="store_true",
        help="If set, normalize filtration values *locally* to [-1, 1]",
    )
    parser.add_argument(
        "-o", "--output", type=str, help="If set, store ECT in a text file"
    )

    args = parser.parse_args()

    df = pd.read_csv(args.FILE, sep=" ", header=None, skip_blank_lines=False)

    df_list = np.split(df, df[df.isna().all(1)].index)

    T = []

    # Skip empty/invalid frames but only if they exclusively consist
    # of NaN values. This looks clunky...
    df_list = [df for df in df_list if not df.isna().all().all()]

    # Remove the remaining NaN values, if any.
    df_list = [df.dropna() for df in df_list]

    for df in df_list:
        if args.normalize:
            t_values = df.iloc[:, 0]
            t_min = t_values.min()
            t_max = t_values.max()
            t_values = 2 * (t_values - t_min) / (t_max - t_min) - 1

            df.iloc[:, 0] = t_values

        T.extend(df.iloc[:, 0])

    T = select_thresholds(
        T, args.num_thresholds, method=args.threshold_selection_method
    )

    print(f"Range: [{T.min():.4f}, {T.max():.4f}]")

    X = []

    for df in df_list:
        df = df.set_index(df.columns[0])
        df = df[~df.index.duplicated(keep="first")]
        df = df.reindex(T, method="nearest")

        X.append(df.to_numpy())

    X = np.hstack(X)
    tv = total_variation(X, axis=0)
    average_distance = pdist(X.T, metric="cityblock").mean()

    print(f"Total variation per column: {tv}")
    print(f"Average column distance: {average_distance:.04f}")

    if args.output is not None:
        np.savetxt(args.output, X, fmt="%.4f")

    plt.rcParams.update(
        {
            "text.usetex": True,
            "font.family": "ITC Giovanni Std",
            "font.size": 20,
        }
    )

    g = sns.heatmap(
        X,
        square=True,
        cmap="cividis",
        xticklabels=False,
        yticklabels=False,
        cbar=False,
    )

    g.set(
        xlabel="Direction $w$",
        ylabel="Filtration value $t$",
        title=f"ECT ({args.threshold_selection_method})",
    )

    plt.tight_layout()
    plt.savefig("/tmp/Heatmap.pdf", bbox_inches="tight", pad_inches=0, dpi=300)

    plt.show()
