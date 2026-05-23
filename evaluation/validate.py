#!/usr/bin/env python

"""Example validation script.

This is a minimal example of how a prediction file can be checked
for expected structure and format, prior to scoring.

In order to display the results on Synapse, the results must be
written to a JSON file. This JSON file will then be used to annotate
the submission (next step in the workflow CWL).
"""

import argparse, json, yaml

# if args.submission_file is None:
#     prediction_file_status = "INVALID"
#     invalid_reasons = ['Expected FileEntity type but found ' + args.entity_type]
# else:
#     invalid_reasons = []
#     prediction_file_status = "VALIDATED"

#     try:
#         open(args.submission_file, "r")
#     except FileNotFoundError:
#         invalid_reasons = ["File could not be opened"]

#     if invalid_reasons == []:
#         exc = 'No error'
#         with open(args.submission_file) as stream:
#             try:
#                 fi = yaml.safe_load(stream)
#             except yaml.YAMLError as exc:
#                 invalid_reasons = [exc]

#     if invalid_reasons == []:
#         try:
#             fi['parameters']['generations']
#             fi['parameters']['post_decline_fraction']
#         except KeyError:
#             invalid_reasons = ['Could not find one or more parameters, which are required for scoring']

#     if invalid_reasons != []:
#         prediction_file_status = "INVALID"
# result = {'submission_errors': "\n".join(invalid_reasons),
#         'submission_status': prediction_file_status}
# with open(args.results, 'w') as o:
#     o.write(json.dumps(result))





def validate_yaml(filepath, expected_entries=["id"]):
    """
    Checks for expected colnames in the YAML file.
    """

    errors = []
    prediction_file_status = "VALIDATED"

    try:
        open(filepath, "r")
    except FileNotFoundError:
        errors = ["File could not be opened"]

    if errors == []:
        exc = 'No error'
        with open(filepath) as stream:
            try:
                fi = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                errors = [exc]

    if errors == []:
        try:
            for entry in expected_entries:
                fi['parameters'][entry]
        except KeyError:
            errors = ['Could not find one or more parameters, which are required for scoring']

    # if errors != []:
    #     prediction_file_status = "INVALID"

    # result = {'submission_errors': "\n".join(errors),
    #         'submission_status': prediction_file_status}
    # with open(args.results, 'w') as o:
    #     o.write(json.dumps(result))

    # Example from Synapse validation script template:
    # errors = []
    # with open(filepath) as yamlfile:
    #     data = yaml.safe_load(yamlfile)
    #     for colname in expected_entries:
    #         if colname not in reader.fieldnames:
    #             errors.append(f"'{colname}' is missing from the prediction file")
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
