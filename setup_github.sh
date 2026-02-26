#!/bin/bash

# GitHub Repository Setup Script for Solar of Things Integration
# This script will create a GitHub repository and push your integration

echo "=================================================="
echo "Solar of Things HA Integration - GitHub Setup"
echo "=================================================="
echo ""

# Configuration
REPO_NAME="solar-of-things-ha"
GITHUB_USERNAME="conexocasa"
GITHUB_EMAIL="bob@conexo.casa"

echo "Repository Name: $REPO_NAME"
echo "GitHub Username: $GITHUB_USERNAME"
echo "GitHub Email: $GITHUB_EMAIL"
echo ""

# Check if we're in the right directory
if [ ! -f "manifest.json" ]; then
    echo "Error: Please run this script from the solar_of_things_integration directory"
    exit 1
fi

# Check if git is configured
if [ "$(git config user.email)" != "$GITHUB_EMAIL" ]; then
    echo "Configuring git..."
    git config --global user.email "$GITHUB_EMAIL"
    git config --global user.name "$GITHUB_USERNAME"
fi

# Rename master to main (GitHub's default)
echo "Renaming branch to main..."
git branch -M main

echo ""
echo "=================================================="
echo "STEP 1: Create GitHub Personal Access Token"
echo "=================================================="
echo ""
echo "1. Go to: https://github.com/settings/tokens/new"
echo "2. Token name: 'Solar of Things Integration'"
echo "3. Expiration: Choose your preference"
echo "4. Select scopes:"
echo "   ☑ repo (all repo permissions)"
echo "5. Click 'Generate token'"
echo "6. COPY THE TOKEN (you won't see it again!)"
echo ""
echo -n "Paste your GitHub Personal Access Token here: "
read -s GITHUB_TOKEN
echo ""
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: Token is required!"
    exit 1
fi

echo "=================================================="
echo "STEP 2: Create GitHub Repository"
echo "=================================================="
echo ""

# Create repository using GitHub API
echo "Creating repository on GitHub..."
RESPONSE=$(curl -s -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{
        \"name\":\"$REPO_NAME\",
        \"description\":\"Home Assistant integration for Solar of Things (Siseli) solar inverter systems with full monitoring and control capabilities\",
        \"homepage\":\"https://github.com/$GITHUB_USERNAME/$REPO_NAME\",
        \"private\":false,
        \"has_issues\":true,
        \"has_projects\":false,
        \"has_wiki\":false
    }")

# Check if repository was created successfully
if echo "$RESPONSE" | grep -q "\"full_name\""; then
    echo "✓ Repository created successfully!"
    REPO_URL=$(echo "$RESPONSE" | grep -o '"clone_url":"[^"]*"' | cut -d'"' -f4)
    echo "  Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
else
    if echo "$RESPONSE" | grep -q "already exists"; then
        echo "⚠ Repository already exists. Using existing repository."
        REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    else
        echo "✗ Error creating repository:"
        echo "$RESPONSE" | grep -o '"message":"[^"]*"' | cut -d'"' -f4
        exit 1
    fi
fi

echo ""
echo "=================================================="
echo "STEP 3: Push to GitHub"
echo "=================================================="
echo ""

# Add remote with token authentication
REPO_URL_WITH_TOKEN="https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo "Adding remote origin..."
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL_WITH_TOKEN"

echo "Pushing to GitHub..."
if git push -u origin main; then
    echo "✓ Successfully pushed to GitHub!"
else
    echo "✗ Error pushing to GitHub"
    exit 1
fi

echo ""
echo "=================================================="
echo "STEP 4: Create Release Tag"
echo "=================================================="
echo ""

echo "Creating v2.0.0 tag..."
git tag -a v2.0.0 -m "Version 2.0.0 - Full Control Features

Major release with complete control capabilities:
- 8 new control entities (Number, Select, Switch)
- Battery charge/discharge limits
- Operating mode selection
- Grid charging control
- Comprehensive documentation
- 15+ automation examples"

echo "Pushing tag to GitHub..."
git push origin v2.0.0

echo ""
echo "=================================================="
echo "SUCCESS! Repository Created"
echo "=================================================="
echo ""
echo "Your repository is now available at:"
echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "Next steps:"
echo "1. Visit your repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "2. Edit the README if needed"
echo "3. Add topics: homeassistant, solar, siseli, home-automation"
echo "4. Submit to HACS (optional)"
echo ""
echo "To add to HACS default repository:"
echo "1. Fork: https://github.com/hacs/default"
echo "2. Add your repo to integration list"
echo "3. Create pull request"
echo ""
echo "Repository details:"
echo "- Name: $REPO_NAME"
echo "- Version: 2.0.0"
echo "- Branch: main"
echo "- Files: 23 files committed"
echo ""

# Clean up token from git config (security)
git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo "✓ Setup complete!"
