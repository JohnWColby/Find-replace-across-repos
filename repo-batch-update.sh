#!/bin/bash

# Repo Batch Update Script
# This script clones multiple repositories, creates a branch, performs find/replace operations,
# commits the changes, and pushes to remote.

# Note: Script continues even if individual repos fail

# ============================================================================
# LOAD CONFIGURATION
# ============================================================================

# Default config file location
CONFIG_FILE="${CONFIG_FILE:-./config.sh}"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Configuration file not found: $CONFIG_FILE"
    echo "Please create config.sh or set CONFIG_FILE environment variable"
    exit 1
fi

# Load configuration
source "$CONFIG_FILE"

# Validate required configuration
if [ -z "$REPO_LIST_FILE" ] || [ -z "$BRANCH_NAME" ] || [ -z "$GIT_BASE_URL" ]; then
    echo "ERROR: Required configuration missing in $CONFIG_FILE"
    echo "Required: REPO_LIST_FILE, BRANCH_NAME, GIT_BASE_URL"
    exit 1
fi

# Validate authentication configuration
if [ -z "$GIT_AUTH_METHOD" ]; then
    echo "ERROR: GIT_AUTH_METHOD not set in $CONFIG_FILE"
    echo "Set to 'token', 'ssh', or 'none'"
    exit 1
fi

# ============================================================================
# SCRIPT LOGIC (DO NOT EDIT BELOW THIS LINE)
# ============================================================================

# Function to set up Git authentication
setup_git_auth() {
    case $GIT_AUTH_METHOD in
        token)
            if [ -z "$GIT_AUTH_TOKEN" ]; then
                echo "ERROR: GIT_AUTH_METHOD is 'token' but GIT_AUTH_TOKEN is not set"
                echo "Set GIT_AUTH_TOKEN in config.sh or as environment variable"
                exit 1
            fi
            
            if [ -z "$GIT_USERNAME" ]; then
                echo "ERROR: GIT_AUTH_METHOD is 'token' but GIT_USERNAME is not set"
                echo "Set GIT_USERNAME in config.sh"
                exit 1
            fi
            
            # Configure Git credential helper to use the token
            # This sets up authentication for HTTPS URLs
            git config --global credential.helper store
            
            # Extract the host from GIT_BASE_URL
            local git_host=""
            if [[ $GIT_BASE_URL == https://* ]]; then
                git_host=$(echo "$GIT_BASE_URL" | sed 's|https://||' | sed 's|/.*||')
            elif [[ $GIT_BASE_URL == http://* ]]; then
                git_host=$(echo "$GIT_BASE_URL" | sed 's|http://||' | sed 's|/.*||')
            else
                echo "ERROR: GIT_AUTH_METHOD is 'token' but GIT_BASE_URL is not HTTPS"
                echo "For token auth, use https:// URLs like: https://github.com/org-name"
                exit 1
            fi
            
            # Store credentials in Git credential store
            # This creates/updates ~/.git-credentials
            echo "https://${GIT_USERNAME}:${GIT_AUTH_TOKEN}@${git_host}" > ~/.git-credentials-batch-temp
            git config --global credential.helper "store --file ~/.git-credentials-batch-temp"
            
            log_info "Git authentication configured using token for ${git_host}"
            ;;
            
        ssh)
            # Check if SSH agent is running and has keys
            if ! ssh-add -l &>/dev/null; then
                echo "ERROR: GIT_AUTH_METHOD is 'ssh' but no SSH keys are loaded"
                echo "Please run: ssh-add ~/.ssh/id_rsa (or your key file)"
                echo "Or start ssh-agent: eval \$(ssh-agent -s) && ssh-add"
                exit 1
            fi
            
            if [[ $GIT_BASE_URL != git@* ]]; then
                echo "ERROR: GIT_AUTH_METHOD is 'ssh' but GIT_BASE_URL is not SSH format"
                echo "For SSH auth, use SSH URLs like: git@github.com:org-name"
                exit 1
            fi
            
            log_info "Git authentication configured using SSH keys"
            ;;
            
        none)
            log_warning "Git authentication disabled - only public repos will work"
            ;;
            
        *)
            echo "ERROR: Invalid GIT_AUTH_METHOD: $GIT_AUTH_METHOD"
            echo "Valid values: 'token', 'ssh', 'none'"
            exit 1
            ;;
    esac
}

# Function to clean up Git authentication
cleanup_git_auth() {
    if [ "$GIT_AUTH_METHOD" = "token" ]; then
        # Remove temporary credentials file
        rm -f ~/.git-credentials-batch-temp
        # Reset to default credential helper
        git config --global --unset credential.helper
        log_info "Git authentication cleaned up"
    fi
}

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

