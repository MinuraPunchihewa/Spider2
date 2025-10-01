#!/usr/bin/env python3
"""
Script to extract and combine data from Spider2 benchmark datasets:
1. Questions from the benchmark JSONL file
2. SQL queries from evaluation_suite/gold/sql/ folder
3. Execution results from evaluation_suite/gold/exec_result/ folder

Usage:
    python extract_benchmark_data.py <benchmark_name>
    
Examples:
    python extract_benchmark_data.py spider2-lite
    python extract_benchmark_data.py spider2-snow
    python extract_benchmark_data.py spider2-dbt

Output: Combined CSV file with question, sql_query, and execution_result columns
        saved in the benchmark's evaluation suite folder
"""

import json
import csv
import os
import glob
import argparse
import sys
from pathlib import Path
import pandas as pd


def read_jsonl(file_path):
    """Read JSONL file and return list of dictionaries"""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line.strip()))
    except FileNotFoundError:
        print(f"Error: JSONL file not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading JSONL file {file_path}: {e}")
        return []
    return data


def read_sql_file(file_path):
    """Read SQL file and return its content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Warning: Error reading SQL file {file_path}: {e}")
        return None


def read_csv_result(file_path):
    """Read CSV result file and return its content as string"""
    try:
        df = pd.read_csv(file_path)
        # Convert DataFrame to string representation
        return df.to_string(index=False)
    except FileNotFoundError:
        return None
    except Exception as e:
        # Fallback to reading as plain text if pandas fails
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except:
            print(f"Warning: Error reading result file {file_path}: {e}")
            return None


def find_execution_result_files(exec_result_dir, instance_id):
    """Find all execution result files for a given instance_id"""
    pattern = os.path.join(exec_result_dir, f"{instance_id}*.csv")
    result_files = glob.glob(pattern)
    
    results = {}
    for file_path in result_files:
        filename = os.path.basename(file_path)
        # Extract suffix (e.g., 'a', 'b', etc.) if it exists
        if filename == f"{instance_id}.csv":
            suffix = "main"
        else:
            # Extract suffix between instance_id and .csv
            suffix = filename[len(instance_id):].replace('.csv', '').lstrip('_')
        
        content = read_csv_result(file_path)
        if content is not None:
            results[suffix] = content
    
    return results


def get_benchmark_field_mapping(benchmark_name):
    """Get field mapping for different benchmarks"""
    mappings = {
        'spider2-lite': {
            'question_field': 'question',
        },
        'spider2-snow': {
            'question_field': 'instruction',
        },
        'spider2-dbt': {
            'question_field': 'question',
        }
    }
    
    return mappings.get(benchmark_name, {
        'question_field': 'question',  # default
    })


def get_benchmark_paths(benchmark_name, repo_root):
    """Get file paths for a specific benchmark"""
    benchmark_dir = repo_root / benchmark_name
    
    # Try different possible JSONL file names
    possible_jsonl_files = [
        benchmark_dir / f"{benchmark_name}.jsonl",
        benchmark_dir / "examples" / f"{benchmark_name}.jsonl",
    ]
    
    jsonl_file = None
    for possible_file in possible_jsonl_files:
        if possible_file.exists():
            jsonl_file = possible_file
            break
    
    if jsonl_file is None:
        print(f"Error: Could not find JSONL file for benchmark '{benchmark_name}'")
        print(f"Looked for files: {[str(f) for f in possible_jsonl_files]}")
        return None, None, None, None
    
    sql_dir = benchmark_dir / "evaluation_suite" / "gold" / "sql"
    exec_result_dir = benchmark_dir / "evaluation_suite" / "gold" / "exec_result"
    output_dir = benchmark_dir / "evaluation_suite" / "gold"
    
    return jsonl_file, sql_dir, exec_result_dir, output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Extract and combine data from Spider2 benchmark datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_benchmark_data.py spider2-lite
  python extract_benchmark_data.py spider2-snow
  python extract_benchmark_data.py spider2-dbt
  
  # Custom field name
  python extract_benchmark_data.py my-benchmark --question-field instruction
        """
    )
    parser.add_argument(
        'benchmark', 
        help='Name of the benchmark to process (e.g., spider2-lite, spider2-snow, spider2-dbt)'
    )
    parser.add_argument(
        '--output-name',
        help='Custom output filename (without extension)',
        default=None
    )
    parser.add_argument(
        '--question-field',
        help='Field name containing the question/instruction (auto-detected if not specified)',
        default=None
    )
    
    args = parser.parse_args()
    benchmark_name = args.benchmark
    
    # Get repository root (assuming script is in scripts/ folder)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    print(f"Repository root: {repo_root}")
    print(f"Processing benchmark: {benchmark_name}")
    
    # Get field mappings (auto-detect or use provided values)
    if args.question_field:
        field_mapping = {
            'question_field': args.question_field,
        }
        print(f"Using custom field mapping: question='{args.question_field}'")
    else:
        field_mapping = get_benchmark_field_mapping(benchmark_name)
        print(f"Auto-detected field mapping: question='{field_mapping['question_field']}'")
    
    # Get benchmark-specific paths
    jsonl_file, sql_dir, exec_result_dir, output_dir = get_benchmark_paths(benchmark_name, repo_root)
    
    if jsonl_file is None:
        sys.exit(1)
    
    # Check if required directories exist
    if not sql_dir.exists():
        print(f"Warning: SQL directory not found: {sql_dir}")
    if not exec_result_dir.exists():
        print(f"Warning: Execution result directory not found: {exec_result_dir}")
    if not output_dir.exists():
        print(f"Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set output filename
    if args.output_name:
        output_filename = f"{args.output_name}.csv"
    else:
        output_filename = f"{benchmark_name}_combined_data.csv"
    
    output_file = output_dir / output_filename
    
    print(f"Input JSONL file: {jsonl_file}")
    print(f"SQL files directory: {sql_dir}")
    print(f"Execution results directory: {exec_result_dir}")
    print(f"Output file: {output_file}")
    
    # Read JSONL data
    questions_data = read_jsonl(jsonl_file)
    if not questions_data:
        print("Error: No data found in JSONL file or file is empty")
        sys.exit(1)
    
    print(f"Found {len(questions_data)} questions in JSONL file")
    
    # Prepare combined data
    combined_data = []
    missing_sql = 0
    missing_exec = 0
    
    for item in questions_data:
        instance_id = item.get('instance_id', '')
        if not instance_id:
            print(f"Warning: Item missing instance_id: {item}")
            continue
        
        # Read SQL file
        sql_file_path = sql_dir / f"{instance_id}.sql"
        sql_query = read_sql_file(sql_file_path)
        
        if sql_query is None:
            missing_sql += 1
            if missing_sql <= 10:  # Only show first 10 warnings
                print(f"Warning: SQL file not found for {instance_id}")
            elif missing_sql == 11:
                print("... (suppressing further SQL file warnings)")
        
        # Find execution result files
        exec_results = find_execution_result_files(exec_result_dir, instance_id)
        
        if not exec_results:
            missing_exec += 1
            if missing_exec <= 10:  # Only show first 10 warnings
                print(f"Warning: No execution result files found for {instance_id}")
            elif missing_exec == 11:
                print("... (suppressing further execution result warnings)")
        
        # Create base row with only essential fields
        base_row = {
            'Question': item.get(field_mapping['question_field'], ''),
            'SQL Query': sql_query or '',
        }
        
        # If there are multiple execution results, create separate rows
        if exec_results:
            for _, result_content in exec_results.items():
                row = base_row.copy()
                row['Expected Answer'] = result_content
                combined_data.append(row)
        else:
            # Always include the question even if no execution result found
            row = base_row.copy()
            row['Expected Answer'] = ''
            combined_data.append(row)
    
    print(f"\nSummary:")
    print(f"Total questions processed: {len(questions_data)}")
    print(f"Questions with SQL queries: {len(questions_data) - missing_sql}")
    print(f"Questions with execution results: {len(questions_data) - missing_exec}")
    print(f"Total rows in output: {len(combined_data)} (all questions included)")
    
    # Write to CSV
    if combined_data:
        fieldnames = ['Question', 'SQL Query', 'Expected Answer']
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(combined_data)
            
            print(f"\n✅ Data successfully written to: {output_file}")
            
            # Show file size
            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"📊 Output file size: {file_size_mb:.1f} MB")
            
        except Exception as e:
            print(f"Error writing to output file: {e}")
            sys.exit(1)
    else:
        print("No data to write!")
        sys.exit(1)


if __name__ == "__main__":
    main()