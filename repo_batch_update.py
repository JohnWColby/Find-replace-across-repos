#!/usr/bin/env python3
"""
Repo Batch Update Script (Python Version)
High-performance implementation for processing many repos with many rules.
"""

import os
import sys
import subprocess
import re
import json
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from datetime import datetime
import concurrent.futures
from dataclasses import dataclass
import requests


@dataclass
class Config:
    """Configuration loaded from config file"""
    repo_list_file: str
    branch_name: str
    git_base_url: str
    work_dir: str
    log_file: str
    commit_message: str
    replacements: List[Tuple[str, str]]
    file_patterns: List[str]
    case_sensitive: bool
    create_pr: bool
    git_platform: str
    pr_title: str
    pr_description: str
    pr_base_branch: str
    git_auth_method: str
    git_username: str
    git_auth_token: str


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


def log_info(message: str):
    """Log info message"""
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}", flush=True)


def log_error(message: str):
    """Log error message"""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}", flush=True)


def log_warning(message: str):
    """Log warning message"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}", flush=True)


def load_config(config_file: str) -> Config:
    """Load configuration from bash config file"""
    log_info(f"Loading configuration from: {config_file}")
    
    # Source the bash config file and extract variables
    cmd = f'source {config_file} && env'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
    env_output, _ = proc.communicate()
    
    env_dict = {}
    for line in env_output.decode().split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            env_dict[key] = value
    
    # Parse replacements array from the config file
    replacements = []
    with open(config_file, 'r') as f:
        content = f.read()
        # Extract REPLACEMENTS array
        match = re.search(r'declare -a REPLACEMENTS=\((.*?)\)', content, re.DOTALL)
        if match:
            replacements_str = match.group(1)
            for line in replacements_str.split('\n'):
                line = line.strip().strip('"\'')
                if '|' in line and not line.startswith('#'):
                    search, replace = line.split('|', 1)
                    replacements.append((search, replace))
    
    # Parse file patterns
    file_patterns_str = env_dict.get('FILE_PATTERNS', '*')
    if file_patterns_str == '*':
        file_patterns = ['*']
    else:
        file_patterns = file_patterns_str.split()
    
    # Convert case sensitive to boolean
    case_sensitive = env_dict.get('CASE_SENSITIVE', 'true').lower() == 'true'
    create_pr = env_dict.get('CREATE_PR', 'false').lower() == 'true'
    
    return Config(
        repo_list_file=env_dict.get('REPO_LIST_FILE', 'repos.txt'),
        branch_name=env_dict.get('BRANCH_NAME', 'update-strings'),
        git_base_url=env_dict.get('GIT_BASE_URL', ''),
        work_dir=env_dict.get('WORK_DIR', './repos_temp'),
        log_file=env_dict.get('LOG_FILE', './batch_update_log.txt'),
        commit_message=env_dict.get('COMMIT_MESSAGE', ''),
        replacements=replacements,
        file_patterns=file_patterns,
        case_sensitive=case_sensitive,
        create_pr=create_pr,
        git_platform=env_dict.get('GIT_PLATFORM', 'github'),
        pr_title=env_dict.get('PR_TITLE', ''),
        pr_description=env_dict.get('PR_DESCRIPTION', ''),
        pr_base_branch=env_dict.get('PR_BASE_BRANCH', 'main'),
        git_auth_method=env_dict.get('GIT_AUTH_METHOD', 'token'),
        git_username=env_dict.get('GIT_USERNAME', ''),
        git_auth_token=env_dict.get('GIT_AUTH_TOKEN', ''),
    )


def setup_git_auth(config: Config):
    """Set up Git authentication"""
    log_info("Setting up Git authentication...")
    log_info(f"Authentication method: {config.git_auth_method}")
    
    if config.git_auth_method == 'token':
        if not config.git_auth_token:
            log_error("GIT_AUTH_TOKEN not set")
            sys.exit(1)
        
        log_info(f"Username: {config.git_username}")
        log_info(f"Token: {config.git_auth_token[:10]}... (truncated)")
        
        # Extract host from URL
        if config.git_base_url.startswith('https://'):
            git_host = config.git_base_url.replace('https://', '').split('/')[0]
        else:
            log_error("GIT_BASE_URL must be HTTPS for token auth")
            sys.exit(1)
        
        # Set up Git credential helper
        cred_file = os.path.expanduser('~/.git-credentials-batch-temp')
        with open(cred_file, 'w') as f:
            f.write(f"https://{config.git_username}:{config.git_auth_token}@{git_host}\n")
        
        subprocess.run(['git', 'config', '--global', 'credential.helper', f'store --file {cred_file}'])
        log_info(f"✓ Git authentication configured for {git_host}")
    
    elif config.git_auth_method == 'ssh':
        # Check SSH keys
        result = subprocess.run(['ssh-add', '-l'], capture_output=True)
        if result.returncode != 0:
            log_error("No SSH keys loaded")
            sys.exit(1)
        log_info("✓ SSH authentication configured")
    
    elif config.git_auth_method == 'none':
        log_warning("Git authentication disabled")


def cleanup_git_auth(config: Config):
    """Clean up Git authentication"""
    if config.git_auth_method == 'token':
        cred_file = os.path.expanduser('~/.git-credentials-batch-temp')
        if os.path.exists(cred_file):
            os.remove(cred_file)
        subprocess.run(['git', 'config', '--global', '--unset', 'credential.helper'], 
                      capture_output=True)
        log_info("Git authentication cleaned up")


def generate_git_url(config: Config, repo_name: str) -> str:
    """Generate Git URL from repo name"""
    if config.git_base_url.startswith('git@'):
        return f"{config.git_base_url}/{repo_name}.git"
    else:
        return f"{config.git_base_url}/{repo_name}.git"


def match_file_pattern(filepath: Path, patterns: List[str]) -> bool:
    """Check if file matches any of the patterns"""
    if patterns == ['*']:
        return True
    
    for pattern in patterns:
        if filepath.match(pattern):
            return True
    return False


def perform_replacements(repo_path: Path, config: Config) -> Tuple[int, int, int, List[Dict]]:
    """
    Perform all replacements in the repository.
    Returns: (files_searched, files_modified, total_replacements, change_details)
    """
    log_info("Performing string replacements...")
    log_info(f"File patterns: {' '.join(config.file_patterns)}")
    log_info(f"Case sensitive: {config.case_sensitive}")
    log_info(f"Number of replacement rules: {len(config.replacements)}")
    log_info("")
    
    files_searched = 0
    files_modified = 0
    total_replacements = 0
    change_details = []
    
    # Compile regex patterns for all replacements
    compiled_patterns = []
    for search_str, replace_str in config.replacements:
        flags = 0 if config.case_sensitive else re.IGNORECASE
        try:
            pattern = re.compile(re.escape(search_str), flags)
            compiled_patterns.append((pattern, search_str, replace_str))
        except re.error as e:
            log_error(f"Invalid regex pattern '{search_str}': {e}")
            continue
    
    # Get all files matching patterns
    all_files = []
    for pattern in config.file_patterns:
        if pattern == '*':
            all_files.extend(repo_path.rglob('*'))
        else:
            all_files.extend(repo_path.rglob(pattern))
    
    # Filter out directories and .git files
    text_files = [f for f in all_files 
                  if f.is_file() and '.git' not in str(f.relative_to(repo_path)).split(os.sep)]
    
    files_searched = len(text_files)
    log_info(f"Found {files_searched} files to process")
    log_info("")
    
    # Process each replacement rule
    for idx, (pattern, search_str, replace_str) in enumerate(compiled_patterns, 1):
        log_info("----------------------------------------")
        log_info(f"Rule {idx}/{len(compiled_patterns)}: '{search_str}' → '{replace_str}'")
        log_info("----------------------------------------")
        
        rule_files_modified = 0
        rule_replacements = 0
        
        for filepath in text_files:
            try:
                # Read file
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find all matches
                matches = list(pattern.finditer(content))
                
                if matches:
                    # Show all matches
                    rel_path = filepath.relative_to(repo_path)
                    log_info(f"  📝 File: {rel_path} ({len(matches)} occurrence(s))")
                    
                    # Get line numbers for each match
                    lines = content.split('\n')
                    for match in matches:
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = lines[line_num - 1].strip()
                        if len(line_content) > 100:
                            line_content = line_content[:100] + "..."
                        log_info(f"     Line {line_num}: {line_content}")
                    
                    # Perform replacement
                    new_content = pattern.sub(replace_str, content)
                    
                    # Write back
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    log_info(f"     ✓ Replaced {len(matches)} occurrence(s)")
                    
                    rule_files_modified += 1
                    rule_replacements += len(matches)
                    
                    change_details.append({
                        'file': str(rel_path),
                        'rule': search_str,
                        'matches': len(matches)
                    })
            
            except (UnicodeDecodeError, PermissionError, IsADirectoryError):
                # Skip binary files, permission errors, etc.
                continue
        
        if rule_files_modified == 0:
            log_info("  ⊘ No matches found for this rule")
        else:
            log_info("")
            log_info(f"  Summary for this rule:")
            log_info(f"    Files modified: {rule_files_modified}")
            log_info(f"    Total replacements: {rule_replacements}")
            files_modified += rule_files_modified
            total_replacements += rule_replacements
        log_info("")
    
    log_info("========================================")
    log_info("REPLACEMENT SUMMARY")
    log_info("========================================")
    log_info(f"Total files searched: {files_searched}")
    log_info(f"Total files modified: {files_modified}")
    log_info(f"Total replacements made: {total_replacements}")
    log_info("")
    
    return files_searched, files_modified, total_replacements, change_details


def create_github_pr(config: Config, owner_repo: str) -> Optional[str]:
    """Create GitHub Pull Request"""
    log_info(f"Creating GitHub PR for: {owner_repo}")
    
    url = f"https://api.github.com/repos/{owner_repo}/pulls"
    headers = {
        'Authorization': f'token {config.git_auth_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'title': config.pr_title,
        'body': config.pr_description,
        'head': config.branch_name,
        'base': config.pr_base_branch
    }
    
    log_info(f"API endpoint: {url}")
    log_info(f"PR title: {config.pr_title}")
    log_info(f"Source branch: {config.branch_name}")
    log_info(f"Target branch: {config.pr_base_branch}")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        log_info(f"HTTP Status: {response.status_code}")
        
        if response.status_code == 201:
            pr_url = response.json()['html_url']
            log_info(f"✓ Pull Request created: {pr_url}")
            return pr_url
        else:
            log_error(f"Failed to create PR: {response.json().get('message', 'Unknown error')}")
            log_error(f"Full response: {response.text}")
            return None
    except Exception as e:
        log_error(f"Exception creating PR: {e}")
        return None


def extract_owner_repo(config: Config, repo_name: str) -> str:
    """Extract owner/repo from base URL"""
    if config.git_base_url.startswith('git@'):
        owner = config.git_base_url.split(':')[1]
    else:
        owner = config.git_base_url.rstrip('/').split('/')[-1]
    
    return f"{owner}/{repo_name}"


def process_repo(repo_name: str, config: Config, log_entries: List[str]) -> bool:
    """Process a single repository"""
    log_info("=========================================")
    log_info(f"Processing repository: {repo_name}")
    log_info("=========================================")
    
    git_url = generate_git_url(config, repo_name)
    repo_path = Path(config.work_dir) / repo_name
    
    log_info(f"Git URL: {git_url}")
    log_info(f"Local path: {repo_path}")
    log_info("")
    
    try:
        # Clone repository
        log_info("Cloning repository...")
        result = subprocess.run(['git', 'clone', git_url, str(repo_path)], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"Failed to clone: {result.stderr}")
            log_entries.append(f"{repo_name}\tFailed: Clone error")
            return False
        
        log_info("✓ Cloned successfully")
        
        # Change to repo directory
        os.chdir(repo_path)
        
        # Create or checkout branch
        log_info(f"Creating branch: {config.branch_name}")
        result = subprocess.run(['git', 'checkout', '-b', config.branch_name], 
                              capture_output=True, text=True)
        
        if result.returncode != 0 and 'already exists' in result.stderr:
            log_warning(f"Branch '{config.branch_name}' exists, checking out...")
            result = subprocess.run(['git', 'checkout', config.branch_name], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                log_error(f"Failed to checkout branch: {result.stderr}")
                log_entries.append(f"{repo_name}\tFailed: Branch checkout error")
                return False
        elif result.returncode != 0:
            log_error(f"Failed to create branch: {result.stderr}")
            log_entries.append(f"{repo_name}\tFailed: Branch creation error")
            return False
        
        log_info("✓ Branch ready")
        log_info("")
        
        # Perform replacements
        files_searched, files_modified, total_replacements, _ = perform_replacements(repo_path, config)
        
        if files_modified == 0:
            log_warning("No changes made")
            log_entries.append(f"{repo_name}\tNo changes (replacements did not match any content)")
            return True
        
        # Stage changes
        log_info("Staging changes...")
        subprocess.run(['git', 'add', '-A'])
        
        # Commit
        log_info("Creating commit...")
        result = subprocess.run(['git', 'commit', '-m', config.commit_message], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"Failed to commit: {result.stderr}")
            log_entries.append(f"{repo_name}\tFailed: Commit error")
            return False
        
        log_info("✓ Committed")
        
        # Push
        log_info("Pushing to remote...")
        result = subprocess.run(['git', 'push', '-u', 'origin', config.branch_name], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            log_error(f"Failed to push: {result.stderr}")
            log_entries.append(f"{repo_name}\tFailed: Push error")
            return False
        
        log_info("✓ Pushed")
        log_info("")
        
        # Create PR if enabled
        if config.create_pr:
            log_info("=========================================")
            log_info(f"Creating Pull Request for {repo_name}")
            log_info("=========================================")
            
            owner_repo = extract_owner_repo(config, repo_name)
            pr_url = create_github_pr(config, owner_repo)
            
            if pr_url:
                log_entries.append(f"{repo_name}\t{pr_url}")
            else:
                log_entries.append(f"{repo_name}\tBranch pushed (PR creation failed)")
        else:
            log_entries.append(f"{repo_name}\tBranch pushed (PR not created)")
        
        log_info(f"✓ Successfully processed {repo_name}")
        return True
        
    except Exception as e:
        log_error(f"Exception processing {repo_name}: {e}")
        log_entries.append(f"{repo_name}\tFailed: {str(e)}")
        return False
    finally:
        # Always return to original directory
        os.chdir(Path.cwd().parent if Path.cwd().name == repo_name else Path.cwd())


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Batch update multiple repositories')
    parser.add_argument('--config', default='./config.sh', help='Config file path')
    args = parser.parse_args()
    
    log_info("=========================================")
    log_info("Repo Batch Update Script (Python)")
    log_info("=========================================")
    log_info(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_info("")
    
    # Load configuration
    config = load_config(args.config)
    
    log_info("Configuration:")
    log_info(f"  Config file: {args.config}")
    log_info(f"  Repo list: {config.repo_list_file}")
    log_info(f"  Branch name: {config.branch_name}")
    log_info(f"  Base URL: {config.git_base_url}")
    log_info(f"  Work directory: {config.work_dir}")
    log_info(f"  Log file: {config.log_file}")
    log_info(f"  File patterns: {' '.join(config.file_patterns)}")
    log_info(f"  Create PR: {config.create_pr}")
    log_info(f"  Replacement rules: {len(config.replacements)}")
    log_info("")
    
    # Setup authentication
    setup_git_auth(config)
    log_info("")
    
    # Create work directory
    Path(config.work_dir).mkdir(parents=True, exist_ok=True)
    
    # Read repo list
    with open(config.repo_list_file, 'r') as f:
        repos = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    log_info(f"Found {len(repos)} repositories to process")
    log_info("")
    
    # Initialize log file
    log_entries = ["Repository\tResult"]
    
    # Process each repo
    successful = 0
    failed = 0
    
    for idx, repo in enumerate(repos, 1):
        log_info(f"=========================================")
        log_info(f"Repository {idx} of {len(repos)}: {repo}")
        log_info(f"=========================================")
        
        if process_repo(repo, config, log_entries):
            successful += 1
        else:
            failed += 1
        
        log_info("")
    
    # Write log file
    with open(config.log_file, 'w') as f:
        f.write('\n'.join(log_entries))
    
    # Cleanup
    cleanup_git_auth(config)
    
    # Summary
    log_info("=========================================")
    log_info("SUMMARY")
    log_info("=========================================")
    log_info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_info(f"Total repositories: {len(repos)}")
    log_info(f"Successful: {successful}")
    log_info(f"Failed: {failed}")
    log_info("")
    log_info(f"Detailed log saved to: {config.log_file}")
    
    if failed > 0:
        log_warning(f"⚠️  {failed} repositories failed. Check the log file for details.")
    else:
        log_info("✓ All repositories processed successfully!")


if __name__ == '__main__':
    main()
