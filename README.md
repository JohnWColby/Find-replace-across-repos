Pull Request Creation Setup Guide
This guide explains how to set up automatic PR creation for the batch repo update script.
Quick Start
Set your platform in the script:
GIT_PLATFORM="github"  # or "gitlab" or "bitbucket"
Enable PR creation:
CREATE_PR=true
Set your access token (choose one method):
Method A: Environment Variable (Recommended)
export GIT_TOKEN="your_token_here"
./repo_batch_update.sh
Method B: In Script (Less Secure)
# Edit the script and set:
GIT_TOKEN="your_token_here"
Creating Access Tokens
GitHub Personal Access Token
Go to https://github.com/settings/tokens
Click "Generate new token" → "Generate new token (classic)"
Give it a name (e.g., "Batch PR Creation")
Select scopes:
✅ repo (full control of private repositories)
Click "Generate token"
Copy the token immediately (you won't see it again!)
Token format: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GitLab Personal Access Token
Go to https://gitlab.com/-/profile/personal_access_tokens
Enter a name (e.g., "Batch MR Creation")
Select scopes:
✅ api (full API access)
Click "Create personal access token"
Copy the token
Token format: glpat-xxxxxxxxxxxxxxxxxxxx
Bitbucket App Password
Go to https://bitbucket.org/account/settings/app-passwords/
Click "Create app password"
Enter a label (e.g., "Batch PR Creation")
Select permissions:
✅ Pull requests: Write
✅ Repositories: Write
Click "Create"
Copy the password
Format: username:app_password
For Bitbucket, set your token as:
export GIT_TOKEN="your_username:your_app_password"
Configuration Examples
GitHub Example
GIT_PLATFORM="github"
GIT_BASE_URL="https://github.com/mycompany"
CREATE_PR=true
PR_TITLE="Update deprecated API calls"
PR_BASE_BRANCH="main"

export GIT_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
./repo_batch_update.sh
GitLab Example
GIT_PLATFORM="gitlab"
GIT_BASE_URL="https://gitlab.com/mycompany"
CREATE_PR=true
PR_TITLE="Update configuration values"
PR_BASE_BRANCH="main"

export GIT_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
./repo_batch_update.sh
Bitbucket Example
GIT_PLATFORM="bitbucket"
GIT_BASE_URL="https://bitbucket.org/mycompany"
CREATE_PR=true
PR_TITLE="Modernize function names"
PR_BASE_BRANCH="master"

export GIT_TOKEN="myusername:app_password_here"
./repo_batch_update.sh
Security Best Practices
Never commit tokens to git
Add this to your .gitignore:
.env
*token*
Use environment variables
Store token in .env file:
# .env file
export GIT_TOKEN="your_token_here"
Source it before running:
source .env
./repo_batch_update.sh
Use secret management in CI/CD
GitHub Actions: Use secrets
GitLab CI: Use CI/CD variables
Jenkins: Use credentials plugin
Rotate tokens regularly
Set expiration dates on tokens
Generate new tokens periodically
PR Customization
You can customize your PR with:
PR_TITLE="Your PR Title"

PR_DESCRIPTION="Detailed description here

## Changes:
- Item 1
- Item 2

## Testing:
- [ ] Tests pass
- [ ] Manual testing done

Closes #123"

PR_BASE_BRANCH="develop"  # Change target branch
Troubleshooting
"Failed to create PR: Bad credentials"
Check that your token is correct
Verify token hasn't expired
Ensure token has correct permissions
"Failed to create PR: Validation Failed"
PR may already exist for this branch
Base branch may not exist
Check that branch was pushed successfully
"GIT_TOKEN not set. Skipping PR creation."
Set the environment variable:
export GIT_TOKEN="your_token"
Or update the script directly (less secure)
PR created but with formatting issues
Escape special characters in PR title/description
For multi-line descriptions, ensure proper formatting
Running Without PR Creation
If you just want to push branches without creating PRs:
CREATE_PR=false
The script will push branches, and you can create PRs manually later.
