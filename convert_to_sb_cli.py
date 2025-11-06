#!/usr/bin/env python3
"""
Convert Agents framework output to SWE-bench CLI format and submit for evaluation.

This script:
1. Reads JSONL predictions from our Agents framework
2. Converts them to SWE-bench CLI format
3. Optionally submits them using sb-cli
"""

import json
import argparse
import subprocess
import sys
from pathlib import Path


def convert_jsonl_to_sb_cli_format(jsonl_file, output_file):
    """
    Convert our JSONL format to SWE-bench CLI dictionary format.
    
    Input format (JSONL):
    {"instance_id": "...", "model_patch": "...", "model_name_or_path": "...", "elapsed_time": 123}
    
    Output format (JSON):
    {"instance_id": {"model_patch": "...", "model_name_or_path": "..."}}
    """
    predictions = {}
    
    with open(jsonl_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            data = json.loads(line)
            instance_id = data['instance_id']
            
            predictions[instance_id] = {
                'model_patch': data.get('model_patch', ''),
                'model_name_or_path': data.get('model_name_or_path', 'real_agents_framework')
            }
    
    with open(output_file, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"✅ Converted {len(predictions)} predictions to {output_file}")
    return len(predictions)


def check_sb_cli_installed():
    """Check if sb-cli is installed."""
    try:
        result = subprocess.run(['sb-cli', '--help'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def submit_to_sb_cli(predictions_file, subset='swe-bench_lite', split='dev', run_id=None):
    """Submit predictions using sb-cli."""
    
    if not check_sb_cli_installed():
        print("❌ sb-cli not installed. Install with: pip install sb-cli")
        print("📖 See: https://www.swebench.com/sb-cli/installation/")
        return False
    
    # Check API key
    import os
    if not os.getenv('SWEBENCH_API_KEY'):
        print("❌ SWEBENCH_API_KEY environment variable not set")
        print("📖 See: https://www.swebench.com/sb-cli/authentication/")
        return False
    
    cmd = [
        'sb-cli', 'submit', subset, split,
        '--predictions_path', str(predictions_file)
    ]
    
    if run_id:
        cmd.extend(['--run_id', run_id])
    
    print(f"🚀 Submitting to SWE-bench CLI: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error submitting: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Convert Agents predictions to SWE-bench CLI format')
    parser.add_argument('input_file', help='Input JSONL file from Agents framework')
    parser.add_argument('--output', '-o', help='Output JSON file (default: input_file.json)')
    parser.add_argument('--submit', action='store_true', help='Submit to SWE-bench CLI after conversion')
    parser.add_argument('--subset', default='swe-bench_lite', choices=['swe-bench-m', 'swe-bench_lite', 'swe-bench_verified'],
                        help='SWE-bench subset (default: swe-bench_lite)')
    parser.add_argument('--split', default='dev', choices=['dev', 'test'], help='Dataset split (default: dev)')
    parser.add_argument('--run-id', help='Custom run ID for submission')
    
    args = parser.parse_args()
    
    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    # Determine output file
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = input_file.with_suffix('.json')
    
    print(f"🔄 Converting {input_file} → {output_file}")
    
    # Convert format
    try:
        num_predictions = convert_jsonl_to_sb_cli_format(input_file, output_file)
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        sys.exit(1)
    
    print(f"📊 Summary:")
    print(f"   Input: {input_file}")
    print(f"   Output: {output_file}")
    print(f"   Predictions: {num_predictions}")
    print(f"   Format: SWE-bench CLI compatible")
    
    # Submit if requested
    if args.submit:
        print(f"\n🚀 Submitting to SWE-bench CLI...")
        success = submit_to_sb_cli(
            output_file, 
            subset=args.subset, 
            split=args.split, 
            run_id=args.run_id
        )
        
        if success:
            print("✅ Submission completed!")
        else:
            print("❌ Submission failed")
            sys.exit(1)
    else:
        print(f"\n💡 To submit manually:")
        print(f"   sb-cli submit {args.subset} {args.split} --predictions_path {output_file}")


if __name__ == '__main__':
    main()