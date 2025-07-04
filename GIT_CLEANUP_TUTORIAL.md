# Git Repository Cleanup Tutorial for Beginners

## What We're Going to Learn

This tutorial teaches you how to clean up a messy Git repository by removing unwanted files and folders that shouldn't be tracked in version control.

## Why Clean Up Your Repository?

When you first start a project, you might accidentally commit files that shouldn't be shared:
- **Sensitive files**: API keys, passwords, environment variables
- **Generated files**: Compiled code, cache files, logs
- **IDE files**: Editor settings, temporary files
- **Personal files**: Screenshots, notes, backup files

## What You'll Need

- Git installed on your computer
- A messy repository (like the one we just cleaned)
- A text editor
- Basic command line knowledge

## Step 1: Understand What's in Your Repository

First, let's see what files Git is currently tracking:

```bash
git ls-files
```

This shows ALL files Git is tracking. Look for:
- Files starting with `.` (hidden files)
- Folders like `__pycache__`, `.vscode`, `.idea`
- Files with extensions like `.log`, `.tmp`, `.pyc`
- Personal files like screenshots, notes

## Step 2: Create a Proper .gitignore File

The `.gitignore` file tells Git which files to ignore. Create or edit `.gitignore`:

```bash
# Python generated files
__pycache__/
*.py[cod]
*.pyc
*.pyo
*.pyd

# Virtual environments
venv/
env/
ENV/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs and databases
*.log
*.db
*.sqlite

# Environment variables (IMPORTANT!)
.env
.env.local

# Personal files
*.bak
*.tmp
*.backup
notes.txt
todo.txt

# Screenshots and images (if not needed)
*.png
*.jpg
*.jpeg
*.gif

# Project specific (customize for your project)
sessions/
logs/
temp/
```

## Step 3: Remove Files from Git Tracking

⚠️ **IMPORTANT**: This doesn't delete files from your computer, only from Git tracking.

### Remove a Single File
```bash
git rm --cached filename.txt
```

### Remove a Folder
```bash
git rm -r --cached foldername/
```

### Remove Multiple Files with Pattern
```bash
git rm --cached *.log
git rm --cached *.pyc
```

### Common Cleanup Commands

```bash
# Remove Python cache files
git rm -r --cached __pycache__/
git rm --cached *.pyc

# Remove IDE files
git rm -r --cached .vscode/
git rm -r --cached .idea/

# Remove environment files
git rm --cached .env
git rm --cached .env.local

# Remove log files
git rm --cached *.log
git rm -r --cached logs/

# Remove database files
git rm --cached *.db
git rm --cached *.sqlite
```

## Step 4: Handle Sensitive Files

If you accidentally committed sensitive files (API keys, passwords):

1. **Remove from Git**:
```bash
git rm --cached .env
git rm --cached config/secrets.txt
```

2. **Add to .gitignore**:
```
.env
config/secrets.txt
```

3. **Consider changing the secrets** since they're in Git history

## Step 5: Commit Your Changes

After removing files and updating `.gitignore`:

```bash
# Add the .gitignore file
git add .gitignore

# Commit the cleanup
git commit -m "Clean up repository: remove unwanted files and add .gitignore

- Removed cache files and build artifacts
- Removed IDE and OS-specific files
- Removed sensitive environment files
- Added comprehensive .gitignore file
"
```

## Step 6: Push to Remote Repository

```bash
git push origin main
```

## Example: Full Cleanup Process

Let's say you have a messy Python project:

```bash
# 1. See what's tracked
git ls-files

# 2. Remove unwanted files
git rm -r --cached __pycache__/
git rm -r --cached .vscode/
git rm --cached .env
git rm --cached *.log
git rm -r --cached temp/

# 3. Create/update .gitignore
echo "__pycache__/" >> .gitignore
echo ".vscode/" >> .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
echo "temp/" >> .gitignore

# 4. Add .gitignore and commit
git add .gitignore
git commit -m "Clean up repository and add .gitignore"

# 5. Push changes
git push origin main
```

## Common Mistakes to Avoid

1. **Don't use `git rm` without `--cached`** - this deletes files from your computer
2. **Don't forget to update .gitignore** - files will be tracked again
3. **Don't commit sensitive files** - add them to .gitignore first
4. **Don't remove important files** - double-check what you're removing

## Advanced: Using find Command

Find all files of a certain type:
```bash
# Find all .pyc files
find . -name "*.pyc" -type f

# Find all __pycache__ directories
find . -name "__pycache__" -type d

# Remove all .pyc files from Git
find . -name "*.pyc" -type f -exec git rm --cached {} \;
```

## What We Accomplished

In our FastTTS cleanup, we removed:
- **89 unwanted files** total
- `.claude/` - Claude AI settings
- `.prompts/` - Prompt files
- `.vscode/` - VS Code settings  
- `__pycache__/` - Python cache directories
- `Technical_Information/` - Documentation folder
- `.env`, `.sesskey` - Sensitive files
- All `.pyc` files - Compiled Python files

## Verification

After cleanup, verify your repository:
```bash
# Check what files are still tracked
git ls-files

# Check repository size
git count-objects -vH

# Check what's ignored
git status --ignored
```

## Pro Tips

1. **Start with .gitignore** - Create it before committing anything
2. **Use templates** - GitHub provides .gitignore templates for different languages
3. **Regular cleanup** - Clean up your repository regularly
4. **Test locally** - Make sure your app still works after cleanup
5. **Backup first** - Create a backup branch before major cleanup

## Template .gitignore Files

### Python Projects
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.env
*.log
.pytest_cache/
.coverage
```

### Node.js Projects
```
node_modules/
npm-debug.log*
.env
.env.local
.DS_Store
*.log
dist/
build/
```

### General Purpose
```
# OS files
.DS_Store
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Environment variables
.env
.env.local

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
*.bak
```

## When to Clean Up

- **Before first public commit** - Clean up before sharing
- **After major development** - Remove accumulated junk
- **Before releases** - Clean repository for stable releases
- **When repository is too large** - Remove unnecessary files

## Summary

Repository cleanup involves:
1. **Identify** unwanted files
2. **Create/update** .gitignore
3. **Remove** files from Git tracking
4. **Commit** the cleanup
5. **Push** to remote

Remember: This process removes files from Git history on new commits, but they remain in previous commits. For completely removing sensitive data from Git history, you'd need more advanced tools like `git filter-branch` or `BFG Repo-Cleaner`.

Happy coding! 🚀