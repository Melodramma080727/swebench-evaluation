#!/usr/bin/env python3
"""
Generate predictions using Agents framework for SWE-bench evaluation.
This script is called by the GitHub Actions workflow.
"""

import json
import subprocess
import tempfile
import time
import os
import sys
from datetime import datetime
from pathlib import Path
from datasets import load_dataset


def create_agent_task(instance):
    """Create task for the agent."""
    return instance['problem_statement'] + """

IMPORTANT: 
1. If issue needs fixing: Create solution.patch with git diff output
2. If issue is already resolved: Create COMPLETELY EMPTY solution.patch file (0 bytes, no content, no comments)
3. Always end with: PATCH_FILE: /workspace/solution.patch"""


def extract_patch_from_workspace(workspace_dir, agent_output):
    """Extract patch from workspace directory and agent output."""
    workspace_dir = Path(workspace_dir)
    agents_dir = workspace_dir.parent
    
    # Method 1: Agent-declared patch file
    if 'PATCH_FILE:' in agent_output:
        for line in agent_output.split('\n'):
            if 'PATCH_FILE:' in line:
                file_path = line.split('PATCH_FILE:')[1].strip()
                if file_path.startswith('/workspace/'):
                    host_path = agents_dir / 'workspace' / file_path[11:]
                    if host_path.exists():
                        content = host_path.read_text()
                        content_stripped = content.strip()
                        
                        if not content_stripped:
                            print(f'✅ Found empty patch file (issue already resolved): {host_path}')
                            return ''
                        
                        has_diff_content = any(
                            line.startswith(('diff --git', '@@', '---', '+++', '+', '-')) 
                            for line in content_stripped.split('\n')
                            if line.strip() and not line.strip().startswith('#')
                        )
                        
                        if has_diff_content:
                            print(f'✅ Found agent-declared patch at: {host_path}')
                            return content.strip()
                        else:
                            print(f'✅ Found documentation-only file, treating as empty patch: {host_path}')
                            return ''
    
    # Method 2: Look for solution.patch in multiple locations
    possible_locations = [
        workspace_dir / 'solution.patch',
        agents_dir / 'workspace' / 'solution.patch',  
        agents_dir / 'workspace' / 'projects' / 'solution.patch',
        agents_dir / 'solution.patch',
    ]
    
    for location in possible_locations:
        if location.exists():
            content = location.read_text()
            content_stripped = content.strip()
            
            if not content_stripped:
                print(f'✅ Found empty patch file (issue already resolved): {location}')
                return ''
            
            has_diff_content = any(
                line.startswith(('diff --git', '@@', '---', '+++', '+', '-')) 
                for line in content_stripped.split('\n')
                if line.strip() and not line.strip().startswith('#')
            )
            
            if has_diff_content:
                print(f'✅ Found valid patch at: {location}')
                return content.strip()
            else:
                print(f'✅ Found documentation-only file, treating as empty patch: {location}')
                return ''
    
    # Method 3: Extract from agent output
    if 'diff --git' in agent_output:
        lines = agent_output.split('\n')
        patch_lines = []
        in_patch = False
        
        for line in lines:
            if line.startswith('diff --git'):
                in_patch = True
            if in_patch:
                patch_lines.append(line)
                if line.strip() in ['```', '---END---', 'Task completed']:
                    break
        
        if patch_lines:
            return '\n'.join(patch_lines).strip()
    
    return None


