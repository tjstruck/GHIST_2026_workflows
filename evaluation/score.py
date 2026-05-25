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

def relative_root_mean_squared_error(truth, pred):
    n = len(truth) # update
    squared_error = np.square((truth - pred) / truth)
    rrmse = np.sqrt(np.sum(squared_error))
    return rrmse

def canonical_pair(row):
    return tuple(sorted([row['indid1'], row['indid2']]))



def score_relation(truth, pred):
    errors = []

    submission = pd.read_csv(pred, sep=None, engine='python')
    groundthruth = pd.read_csv(truth, sep=None, engine='python')

    # Standardize column names to lowercase for merging
    submission.columns = submission.columns.str.lower()
    groundthruth.columns = groundthruth.columns.str.lower()

    # Create a canonical pair key for merging (order of individuals should not matter)
    groundthruth['pair_key'] = groundthruth.apply(canonical_pair, axis=1)
    submission['pair_key'] = submission.apply(canonical_pair, axis=1)

    # Merge submission with groundtruth on the canonical pair key
    merged = submission.merge(
        groundthruth[['pair_key', 'meioses_count']],
        on='pair_key',
        how='left',
        suffixes=('_pred', '_truth')
    )

    # Calculate RRMSE, handling potential issues with missing values or non-numeric data
    try:
        RRMSE = relative_root_mean_squared_error(merged['meioses_count_truth'].to_numpy(), merged['meioses_count_pred'].to_numpy())
    except:
        RRMSE = np.nan
        errors.append("Error calculating RRMSE; check that 'meioses_count' column is present and contains numeric values")

    # Calculate percentage of pairs with correct relation (if relation column is present)
    if 'relation' in submission.columns and 'relation' in groundthruth.columns:
        # Control for case sensitivity and whitespace in relation column before merging
        submission['relation'] = submission['relation'].str.strip().str.lower()
        groundthruth['relation'] = groundthruth['relation'].str.strip().str.lower()

        # Re-merge to include relation column for accuracy calculation
        merged = submission.merge(
            groundthruth[['pair_key', 'relation']],
            on='pair_key',
            how='left',
            suffixes=('_pred', '_truth')
        )
        relation_accuracy = np.mean(merged['relation_pred'] == merged['relation_truth'])
    else:
        relation_accuracy = np.nan

    return RRMSE, relation_accuracy, errors


def main():
    """Main function."""

    try:
        RRMSE, relation_accuracy, errors = score_relation(args.groundtruth_file, args.prediction_file)
        status = "SCORED"
    except ValueError:
        RRMSE = np.nan
        relation_accuracy = np.nan
        status = "INVALID"
        errors = "Cannot be evaluated; error encountered during scoring"

    result = {
        "RRMSE": RRMSE,
        "relation_accuracy": relation_accuracy,
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