# Function to log completed repo with PR URL
log_completed_repo() {
    local repo_name=$1
    local pr_url=$2
    local status=$3
    
    if [ -n "$pr_url" ]; then
        echo -e "${repo_name}\t${pr_url}" >> "$LOG_FILE"
    elif [ "$status" = "no_changes" ]; then
        echo -e "${repo_name}\tNo changes (replacements did not match any content)" >> "$LOG_FILE"
    else
        echo -e "${repo_name}\tBranch pushed (PR not created)" >> "$LOG_FILE"
    fi
}

# Function to log failed repo
log_failed_repo() {
    local repo_name=$1
    local reason=$2
    
    echo -e "${repo_name}\tFailed: ${reason}" >> "$LOG_FILE"
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

# Function to extract owner and repo from git URL or base URL
extract_owner_repo() {
    local repo_name=$1
    local owner=""
    
    # Extract owner from base URL
    if [[ $GIT_BASE_URL == git@*:* ]]; then
        # SSH format: git@github.com:username
        owner=$(echo "$GIT_BASE_URL" | sed 's/.*://')
    elif [[ $GIT_BASE_URL == https://* ]] || [[ $GIT_BASE_URL == http://* ]]; then
        # HTTPS format: https://github.com/username
        owner=$(echo "$GIT_BASE_URL" | sed 's|.*/||')
    fi
    
    echo "$owner/$repo_name"
}

# Function to create a Pull Request
create_pull_request() {
    local repo_name=$1
    local owner_repo=$(extract_owner_repo "$repo_name")
    
    if [ -z "$GIT_TOKEN" ]; then
        log_warning "GIT_TOKEN not set. Skipping PR creation."
        log_info "To create PRs automatically, set GIT_TOKEN environment variable or update the script."
        echo ""  # Return empty string
        return 0
    fi
    
    log_info "Creating Pull Request..."
    
    local pr_url=""
    case $GIT_PLATFORM in
        github)
            pr_url=$(create_github_pr "$owner_repo")
            ;;
        gitlab)
            pr_url=$(create_gitlab_pr "$owner_repo")
            ;;
        bitbucket)
            pr_url=$(create_bitbucket_pr "$owner_repo")
            ;;
        *)
            log_error "Unknown platform: $GIT_PLATFORM"
            echo ""
            return 1
            ;;
    esac
    
    echo "$pr_url"  # Return the PR URL
}

# Function to create GitHub PR
create_github_pr() {
    local repo=$1
    
    local response=$(curl -s -X POST \
        -H "Authorization: token $GIT_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$repo/pulls" \
        -d @- <<EOF
{
  "title": "$PR_TITLE",
  "body": "$PR_DESCRIPTION",
  "head": "$BRANCH_NAME",
  "base": "$PR_BASE_BRANCH"
}
EOF
)
    
    # Check if PR was created successfully
    local pr_url=$(echo "$response" | grep -o '"html_url": *"[^"]*"' | head -1 | sed 's/"html_url": *"\([^"]*\)"/\1/')
    
    if [ -n "$pr_url" ]; then
        log_info "✓ Pull Request created: $pr_url"
        echo "$pr_url"  # Return the URL
        return 0
    else
        local error_message=$(echo "$response" | grep -o '"message": *"[^"]*"' | sed 's/"message": *"\([^"]*\)"/\1/')
        log_error "Failed to create PR: $error_message"
        return 1
    fi
}

# Function to create GitLab MR (Merge Request)
create_gitlab_pr() {
    local repo=$1
    local encoded_repo=$(echo "$repo" | sed 's/\//%2F/g')
    
    # GitLab uses different API structure - adjust the URL based on your GitLab instance
    local gitlab_url="https://gitlab.com"
    
    local response=$(curl -s -X POST \
        -H "PRIVATE-TOKEN: $GIT_TOKEN" \
        -H "Content-Type: application/json" \
        "$gitlab_url/api/v4/projects/$encoded_repo/merge_requests" \
        -d @- <<EOF
{
  "source_branch": "$BRANCH_NAME",
  "target_branch": "$PR_BASE_BRANCH",
  "title": "$PR_TITLE",
  "description": "$PR_DESCRIPTION"
}
EOF
)
    
    local mr_url=$(echo "$response" | grep -o '"web_url": *"[^"]*"' | head -1 | sed 's/"web_url": *"\([^"]*\)"/\1/')
    
    if [ -n "$mr_url" ]; then
        log_info "✓ Merge Request created: $mr_url"
        echo "$mr_url"  # Return the URL
        return 0
    else
        local error_message=$(echo "$response" | grep -o '"message": *"[^"]*"' | sed 's/"message": *"\([^"]*\)"/\1/')
        log_error "Failed to create MR: $error_message"
        return 1
    fi
}

