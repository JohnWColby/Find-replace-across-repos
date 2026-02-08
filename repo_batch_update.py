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
    source_branch: str
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
    # Proxy settings
    proxy_url: str = ""
    proxy_username: str = ""
    proxy_password: str = ""
    use_proxy: bool = False


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
    
    if not os.path.exists(config_file):
        log_error(f"Config file not found: {config_file}")
        sys.exit(1)
    
    # Read the config file directly instead of sourcing it
    # This works on all platforms without needing bash
    config_vars = {}
    replacements = []
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract REPLACEMENTS array - handle parentheses in strings
    # Look for the array declaration and find matching closing paren
    match = re.search(r'declare -a REPLACEMENTS=\(', content)
    if match:
        start = match.end()
        # Find the matching closing parenthesis
        # Track nesting level considering quoted strings
        depth = 1
        i = start
        in_string = False
        string_char = None
        
        while i < len(content) and depth > 0:
            char = content[i]
            
            # Handle string boundaries
            if char in ('"', "'") and (i == 0 or content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            
            # Only count parens outside strings
            if not in_string:
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
            
            i += 1
        
        if depth == 0:
            replacements_str = content[start:i-1]
            
            # Parse each line in the replacements
            for line in replacements_str.split('\n'):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Remove leading/trailing quotes
                if (line.startswith('"') and line.endswith('"')) or \
                   (line.startswith("'") and line.endswith("'")):
                    line = line[1:-1]
                
                # Split on first unquoted pipe
                if '|' in line:
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        search, replace = parts
                        replacements.append((search, replace))
    
    if not replacements:
        log_warning("No replacement rules found in config file")
    else:
        log_info(f"Loaded {len(replacements)} replacement rules")
    
    # Extract simple variable assignments
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Match variable assignments: VAR="value" or VAR='value' or VAR=value
        match = re.match(r'^([A-Z_][A-Z0-9_]*)=(.+)$', line)
        if match:
            var_name = match.group(1)
            var_value = match.group(2).strip()
            
            # Remove quotes if present
            if (var_value.startswith('"') and var_value.endswith('"')) or \
               (var_value.startswith("'") and var_value.endswith("'")):
                var_value = var_value[1:-1]
            
            # Handle variable references like ${VAR:-default}
            if var_value.startswith('${') and var_value.endswith('}'):
                # Extract the variable name and default
                inner = var_value[2:-1]
                if ':-' in inner:
                    env_var, default = inner.split(':-', 1)
                    var_value = os.environ.get(env_var, default.strip('"\''))
                else:
                    env_var = inner
                    var_value = os.environ.get(env_var, '')
            
            config_vars[var_name] = var_value
    
    # Parse file patterns
    file_patterns_str = config_vars.get('FILE_PATTERNS', '*')
    if file_patterns_str == '*':
        file_patterns = ['*']
    else:
        file_patterns = file_patterns_str.split()
    
    # Convert case sensitive to boolean
    case_sensitive = config_vars.get('CASE_SENSITIVE', 'true').lower() == 'true'
    create_pr = config_vars.get('CREATE_PR', 'false').lower() == 'true'
    
    # Get git auth token from environment if not in config
    git_auth_token = config_vars.get('GIT_AUTH_TOKEN', '')
    if not git_auth_token:
        git_auth_token = os.environ.get('GIT_AUTH_TOKEN', '')
    
    # Get proxy settings
    proxy_url = config_vars.get('PROXY_URL', '')
    if not proxy_url:
        proxy_url = os.environ.get('PROXY_URL', '')
    
    proxy_username = config_vars.get('PROXY_USERNAME', '')
    if not proxy_username:
        proxy_username = os.environ.get('PROXY_USERNAME', '')
    
    proxy_password = config_vars.get('PROXY_PASSWORD', '')
    if not proxy_password:
        proxy_password = os.environ.get('PROXY_PASSWORD', '')
    
    use_proxy = config_vars.get('USE_PROXY', 'false').lower() == 'true'
    if not use_proxy and proxy_url:
        use_proxy = True  # Auto-enable if proxy URL is set
    
    return Config(
        repo_list_file=config_vars.get('REPO_LIST_FILE', 'repos.txt'),
        branch_name=config_vars.get('BRANCH_NAME', 'update-strings'),
        source_branch=config_vars.get('SOURCE_BRANCH', ''),
        git_base_url=config_vars.get('GIT_BASE_URL', ''),
        work_dir=config_vars.get('WORK_DIR', './repos_temp'),
        log_file=config_vars.get('LOG_FILE', './batch_update_log.txt'),
        commit_message=config_vars.get('COMMIT_MESSAGE', ''),
        replacements=replacements,
        file_patterns=file_patterns,
        case_sensitive=case_sensitive,
        create_pr=create_pr,
        git_platform=config_vars.get('GIT_PLATFORM', 'github'),
        pr_title=config_vars.get('PR_TITLE', ''),
        pr_description=config_vars.get('PR_DESCRIPTION', ''),
        pr_base_branch=config_vars.get('PR_BASE_BRANCH', 'main'),
        git_auth_method=config_vars.get('GIT_AUTH_METHOD', 'token'),
        git_username=config_vars.get('GIT_USERNAME', ''),
        git_auth_token=git_auth_token,
        proxy_url=proxy_url,
        proxy_username=proxy_username,
        proxy_password=proxy_password,
        use_proxy=use_proxy,
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


def perform_replacements(config: Config) -> Tuple[int, int, int, List[Dict]]:
    """
    Perform all replacements in the repository.
    Uses current working directory as repo path.
    Returns: (files_searched, files_modified, total_replacements, change_details)
    """
    # Use current directory as the repo path
    repo_path = Path.cwd()
    
    log_info("Performing string replacements...")
    log_info(f"Working directory: {repo_path}")
    log_info(f"File patterns: {' '.join(config.file_patterns)}")
    log_info(f"Case sensitive: {config.case_sensitive}")
    log_info(f"Number of replacement rules: {len(config.replacements)}")
    log_info("")
    
    if len(config.replacements) == 0:
        log_error("No replacement rules configured!")
        return 0, 0, 0, []
    
    files_searched = 0
    files_modified = 0
    total_replacements = 0
    change_details = []
    
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
    
    if files_searched == 0:
        log_warning("No files found matching patterns!")
        log_info(f"Current directory: {repo_path}")
        log_info(f"Patterns: {config.file_patterns}")
        # Show what's in current directory
        log_info("Files in current directory:")
        for item in list(repo_path.iterdir())[:10]:
            log_info(f"  {item.name}")
        return 0, 0, 0, []
    
    log_info("")
    
    # Process each replacement rule
    for idx, (search_str, replace_str) in enumerate(config.replacements, 1):
        log_info("----------------------------------------")
        log_info(f"Rule {idx}/{len(config.replacements)}: '{search_str}' → '{replace_str}'")
        log_info("----------------------------------------")
        
        rule_files_modified = 0
        rule_replacements = 0
        
        for filepath in text_files:
            try:
                # Read file
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check if search string exists first (simple string check)
                if config.case_sensitive:
                    if search_str not in content:
                        continue
                    # Count occurrences
                    matches_count = content.count(search_str)
                    # Perform replacement
                    new_content = content.replace(search_str, replace_str)
                else:
                    # Case-insensitive - need regex
                    flags = re.IGNORECASE
                    # Use re.escape for literal matching
                    pattern = re.compile(re.escape(search_str), flags)
                    matches = list(pattern.finditer(content))
                    matches_count = len(matches)
                    
                    if matches_count == 0:
                        continue
                    
                    # Perform replacement
                    new_content = pattern.sub(replace_str, content)
                
                if matches_count > 0 and new_content != content:
                    # Show matches
                    rel_path = filepath.relative_to(repo_path)
                    log_info(f"  📝 File: {rel_path} ({matches_count} occurrence(s))")
                    
                    # Get line numbers for matches
                    lines = content.split('\n')
                    matches_shown = 0
                    max_to_show = 10
                    
                    for line_idx, line in enumerate(lines, 1):
                        line_lower = line.lower() if not config.case_sensitive else line
                        search_lower = search_str.lower() if not config.case_sensitive else search_str
                        
                        if search_lower in line_lower:
                            line_content = line.strip()
                            if len(line_content) > 100:
                                line_content = line_content[:100] + "..."
                            log_info(f"     Line {line_idx}: {line_content}")
                            matches_shown += 1
                            if matches_shown >= max_to_show:
                                if matches_count > max_to_show:
                                    log_info(f"     ... and {matches_count - max_to_show} more occurrence(s)")
                                break
                    
                    # Write back
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    log_info(f"     ✓ Replaced")
                    
                    rule_files_modified += 1
                    rule_replacements += matches_count
                    
                    change_details.append({
                        'file': str(rel_path),
                        'rule': search_str,
                        'matches': matches_count
                    })
            
            except (UnicodeDecodeError, PermissionError, IsADirectoryError) as e:
                # Skip binary files, permission errors, etc.
                continue
            except Exception as e:
                log_warning(f"  Error processing {filepath.name}: {e}")
                continue
        
        if rule_files_modified == 0:
            log_info(f"  ⊘ No matches found for this rule")
            # Show debug info for first rule
            if idx == 1:
                log_info(f"  Debug: Searched {files_searched} files")
                log_info(f"  Sample files:")
                for i, f in enumerate(text_files[:3], 1):
                    log_info(f"    {f.relative_to(repo_path)}")
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
    """Create GitHub Pull Request with optional NTLM proxy support"""
    log_info(f"Creating GitHub PR for: {owner_repo}")
    
    url = f"https://api.github.com/repos/{owner_repo}/pulls"
    
    # Verify token is set
    if not config.git_auth_token:
        log_error("GIT_AUTH_TOKEN is not set!")
        return None
    
    headers = {
        'Authorization': f'Bearer {config.git_auth_token}',
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
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
    log_info(f"Token (first 10 chars): {config.git_auth_token[:10]}...")
    
    # Set up proxy if configured
    proxies = None
    if config.use_proxy and config.proxy_url:
        log_info(f"Using proxy: {config.proxy_url}")
        log_info(f"Proxy username: {config.proxy_username}")
        
        # Format proxy URL with credentials for NTLM
        if config.proxy_username and config.proxy_password:
            # Parse proxy URL
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(config.proxy_url)
            
            # Add credentials to proxy URL
            netloc_with_auth = f"{config.proxy_username}:{config.proxy_password}@{parsed.netloc}"
            proxy_url_with_auth = urlunparse((
                parsed.scheme,
                netloc_with_auth,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            proxies = {
                'http': proxy_url_with_auth,
                'https': proxy_url_with_auth
            }
        else:
            proxies = {
                'http': config.proxy_url,
                'https': config.proxy_url
            }
    
    log_info("")
    
    try:
        # Try with requests-ntlm if available for better NTLM support
        try:
            from requests_ntlm import HttpNtlmAuth
            if config.use_proxy and config.proxy_username and config.proxy_password:
                log_info("Using NTLM authentication for proxy")
                # For NTLM, we need to use the auth parameter
                # Set up session for NTLM
                session = requests.Session()
                session.proxies = {'http': config.proxy_url, 'https': config.proxy_url}
                session.auth = HttpNtlmAuth(config.proxy_username, config.proxy_password)
                response = session.post(url, headers=headers, json=data)
            else:
                response = requests.post(url, headers=headers, json=data, proxies=proxies)
        except ImportError:
            log_info("requests-ntlm not available, using basic proxy authentication")
            log_info("For NTLM proxy support, install: pip install requests-ntlm")
            response = requests.post(url, headers=headers, json=data, proxies=proxies)
        
        log_info(f"HTTP Status: {response.status_code}")
        
        if response.status_code == 201:
            pr_url = response.json()['html_url']
            log_info(f"✓ Pull Request created: {pr_url}")
            return pr_url
        elif response.status_code == 404:
            log_error("GitHub API returned 404 - Possible causes:")
            log_error("  1. Repository doesn't exist or wrong owner/repo name")
            log_error(f"     Tried: {owner_repo}")
            log_error("  2. Token doesn't have access to this repository")
            log_error("  3. Token doesn't have 'repo' scope")
            log_error("  4. Token format issue (should start with 'ghp_' for classic tokens or 'github_pat_' for fine-grained)")
            log_error(f"Full response: {response.text}")
            return None
        elif response.status_code == 401:
            log_error("GitHub API returned 401 - Authentication failed")
            log_error("  Possible causes:")
            log_error("  1. Token is invalid or expired")
            log_error("  2. Token format is wrong")
            log_error(f"  3. Token being used: {config.git_auth_token[:20]}...")
            log_error(f"Full response: {response.text}")
            return None
        elif response.status_code == 407:
            log_error("HTTP 407 - Proxy Authentication Required")
            log_error("  Your corporate proxy requires authentication")
            log_error("  Set these in config.sh or as environment variables:")
            log_error("    PROXY_URL (e.g., http://proxy.company.com:8080)")
            log_error("    PROXY_USERNAME")
            log_error("    PROXY_PASSWORD")
            log_error("  For NTLM: pip install requests-ntlm")
            return None
        elif response.status_code == 422:
            log_error("GitHub API returned 422 - Validation failed")
            log_error("  Possible causes:")
            log_error("  1. PR already exists for this branch")
            log_error("  2. Branch doesn't exist on remote")
            log_error("  3. Base branch doesn't exist")
            error_details = response.json()
            log_error(f"Error details: {json.dumps(error_details, indent=2)}")
            return None
        else:
            log_error(f"Failed to create PR: {response.json().get('message', 'Unknown error')}")
            log_error(f"Full response: {response.text}")
            return None
    except requests.exceptions.ProxyError as e:
        log_error(f"Proxy error: {e}")
        log_error("Check your proxy settings:")
        log_error(f"  PROXY_URL: {config.proxy_url}")
        log_error(f"  PROXY_USERNAME: {config.proxy_username}")
        log_error("For NTLM proxy, install: pip install requests-ntlm")
        return None
    except Exception as e:
        log_error(f"Exception creating PR: {e}")
        import traceback
        log_error(traceback.format_exc())
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
    
    # Save original directory to ensure we always return to it
    original_dir = Path.cwd()
    
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
        log_info(f"Changed to directory: {os.getcwd()}")
        
        # Checkout source branch if specified
        if config.source_branch:
            log_info(f"Checking out source branch: {config.source_branch}")
            result = subprocess.run(['git', 'checkout', config.source_branch], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                log_error(f"Failed to checkout source branch '{config.source_branch}': {result.stderr}")
                log_error("Source branch may not exist in this repository")
                log_failed_repo(repo_name, f"Source branch '{config.source_branch}' not found")
                return False
            
            log_info(f"✓ Checked out source branch: {config.source_branch}")
            
            # Fetch latest changes
            log_info("Fetching latest changes from remote...")
            result = subprocess.run(['git', 'fetch', 'origin', config.source_branch], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                log_warning(f"Failed to fetch: {result.stderr}")
            else:
                log_info("✓ Fetched latest changes")
            
            # Check if local branch is behind remote
            log_info("Checking if branch is up to date...")
            result = subprocess.run(['git', 'rev-list', '--count', f'HEAD..origin/{config.source_branch}'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                commits_behind = result.stdout.strip()
                
                if commits_behind and int(commits_behind) > 0:
                    log_info(f"Branch is {commits_behind} commit(s) behind remote")
                    
                    # Check if there are local commits ahead
                    result = subprocess.run(['git', 'rev-list', '--count', f'origin/{config.source_branch}..HEAD'], 
                                          capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        commits_ahead = result.stdout.strip()
                        
                        if commits_ahead and int(commits_ahead) > 0:
                            log_warning(f"Branch has {commits_ahead} local commit(s) ahead of remote")
                            log_warning("Skipping pull to avoid potential conflicts")
                        else:
                            # Safe to pull - no local commits ahead
                            log_info("Pulling latest changes...")
                            result = subprocess.run(['git', 'pull', 'origin', config.source_branch], 
                                                  capture_output=True, text=True)
                            
                            if result.returncode != 0:
                                log_warning(f"Failed to pull: {result.stderr}")
                            else:
                                log_info("✓ Pulled latest changes")
                else:
                    log_info("✓ Branch is up to date")
        else:
            # Get current branch name for logging
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            current_branch = result.stdout.strip()
            log_info(f"Using current branch: {current_branch}")
        
        # Create or checkout new branch
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
        
        # Perform replacements (uses current directory)
        files_searched, files_modified, total_replacements, _ = perform_replacements(config)
        
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
        import traceback
        log_error(traceback.format_exc())
        log_entries.append(f"{repo_name}\tFailed: {str(e)}")
        return False
    finally:
        # ALWAYS return to original directory
        os.chdir(original_dir)
        log_info(f"Returned to directory: {os.getcwd()}")
        log_info("")


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
