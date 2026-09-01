#!/usr/bin/env python

"""Example validation script.

This is a minimal example of how a prediction file can be checked
for expected structure and format, prior to scoring.

In order to display the results on Synapse, the results must be
written to a JSON file. This JSON file will then be used to annotate
the submission (next step in the workflow CWL).
"""

import argparse, json, yaml
import numpy as np
from dataclasses import dataclass
import warnings

def _read_bed(bedfile):
    """
    Read bedfile into a list of lists [[start1, end1], [start2, end2] ...]
    """
    if bedfile is None:
        warnings.warn(f"No intervals in: {bedfile}. Set intervals manually.")
        intervals = [] 
    else:
        # Load the intervals from the BED file
        intervals = []
        with open(bedfile, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                start = int(parts[1])
                end = int(parts[2])
                intervals.append([start, end])
        if not intervals:
            raise ValueError("No valid intervals found in the BED file. File should have values chrom, start, and stop values. ex: 1 1000 20000")
    return

def validate_bed(filepath):
    """
    Checks for expected colnames in the YAML file.
    """

    if filepath is None:
        invalid_reasons = ['Expected FileEntity type but found ' + args.entity_type]
    else:
        invalid_reasons = []

        try:
            open(filepath, "r")
        except FileNotFoundError:
            invalid_reasons = ["File could not be opened"]

        if invalid_reasons == []:
            exc = 'No error'
            try:
                _read_bed(filepath)
            except ValueError as exc:
                invalid_reasons = [exc]

    return "\n".join(invalid_reasons)

def main():
    """Main function."""

    # if args.entity_type != "FileEntity":
    #     errors = f"Submission should be a file, not {args.entity_type}"
    # else:
    errors = validate_bed(
        args.prediction_file
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
