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
import yaml
import numpy as np

def relative_root_mean_squared_error(truth, pred):
    n = len(truth) # update
    squared_error = np.square((truth - pred) / truth)
    rrmse = np.sqrt(np.sum(squared_error))
    return rrmse

def score_demography(truth, pred):
    error = []
    with open(args.submissionfile) as stream:
        try:
            submission = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            error.append(str(exc))

    with open(truth) as stream:
        try:
            groundthruth = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            error.append(str(exc))

    try:
        keys = list(groundthruth['parameters'].keys())
        keys.sort()
        RRMSE = relative_root_mean_squared_error(np.array([groundthruth['parameters'][key] for key in keys]), np.array([submission['parameters'][key] for key in keys]))
    except:
        RRMSE = np.nan
    if error == []:
        error = ""
    return RRMSE, error


def main():
    """Main function."""

    # id_col = "PatientID"
    # pred = read_csv(args.prediction_file, id_col=id_col)
    # if not pred:
    #     scores = 0
    #     status = "INVALID"
    #     errors = f"Cannot be evaluated; {id_col} not found in the prediction file"
    # else:
    #     truth = read_csv(args.groundtruth_file, id_col=id_col)
    #     status = "SCORED"
    #     errors = ""

    try:
        scores, errors = score_demography(args.groundtruth_file, args.prediction_file)
        status = "SCORED"
    except ValueError:
        scores = np.nan
        status = "INVALID"
        errors = "Cannot be evaluated; error encountered during scoring"

    result = {
        "RRMSE": scores,
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
