# semrush_position_data_analyzer
# SEMrush Position Data AnalyzerSEMRUSH Position Data Analyzer

This Python script is designed to analyze SEO (Search Engine Optimization) keyword position data from SEMrush reports that have been saved as email files (.eml format). The code processes multiple email reports, extracting information about keyword rankings, position changes, and search volumes from HTML tables embedded within these emails. It's particularly useful for tracking keyword performance over time across multiple reports.

The script's workflow begins by reading .eml files from a specified directory, parsing their HTML content using regular expressions to extract structured data about keywords and their metrics. 
It then aggregates this information into a pandas DataFrame for analysis, generating comprehensive statistics about keyword performance including average positions, position changes, and search volumes. 

The final output includes both a human-readable report summarizing the findings and a detailed CSV file containing all extracted data. The code includes robust error handling for file operations, content parsing, and data validation, making it resilient to common issues like different character encodings or malformed HTML content. 

This tool would be particularly valuable for SEO professionals who need to analyze historical keyword ranking data from SEMrush reports in bulk.

I'll start by analyzing the imports and then break down each function in detail. Let's do this step by step.

First, let's analyze the imports:

The code uses both standard Python libraries and external dependencies:

```python
import email
import os
import re
from collections import defaultdict
import pandas as pd
```

**Email module** is a built-in Python library used for parsing email messages, specifically handling .eml files in this case. It provides tools for parsing email headers, bodies, and attachments in various formats.

**The os module **provides operating system dependent functionality, particularly for file and directory operations like path manipulation and file existence checks. 

**The re module** provides support for regular expressions in Python, which is used here for pattern matching and extracting data from HTML content.

**Collections.defaultdict** is a dictionary subclass that automatically handles missing keys based on a factory function - though interestingly, while imported, it's not used in the current code. 

Finally,** pandas** (imported as pd) is an external library that provides powerful data manipulation and analysis tools, particularly through its DataFrame structure.

I'll analyze each function in detail.

1. `extract_keyword_data(content)`:
This function is responsible for parsing HTML content to extract keyword-related data. It uses a complex regular expression pattern to match and extract information from HTML table cells. The regular expression `pattern` looks for specific HTML structures containing keyword data, positions, differences, and volumes. For each matched row, it creates a dictionary with cleaned and validated data. The function includes error handling for value conversion and implements a basic filter to exclude keywords shorter than 3 characters. The results are returned as a list of dictionaries, each containing "keyword", "position", "difference", and "volume" keys. Important implementation detail: it uses regex groups to capture specific data points within HTML td elements.

2. `parse_eml_file(file_path)`:
This function handles the parsing of individual .eml files. It employs a robust approach to email parsing with multiple encoding fallbacks (utf-8, latin1, cp1252). The function first reads the file in binary mode and uses the email module to parse the raw content. It's designed to handle both multipart and single-part email messages, specifically looking for HTML content. The function implements comprehensive error handling for file operations and content decoding. After extracting the email body, it calls extract_keyword_data() to process the content and adds the source filename to each result record. It provides detailed logging of its operations through print statements.

3. `analyze_emails(directory_path)`:
This function serves as the orchestrator for processing multiple email files. It first validates the directory existence and checks for .eml files. The function aggregates results from all processed files into a single dataset. 

It converts the collected data into a pandas DataFrame for analysis and generates summary statistics. The summary includes grouping by keywords to calculate mean, min, max positions, and count of occurrences. The function returns both the raw DataFrame and a summary dictionary containing aggregated statistics. 

Error handling is implemented for cases where no files are found or no data could be extracted.

4. `generate_report(df, summary)`:
This function takes the analyzed data and creates a human-readable report. It formats the summary statistics into a structured text output, including total counts and detailed statistics for each keyword. 

The report includes metrics like tracking frequency, average position, best and worst positions, and search volume when available. The function uses string formatting to create a hierarchical report structure, with clear section headers and indented details for each keyword.

5. `main()`:
The main function serves as the entry point and coordinator of the entire process. It sets up the execution environment, calls the analysis functions, and handles output generation. 

It includes error handling with user-friendly error messages and setup verification steps. 

The function also saves the detailed analysis to a CSV file for further processing. Important implementation detail: it hardcodes the directory path to "100 emails" and the output filename to "keyword_position_analysis.csv".

