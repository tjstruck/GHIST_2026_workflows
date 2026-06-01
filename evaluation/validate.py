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

def validate_columns(df):
    errors = []
    cols_lower = {c.lower(): c for c in df.columns}

    required = ["indid1", "indid2"]
    missing = [r for r in required if r not in cols_lower]
    if missing:
        errors.append(f"Missing required columns: {[cols_lower.get(m, m) for m in missing]}.")

    optional = ["meioses_count", "relation", "relationship"]
    if not any(o in cols_lower for o in optional):
        errors.append(f"Must have at least one of: {optional}.")
    return errors

def validate_table(filepath, truth):
    """
    Checks for expected colnames in the YAML file.
    """

    errors = []

    # Make sure the user uploaded a file that can be opened and read
    try:
        open(filepath, "r")
    except FileNotFoundError:
        errors = ["File could not be opened"]

    # Make sure there are no errors opening with pandas
    if errors == []:
        exc = 'No error'
        try:
            table = pd.read_csv(filepath, sep=None, engine='python')
        except ValueError as exc:
            errors = [exc]

    if errors == []:
        groundtruth = pd.read_csv(truth, sep=None, engine='python')
        table.columns = table.columns.str.lower()
        groundtruth.columns = groundtruth.columns.str.lower()

        # Check for expected column names (case-insensitive)
        errors = validate_columns(table)

    # Already making sure the submission has the needed columns, not interested in extra columns
    # if errors == []:
    #     # Checking for expected column names (case-insensitive)
    #     for entry in list(table):
    #         entry.lower().strip() in [header.lower().strip() for header in groundtruth.columns] or errors.append(f"Unexpected column name: {entry}")
    #     # for header in groundtruth.columns:
    #     #     header.lower().strip() in [col.lower().strip() for col in list(table)] or errors.append(f"Missing expected column name: {header}")

    if errors == [] and 'relation' in table.columns:
        groundtruth['relation'] = groundtruth['relation'].str.lower()
        groundtruth = groundtruth[groundtruth['relation'] != 'unrelated']
        try:
            table['relation'] = table['relation'].str.lower()
        except:
            pass
        potential_entries = '\n'.join(groundtruth['relation'].unique())
        for ele in table['relation']:
            if ele not in groundtruth['relation'].unique():
                errors.append(f"Unexpected relation value: {ele}. Expected relation of any of the following: " + potential_entries)

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
