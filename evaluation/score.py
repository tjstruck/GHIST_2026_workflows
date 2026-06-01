#!/usr/bin/env python

"""Example scoring script.

This is a minimal example of how a prediction file can be evaluated
using built-in Python functions. In this example, "accuracy" is
computed.

In order to display the scores (and other results) on Synapse, they
must be written to a JSON file. This JSON file will then be used to
annotate the submission (next step in the workflow CWL).
"""

import argparse
import json
import numpy as np
import pandas as pd

def jaccard_index(merged, column_prefix):
    classes = list(merged[f'{column_prefix}_truth'].unique())
    jaccard_k = []
    N_k = []
    # Itterate over each class and calculate TP, FP, FN for that class
    for cls in classes:
        # Calculate Jaccard index for predictions
        TP_k = np.sum((merged[f'{column_prefix}_pred'] == cls) & (merged[f'{column_prefix}_truth'] == cls))
        FP_k = np.sum((merged[f'{column_prefix}_pred'] == cls) & (merged[f'{column_prefix}_truth'] != cls))
        FN_k = np.sum((merged[f'{column_prefix}_pred'] != cls) & (merged[f'{column_prefix}_truth'] == cls))

        jaccard_k.append(TP_k / (TP_k + FP_k + FN_k) if (TP_k + FP_k + FN_k) > 0 else str(np.nan))
        N_k.append(TP_k + FN_k)


    jaccard_weighted = 1 / np.sum(N_k) * np.sum(np.array(N_k) * np.array(jaccard_k))
    return jaccard_weighted

def canonical_pair(row):
    return tuple(sorted([row['indid1'], row['indid2']]))

def score_relation(truth, pred):
    errors = []

    # Load submission and groundtruth files with pandas, handling potential issues with file format or encoding
    submission = pd.read_csv(pred, sep=None, engine='python')
    groundtruth = pd.read_csv(truth, sep=None, engine='python')

    # Standardize column names to lowercase for merging
    submission.columns = submission.columns.str.lower()
    groundtruth.columns = groundtruth.columns.str.lower()

    # Normalize relation column to lowercase
    groundtruth['relation'] = groundtruth['relation'].str.lower()
    try:
        submission['relation'] = submission['relation'].str.lower()
    except:
        pass  # If 'relation' column is not present in submission, skip this step

    # Exclude unrelated pairs from scoring
    groundtruth = groundtruth[groundtruth['relation'] != 'unrelated']

    # Create a canonical pair key for merging (order of individuals should not matter)
    groundtruth['pair_key'] = groundtruth.apply(canonical_pair, axis=1)
    submission['pair_key'] = submission.apply(canonical_pair, axis=1)

    # Merge submission with groundtruth on the canonical pair key
    merged = submission.merge(
        groundtruth[['pair_key', 'meioses_count', 'relation']],
        on='pair_key',
        how='right',
        suffixes=('_pred', '_truth')
    )

    # Calculate Jaccard index, handling potential issues with missing values or non-numeric data
    J = {}
    for column in ['meioses_count', 'relation']:
        try:
            J[column] = jaccard_index(merged, column)
        except:
            J[column] = str(np.nan)

    # if all(v == str(np.nan) for v in J.values()):
    #     errors.append("Unable to score.")

    return J, '\n'.join(errors)


def main():
    """Main function."""

    try:
        jaccard_index, errors = score_relation(args.groundtruth_file, args.prediction_file)
        if errors:
            status = "INVALID"
        else:
            status = "SCORED"
    except:
        jaccard_index["meioses_count"] = str(np.nan)
        jaccard_index["relation"] = str(np.nan)
        status = "INVALID"
        errors = "Cannot be evaluated; error encountered during scoring"

    result = {
        "meioses_count": jaccard_index["meioses_count"],
        "relation": jaccard_index["relation"],
        "submission_status": status,
        "submission_errors": errors,
    }
    with open(args.output_file, "w") as o:
        o.write(json.dumps(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--prediction_file",
        required=True,
        help="Filepath to prediction CSV",
    )
    parser.add_argument(
        "-g",
        "--groundtruth_file",
        required=True,
        help="Filepath to groundtruth/goldstandard CSV",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        default="results.json",
        help="Output JSON file for scores and results",
    )
    args = parser.parse_args()
    main()