def run_agent_on_task(instance, instance_idx, total):
    """Run the Agents framework on a single SWE-bench task."""
    instance_id = instance['instance_id']
    print(f'\n[{instance_idx}/{total}] Processing {instance_id}')
    
    start_time = time.time()
    
    try:
        # Clone Agents repository
        agents_dir = Path('/tmp/agents')
        if agents_dir.exists():
            subprocess.run(['rm', '-rf', str(agents_dir)], check=True)
        
        subprocess.run(['git', 'clone', os.getenv('AGENTS_REPO'), str(agents_dir)], check=True)
        
        # Create task
        task = create_agent_task(instance)
        
        # Run agent
        cmd = [
            'docker', 'run', '--rm',
            '-v', f'{agents_dir}/workspace:/workspace',
            '-e', f'ANTHROPIC_API_KEY={os.getenv("ANTHROPIC_API_KEY")}',
            '-w', '/workspace',
            'agents-framework',
            'python', '-m', 'openhands.core.cli',
            '--task', task,
            '--agent', 'CodeActAgent',
            '--llm-model', os.getenv('MODEL_NAME'),
            '--max-iterations', '500'  # High limit to avoid iteration errors during SWE-bench testing
        ]
        
        print(f'🚀 Running Agent on {instance_id}...')
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 hour: 500 iterations × ~7s avg per iteration
        except subprocess.TimeoutExpired:
            elapsed = time.time() - start_time
            print(f'❌ Timeout after {elapsed:.1f}s')
            return {
                'instance_id': instance_id,
                'model_name_or_path': 'real_agents_framework',
                'model_patch': '',
                'error': 'Timeout',
                'elapsed_time': elapsed
            }
        
        elapsed = time.time() - start_time
        
        # Extract patch
        patch = extract_patch_from_workspace(agents_dir / 'workspace', result.stdout)
        
        if patch is None:
            print(f'⚠️  No patch found')
            return {
                'instance_id': instance_id,
                'model_name_or_path': 'real_agents_framework',
                'model_patch': '',
                'error': 'No patch generated',
                'elapsed_time': elapsed
            }
        
        if patch == '':
            print(f'✅ Empty patch (issue already resolved)')
        else:
            print(f'✅ Patch extracted ({len(patch)} chars)')
        
        return {
            'instance_id': instance_id,
            'model_name_or_path': 'real_agents_framework',
            'model_patch': patch,
            'elapsed_time': elapsed
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f'❌ Error: {e}')
        return {
            'instance_id': instance_id,
            'model_name_or_path': 'real_agents_framework',
            'model_patch': '',
            'error': str(e),
            'elapsed_time': elapsed
        }


def main():
    """Main execution function."""
    print('='*80)
    print('🤖 Real Agents Framework - SB-CLI Evaluation')
    print('='*80)
    
    # Configuration from environment
    DATASET_NAME = 'princeton-nlp/SWE-bench_Lite'
    NUM_INSTANCES = int(os.getenv('NUM_INSTANCES', '1'))
    AGENTS_REPO = os.getenv('AGENTS_REPO')
    MODEL_NAME = os.getenv('MODEL_NAME', 'claude-sonnet-4-20250514')
    
    # Load dataset
    print(f'\nLoading {DATASET_NAME}...')
    dataset = load_dataset(DATASET_NAME, split='test')
    
    # Exclude previously tested instances
    TESTED_INSTANCES = {
        'pallets__flask-4045',
        'astropy__astropy-12907',
        'astropy__astropy-14182',
    }
    
    available_instances = [item for item in dataset if item['instance_id'] not in TESTED_INSTANCES]
    instances = list(available_instances[:NUM_INSTANCES])
    
    print(f'✅ Selected {len(instances)} instance(s): {[i["instance_id"] for i in instances]}')
    
    # Output file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    predictions_file = f'/tmp/real_agents_predictions_{timestamp}.jsonl'
    
    # Process instances
    results = []
    successful = 0
    failed = 0
    
    with open(predictions_file, 'w') as f:
        for idx, instance in enumerate(instances, 1):
            result = run_agent_on_task(instance, idx, len(instances))
            
            f.write(json.dumps(result) + '\n')
            f.flush()
            
            results.append(result)
            
            if 'error' in result:
                failed += 1
            else:
                successful += 1
    
    print('='*80)
    print('SUMMARY')
    print('='*80)
    print(f'Total instances: {len(instances)}')
    print(f'Successful: {successful}')
    print(f'Failed: {failed}')
    print(f'Success rate: {successful/len(instances)*100:.1f}%')
    print(f'Predictions: {predictions_file}')
    print('='*80)
    
    # Output for next step
    print(f'predictions_file={predictions_file}')
    
    return predictions_file


if __name__ == '__main__':
    # Build Docker image first
    agents_dir = Path('/tmp/agents_build')
    if agents_dir.exists():
        subprocess.run(['rm', '-rf', str(agents_dir)], check=True)
    subprocess.run(['git', 'clone', os.getenv('AGENTS_REPO'), str(agents_dir)], check=True)
    subprocess.run(['docker', 'build', '-t', 'agents-framework', '.'], 
                  cwd=agents_dir, check=True)
    
    main()