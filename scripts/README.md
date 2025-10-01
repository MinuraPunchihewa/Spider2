# Spider2 Benchmark Data Extraction Scripts

This directory contains utility scripts for extracting and processing Spider2 benchmark datasets.

## Scripts

### `extract_benchmark_data.py`

Extracts and combines data from Spider2 benchmark datasets into a single CSV file.

**Features:**
- Combines questions, SQL queries, and execution results
- Supports multiple Spider2 benchmarks (spider2-lite, spider2-snow, spider2-dbt)
- Auto-detects field names for different benchmark types
- Supports custom field name mapping via command line arguments
- Uses relative paths for repository portability
- Handles multiple execution result files per instance
- Saves output in the appropriate benchmark's evaluation suite folder

**Usage:**
```bash
# Extract spider2-lite data
python scripts/extract_benchmark_data.py spider2-lite

# Extract spider2-snow data
python scripts/extract_benchmark_data.py spider2-snow

# Extract spider2-dbt data
python scripts/extract_benchmark_data.py spider2-dbt

# Custom output filename
python scripts/extract_benchmark_data.py spider2-lite --output-name my_custom_output

# Custom field names (for non-standard benchmarks)
python scripts/extract_benchmark_data.py my-benchmark --question-field instruction --db-field database_type
```

**Output:**
- Default location: `{benchmark}/evaluation_suite/gold/{benchmark}_combined_data.csv`
- Custom location: `{benchmark}/evaluation_suite/gold/{custom_name}.csv`

**Field Mapping:**
The script automatically detects field names based on benchmark type:
- `spider2-lite`: uses `question` and `db` fields
- `spider2-snow`: uses `instruction` and `db_id` fields  
- `spider2-dbt`: uses `instruction` and `type` fields

You can override auto-detection with `--question-field` and `--db-field` arguments.

**Output CSV Structure:**
- `question`: The natural language question or instruction
- `sql_query`: The SQL query that answers the question (empty if not available)
- `execution_result`: The execution result of the SQL query (empty if not available)

Note: All questions are included in the output, even if they don't have corresponding SQL queries or execution results.

**Requirements:**
- Python 3.6+
- pandas
- Standard library modules (json, csv, os, glob, argparse, pathlib)

## Installation

No additional installation required beyond Python and pandas:

```bash
pip install pandas
```

## Examples

### Running from repository root:
```bash
cd /path/to/Spider2
python scripts/extract_benchmark_data.py spider2-lite
```

### Output example:
```
Repository root: /path/to/Spider2
Processing benchmark: spider2-lite
Input JSONL file: /path/to/Spider2/spider2-lite/spider2-lite.jsonl
SQL files directory: /path/to/Spider2/spider2-lite/evaluation_suite/gold/sql
Execution results directory: /path/to/Spider2/spider2-lite/evaluation_suite/gold/exec_result
Output file: /path/to/Spider2/spider2-lite/evaluation_suite/gold/spider2-lite_combined_data.csv

Found 547 questions in JSONL file
Summary:
Total questions processed: 547
Missing SQL files: 297
Missing execution results: 0
Total combined rows created: 631

✅ Data successfully written to: /path/to/Spider2/spider2-lite/evaluation_suite/gold/spider2-lite_combined_data.csv
📊 Output file size: 70.5 MB
```