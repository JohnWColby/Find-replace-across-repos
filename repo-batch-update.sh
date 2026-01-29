#!/bin/bash

# Repo Batch Update Script
# This script clones multiple repositories, creates a branch, performs find/replace operations,
# commits the changes, and pushes to remote.

set -e  # Exit on error

# ============================================================================
# CONFIGURATION SECTION - MODIFY THESE VALUES
# ============================================================================

# File containing repo names (one per line)
REPO_LIST_FILE="repos.txt"

# Branch name to create
BRANCH_NAME="update-strings"

# Git remote base URL (will be combined with repo name)
# Examples:
#   For GitHub: "https://github.com/username"
#   For GitLab: "https://gitlab.com/username"
#   For SSH: "git@github.com:username"
GIT_BASE_URL="https://github.com/yourusername"

# Working directory for cloning repos (will be created if it doesn't exist)
WORK_DIR="./repos_temp"

# Commit message
COMMIT_MESSAGE="Update string replacements across repository"

# Find/Replace mappings (add as many as needed)
# Format: "SEARCH_STRING|REPLACEMENT_STRING"
declare -a REPLACEMENTS=(
    "oldString1|newString1"
    "oldString2|newString2"
    "TODO: update this|DONE: updated"
)

# File extensions to process (leave empty to process all files)
# Example: "*.py *.js *.md"
FILE_PATTERNS="*"

# ============================================================================
# END CONFIGURATION SECTION
# ============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to generate git URL from repo name
generate_git_url() {
    local repo_name=$1
    
    # Check if base URL uses SSH or HTTPS
    if [[ $GIT_BASE_URL == git@* ]]; then
        # SSH format: git@github.com:username/repo.git
        echo "${GIT_BASE_URL}/${repo_name}.git"
    else
        # HTTPS format: https://github.com/username/repo.git
        echo "${GIT_BASE_URL}/${repo_name}.git"
    fi
}

# Function to perform find/replace in a repository
perform_replacements() {
    local repo_path=$1
    
    log_info "Performing string replacements..."
    
    local changes_made=false
    
    for replacement in "${REPLACEMENTS[@]}"; do
        IFS='|' read -r search_str replace_str <<< "$replacement"
        
        log_info "  Replacing '$search_str' with '$replace_str'"
        
        # Find all files matching patterns (excluding .git directory)
        while IFS= read -r -d '' file; do
            # Check if file is a text file (not binary)
            if file "$file" | grep -q text; then
                # Perform replacement using sed
                if grep -q "$search_str" "$file" 2>/dev/null; then
                    sed -i "s|$search_str|$replace_str|g" "$file"
                    log_info "    Updated: $file"
                    changes_made=true
                fi
            fi
        done < <(find "$repo_path" -type f -not -path "*/.git/*" -name "$FILE_PATTERNS" -print0)
    done
    
    if [ "$changes_made" = false ]; then
        log_warning "No changes were made in this repository"
        return 1
    fi
    
    return 0
}

# Function to process a single repository
process_repo() {
    local repo_name=$1
    local git_url=$(generate_git_url "$repo_name")
    local repo_path="$WORK_DIR/$repo_name"
    
    log_info "========================================="
    log_info "Processing repository: $repo_name"
    log_info "Git URL: $git_url"
    log_info "========================================="
    
    # Clone the repository
    log_info "Cloning repository..."
    if ! git clone "$git_url" "$repo_path"; then
        log_error "Failed to clone $repo_name"
        return 1
    fi
    
    cd "$repo_path" || return 1
    
    # Create and checkout new branch
    log_info "Creating branch: $BRANCH_NAME"
    if ! git checkout -b "$BRANCH_NAME"; then
        log_error "Failed to create branch $BRANCH_NAME"
        cd - > /dev/null
        return 1
    fi
    
    # Perform replacements
    if ! perform_replacements "$repo_path"; then
        log_warning "Skipping commit for $repo_name (no changes made)"
        cd - > /dev/null
        return 0
    fi
    
    # Stage all changes
    log_info "Staging changes..."
    git add -A
    
    # Check if there are changes to commit
    if git diff --cached --quiet; then
        log_warning "No changes to commit for $repo_name"
        cd - > /dev/null
        return 0
    fi
    
    # Commit changes
    log_info "Creating commit..."
    if ! git commit -m "$COMMIT_MESSAGE"; then
        log_error "Failed to commit changes"
        cd - > /dev/null
        return 1
    fi
    
    # Push to remote
    log_info "Pushing branch to remote..."
    if ! git push -u origin "$BRANCH_NAME"; then
        log_error "Failed to push branch to remote"
        cd - > /dev/null
        return 1
    fi
    
    log_info "Successfully processed $repo_name"
    cd - > /dev/null
    return 0
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

main() {
    log_info "Starting repo batch update script"
    
    # Check if repo list file exists
    if [ ! -f "$REPO_LIST_FILE" ]; then
        log_error "Repo list file not found: $REPO_LIST_FILE"
        exit 1
    fi
    
    # Create working directory
    mkdir -p "$WORK_DIR"
    
    # Read repo names and process each one
    local total_repos=0
    local successful_repos=0
    local failed_repos=0
    
    while IFS= read -r repo_name || [ -n "$repo_name" ]; do
        # Skip empty lines and comments
        [[ -z "$repo_name" || "$repo_name" =~ ^# ]] && continue
        
        # Trim whitespace
        repo_name=$(echo "$repo_name" | xargs)
        
        total_repos=$((total_repos + 1))
        
        if process_repo "$repo_name"; then
            successful_repos=$((successful_repos + 1))
        else
            failed_repos=$((failed_repos + 1))
        fi
        
        echo ""
    done < "$REPO_LIST_FILE"
    
    # Summary
    log_info "========================================="
    log_info "SUMMARY"
    log_info "========================================="
    log_info "Total repositories: $total_repos"
    log_info "Successful: $successful_repos"
    log_info "Failed: $failed_repos"
    
    if [ $failed_repos -gt 0 ]; then
        exit 1
    fi
}

# Run main function
main