# Function to create Bitbucket PR
create_bitbucket_pr() {
    local repo=$1
    
    # Bitbucket API v2.0
    local response=$(curl -s -X POST \
        -u "$GIT_TOKEN" \
        -H "Content-Type: application/json" \
        "https://api.bitbucket.org/2.0/repositories/$repo/pullrequests" \
        -d @- <<EOF
{
  "title": "$PR_TITLE",
  "description": "$PR_DESCRIPTION",
  "source": {
    "branch": {
      "name": "$BRANCH_NAME"
    }
  },
  "destination": {
    "branch": {
      "name": "$PR_BASE_BRANCH"
    }
  }
}
EOF
)
    
    local pr_url=$(echo "$response" | grep -o '"html": *{[^}]*"href": *"[^"]*"' | sed 's/.*"href": *"\([^"]*\)"/\1/')
    
    if [ -n "$pr_url" ]; then
        log_info "✓ Pull Request created: $pr_url"
        echo "$pr_url"  # Return the URL
        return 0
    else
        local error_message=$(echo "$response" | grep -o '"message": *"[^"]*"' | sed 's/"message": *"\([^"]*\)"/\1/')
        log_error "Failed to create PR: $error_message"
        return 1
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
        return 2  # Return 2 to indicate no changes
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
    if ! git clone "$git_url" "$repo_path" 2>&1 | grep -v "^Cloning into"; then
        log_error "Failed to clone $repo_name"
        log_failed_repo "$repo_name" "Failed to clone repository"
        return 1
    fi
    
    cd "$repo_path" || {
        log_failed_repo "$repo_name" "Failed to change directory"
        return 1
    }
    
    # Create and checkout new branch
    log_info "Creating branch: $BRANCH_NAME"
    if ! git checkout -b "$BRANCH_NAME" 2>&1 | grep -v "^Switched to"; then
        log_error "Failed to create branch $BRANCH_NAME"
        log_failed_repo "$repo_name" "Failed to create branch"
        cd - > /dev/null
        return 1
    fi
    
    # Perform replacements
    local replacement_status=0
    perform_replacements "$repo_path"
    replacement_status=$?
    
    if [ $replacement_status -eq 2 ]; then
        log_warning "Skipping commit for $repo_name (no changes made)"
        log_completed_repo "$repo_name" "" "no_changes"
        cd - > /dev/null
        return 0
    fi
    
    # Stage all changes
    log_info "Staging changes..."
    git add -A
    
    # Check if there are changes to commit
    if git diff --cached --quiet; then
        log_warning "No changes to commit for $repo_name"
        log_completed_repo "$repo_name" "" "no_changes"
        cd - > /dev/null
        return 0
    fi
    
    # Commit changes
    log_info "Creating commit..."
    if ! git commit -m "$COMMIT_MESSAGE" > /dev/null 2>&1; then
        log_error "Failed to commit changes"
        log_failed_repo "$repo_name" "Failed to commit changes"
        cd - > /dev/null
        return 1
    fi
    
    # Push to remote
    log_info "Pushing branch to remote..."
    if ! git push -u origin "$BRANCH_NAME" 2>&1 | grep -v "^To\|^remote:\|^branch"; then
        log_error "Failed to push branch to remote"
        log_failed_repo "$repo_name" "Failed to push to remote"
        cd - > /dev/null
        return 1
    fi
    
    # Create Pull Request if enabled
    local pr_url=""
    if [ "$CREATE_PR" = true ]; then
        pr_url=$(create_pull_request "$repo_name")
        if [ -z "$pr_url" ]; then
            log_warning "Failed to create PR for $repo_name, but changes were pushed successfully"
            log_completed_repo "$repo_name" "" "pushed"
        else
            log_completed_repo "$repo_name" "$pr_url" "success"
        fi
    else
        log_completed_repo "$repo_name" "" "pushed"
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
    
    # Set up Git authentication
    setup_git_auth
    
    # Initialize log file with header
    echo -e "Repository\tResult" > "$LOG_FILE"
    
    # Check if repo list file exists
    if [ ! -f "$REPO_LIST_FILE" ]; then
        log_error "Repo list file not found: $REPO_LIST_FILE"
        cleanup_git_auth
        exit 1
    fi
    
    # Create working directory
    mkdir -p "$WORK_DIR"
    
    # Read repo names and process each one
    local total_repos=0
    local successful_repos=0
    local failed_repos=0
    local skipped_repos=0
    
    while IFS= read -r repo_name || [ -n "$repo_name" ]; do
        # Skip empty lines and comments
        [[ -z "$repo_name" || "$repo_name" =~ ^# ]] && continue
        
        # Trim whitespace
        repo_name=$(echo "$repo_name" | xargs)
        
        total_repos=$((total_repos + 1))
        
        # Process repo and capture return code
        if process_repo "$repo_name"; then
            successful_repos=$((successful_repos + 1))
        else
            failed_repos=$((failed_repos + 1))
            log_warning "Continuing with next repository..."
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
    log_info ""
    log_info "Detailed log saved to: $LOG_FILE"
    
    # Clean up Git authentication
    cleanup_git_auth
    
    # Exit with error if any repos failed, but don't prevent completion
    if [ $failed_repos -gt 0 ]; then
        log_warning "Some repositories failed. Check the log file for details."
    fi
}

# Run main function
main
