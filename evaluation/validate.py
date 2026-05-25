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


def validate_table(filepath):
    """
    Checks for expected colnames in the YAML file.
    """

    errors = []
    prediction_file_status = "VALIDATED"
    headers = ["indid1", "indid2", "meioses_count", "relation"]

    try:
        open(filepath, "r")
    except FileNotFoundError:
        errors = ["File could not be opened"]

    if errors == []:
        exc = 'No error'
        try:
            table = pd.read_csv("groundtruth/relatedness2_testing.csv", sep=None, engine='python')
        except ValueError as exc:
            errors = [exc]

    if errors == []:
        try:
            for entry in list(table):
                entry.lower()
        except KeyError:
            errors = ['Could not find one or more parameters, which are required for scoring']

    return "\n".join(errors)

def main():
    """Main function."""

    expected_entries=[
                "generations",
                "post_decline_fraction",
                ]

    # if args.entity_type != "FileEntity":
    #     errors = f"Submission should be a file, not {args.entity_type}"
    # else:
    errors = validate_yaml(
        args.prediction_file,
        expected_entries,
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
        "-o",
        "--output_file",
        default="results.json",
        help="Output JSON file for scores and results",
    )
    args = parser.parse_args()
    main()
