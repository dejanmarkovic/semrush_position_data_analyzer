import email
import os
import re
from collections import defaultdict

import pandas as pd


def extract_keyword_data(content):
    """Extract keyword data from the content using table data pattern"""
    # Pattern to match table row with keyword, position, difference, and volume
    pattern = r'<td class="cell_keyword"[^>]*>.*?<a[^>]*>\s*(.*?)\s*</a>.*?</td>.*?<td[^>]*>\s*(\d+)\s*</td>.*?<td[^>]*>.*?([+-]?\d+)\s*</span>.*?</td>.*?<td[^>]*>\s*(\d+)?\s*</td>'
    matches = re.findall(pattern, content, re.DOTALL)

    results = []
    for match in matches:
        keyword = match[0].strip()
        if len(keyword) > 3:  # Filter out very short keywords
            try:
                position = int(match[1])
                difference = int(match[2]) if match[2] else None
                volume = int(match[3]) if match[3] and match[3].strip() else None

                results.append(
                    {
                        "keyword": keyword,
                        "position": position,
                        "difference": difference,
                        "volume": volume,
                    }
                )
            except (ValueError, IndexError) as e:
                print(f"Error parsing match {match}: {str(e)}")

    return results


def parse_eml_file(file_path):
    """
    Parse an .eml file and extract keyword position data.
    Returns a list of dictionaries with keyword data
    """
    try:
        # Read the file in binary mode
        with open(file_path, "rb") as file:
            raw_email = file.read()

        # Parse the email content from bytes
        msg = email.message_from_bytes(raw_email)

        # Get email body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            body = payload.decode("utf-8")
                            break
                        except UnicodeDecodeError:
                            try:
                                body = payload.decode("latin1")
                            except UnicodeDecodeError:
                                body = payload.decode("cp1252", errors="ignore")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                try:
                    body = payload.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        body = payload.decode("latin1")
                    except UnicodeDecodeError:
                        body = payload.decode("cp1252", errors="ignore")

        print(f"\nProcessing file: {file_path}")

        # Extract keyword data from the HTML content
        results = extract_keyword_data(body)

        # Add source file to results
        for result in results:
            result["source_file"] = os.path.basename(file_path)

        print(f"Found {len(results)} keywords in {file_path}")
        for result in results:
            print(
                f"Keyword: {result['keyword']}, Position: {result['position']}, Difference: {result['difference']}, Volume: {result['volume']}"
            )

        return results

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []


def analyze_emails(directory_path):
    """
    Analyze all .eml files in the specified directory and generate a report.
    """
    all_results = []

    # Check if directory exists
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")

    # Get list of .eml files
    eml_files = [f for f in os.listdir(directory_path) if f.endswith(".eml")]
    print(f"\nFound {len(eml_files)} .eml files in directory")

    if len(eml_files) == 0:
        raise ValueError(f"No .eml files found in directory: {directory_path}")

    # Process all .eml files
    for filename in eml_files:
        file_path = os.path.join(directory_path, filename)
        results = parse_eml_file(file_path)
        all_results.extend(results)

    if not all_results:
        raise ValueError("No data was extracted from any of the email files")

    # Convert to DataFrame for analysis
    df = pd.DataFrame(all_results)

    print("\nExtracted data summary:")
    print(f"Total records: {len(df)}")
    print("\nSample of extracted data:")
    print(df.head())

    # Generate summary statistics
    summary = {
        "keyword_stats": df.groupby("keyword")
        .agg({"position": ["mean", "min", "max", "count"], "volume": "last"})
        .round(2),
        "total_keywords": len(df["keyword"].unique()),
        "total_records": len(df),
    }

    return df, summary


def generate_report(df, summary):
    """
    Generate a formatted report of the analysis results.
    """
    report = []
    report.append("=== Keyword Position Analysis Report ===\n")

    report.append(f"Total unique keywords analyzed: {summary['total_keywords']}")
    report.append(f"Total records processed: {summary['total_records']}\n")

    report.append("=== Keyword Performance Summary ===")
    for keyword, stats in summary["keyword_stats"].iterrows():
        report.append(f"\nKeyword: {keyword}")
        report.append(f"  Times tracked: {stats['position']['count']}")
        report.append(f"  Average Position: {stats['position']['mean']}")
        report.append(f"  Best Position: {stats['position']['min']}")
        report.append(f"  Worst Position: {stats['position']['max']}")
        if not pd.isna(stats["volume"]["last"]):
            report.append(f"  Latest Volume: {stats['volume']['last']}")

    return "\n".join(report)


def main():
    try:
        # Replace with your Google Drive directory path
        directory_path = "100 emails"

        print(f"Starting analysis of directory: {directory_path}")

        # Analyze emails
        df, summary = analyze_emails(directory_path)

        # Generate and print report
        report = generate_report(df, summary)
        print(report)

        # Save detailed data to CSV
        output_file = "keyword_position_analysis.csv"
        df.to_csv(output_file, index=False)
        print(f"\nDetailed analysis saved to '{output_file}'")

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nPlease check that:")
        print("1. The directory '100 emails' exists in the current working directory")
        print("2. The directory contains .eml files")
        print("3. The email files contain the expected keyword position data")


if __name__ == "__main__":
    main()
