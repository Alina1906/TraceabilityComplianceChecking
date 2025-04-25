import xml.etree.ElementTree as ET
import html
import json
import argparse

def extract_issue_keys_and_commits(xml_file):
    """Extracts issue keys and commit hashes from a Jira backup XML file."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    results = []

    for entity in root.findall(".//EntityProperty"):
        value_attr = entity.get("value")
        if value_attr:
            decoded_value = html.unescape(value_attr)  # Decode HTML entities
            try:
                json_data = json.loads(decoded_value)  # Parse JSON data

                # Ensure json_data is a dictionary before accessing .get()
                if not isinstance(json_data, dict):
                    continue

                value_field = json_data.get("value")

                # If "value" is a string, try parsing it as JSON
                if isinstance(value_field, str):
                    try:
                        value_field = json.loads(value_field)
                    except json.JSONDecodeError:
                        continue  # Skip if it cannot be parsed

                # Ensure value_field is a dictionary before accessing "targets"
                if not isinstance(value_field, dict):
                    continue

                targets = value_field.get("targets", {})

                for issue_key, target_list in targets.items():
                    commit_hashes = []
                    for target in target_list:
                        if target.get("type", {}).get("id") == "repository":
                            for obj in target.get("objects", []):
                                if obj.get("type") == "git":
                                    commit_hashes.extend(obj.get("commits", []))

                    # If no commits are found, store an empty value
                    if not commit_hashes:
                        commit_hashes.append("")

                    # Store results
                    for commit in commit_hashes:
                        results.append((issue_key, commit))

            except json.JSONDecodeError:
                continue  # Skip malformed JSON

    return results

def main():
    """Parses XML file and saves extracted issue keys and commits to a file."""
    parser = argparse.ArgumentParser(description="Parse Jira XML backup for issue keys and commits.")
    parser.add_argument("xml_file", help="Path to the Jira XML backup file")
    parser.add_argument("output_file", help="Path to save the extracted data")

    args = parser.parse_args()

    parsed_data = extract_issue_keys_and_commits(args.xml_file)

    # Save results to a file
    with open(args.output_file, "w", encoding="utf-8") as f:
        for issue, commit in parsed_data:
            f.write(f"Issue: {issue}, Commit: {commit}\n")

if __name__ == "__main__":
    main()
