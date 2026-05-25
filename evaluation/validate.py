#!/usr/bin/env python

"""Example validation script.

This is a minimal example of how a prediction file can be checked
for expected structure and format, prior to scoring.

In order to display the results on Synapse, the results must be
written to a JSON file. This JSON file will then be used to annotate
the submission (next step in the workflow CWL).
"""

import argparse, json
import pandas as pd


def validate_table(filepath, truth):
    """
    Checks for expected colnames in the YAML file.
    """

    errors = []

    try:
        open(filepath, "r")
    except FileNotFoundError:
        errors = ["File could not be opened"]

    if errors == []:
        exc = 'No error'
        try:
            table = pd.read_csv(filepath, sep=None, engine='python')
        except ValueError as exc:
            errors = [exc]

    # Check for expected column number so we know if they are including the "relation" column or not, 
    # which is optional for scoring but may be included in the submission file
    if len(table.columns) < 3:
        headers = ["indID1", "indID2", "meioses_count"]
    elif len(table.columns) == 4:
        headers = ["indID1", "indID2", "meioses_count", "relation"]
    else:
        errors.append(f"Unexpected number of columns: {len(table.columns)}. Expected 3 or 4 columns (indID1, indID2, meioses_count, and optional relation column).")

    if errors == []:
        # Checking for expected column names (case-insensitive)
        for entry in list(table):
            entry.lower() in headers or errors.append(f"Unexpected column name: {entry}")
        for header in headers:
            header in [col.lower() for col in list(table)] or errors.append(f"Missing expected column name: {header}")

        # Check that the number of rows in the submission matches the number of rows in the groundtruth
        groundthruth = pd.read_csv(truth, sep=None, engine='python')
        if len(groundthruth) == len(table):
            pass
        else:
            errors.append(f"Number of rows in submission ({len(table)}) does not match number of rows in groundtruth ({len(groundthruth)}). \
                        \nMake sure to include unrelated individuals in the submission file.")

    return "\n".join(errors)

def main():
    """Main function."""

    errors = validate_table(
        args.prediction_file,
        args.groundtruth_file
    )

    result = {
        "submission_status": "INVALID" if errors else "VALIDATED",
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
        help="Filepath to prediction YAML",
    )
    parser.add_argument(
        "-e",
        "--entity_type",
        default="FileEntity",
        help="Submission type, based on Synapse entities",
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
