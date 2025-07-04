#!/bin/bash

# FastTTS Backup Script (Portable Version)
# Usage: ./backup_fasttts.sh [type] [project_dir]
# Types: daily, weekly, major, emergency
# If project_dir not specified, auto-detects based on script location

BACKUP_TYPE=${1:-daily}
PROJECT_DIR=${2:-""}

# Auto-detect project directory
if [ -z "$PROJECT_DIR" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Check if script is in project root (contains main.py)
    if [ -f "$SCRIPT_DIR/main.py" ]; then
        PROJECT_DIR="$SCRIPT_DIR"
    # Check if script is in parent directory of FastTTS
    elif [ -f "$SCRIPT_DIR/FastTTS/main.py" ]; then
        PROJECT_DIR="$SCRIPT_DIR/FastTTS"
    # Use current working directory if it contains main.py
    elif [ -f "$(pwd)/main.py" ]; then
        PROJECT_DIR="$(pwd)"
    else
        echo "❌ Error: Cannot find FastTTS project directory"
        echo "   Place script in project root or specify: $0 $BACKUP_TYPE /path/to/FastTTS"
        exit 1
    fi
fi

SOURCE_DIR="$PROJECT_DIR"
BACKUP_BASE="$(dirname "$PROJECT_DIR")/FastTTS_Backups"
DATE=$(date +%Y-%m-%d)
WEEK=$(date +Week_%V_%Y)

# Create backup directories
mkdir -p "$BACKUP_BASE/Daily"
mkdir -p "$BACKUP_BASE/Weekly" 
mkdir -p "$BACKUP_BASE/Major_Versions"
mkdir -p "$BACKUP_BASE/Emergency"

case $BACKUP_TYPE in
    "daily")
        BACKUP_DIR="$BACKUP_BASE/Daily/${DATE}_FastTTS"
        echo "📅 Creating daily backup: $BACKUP_DIR"
        ;;
    "weekly")
        BACKUP_DIR="$BACKUP_BASE/Weekly/${WEEK}_FastTTS"
        echo "📅 Creating weekly backup: $BACKUP_DIR"
        ;;
    "major")
        read -p "Enter version name (e.g., v1.3_New_Feature): " VERSION_NAME
        BACKUP_DIR="$BACKUP_BASE/Major_Versions/$VERSION_NAME"
        echo "🚀 Creating major version backup: $BACKUP_DIR"
        ;;
    "emergency")
        BACKUP_DIR="$BACKUP_BASE/Emergency/Last_Known_Good"
        echo "🆘 Creating emergency backup: $BACKUP_DIR"
        ;;
esac

# Remove existing backup if it exists
if [ -d "$BACKUP_DIR" ]; then
    echo "🗑️ Removing existing backup..."
    rm -rf "$BACKUP_DIR"
fi

# Create the backup
echo "📦 Copying files..."
cp -r "$SOURCE_DIR" "$BACKUP_DIR"

# Remove unnecessary files from backup
echo "🧹 Cleaning backup..."
rm -rf "$BACKUP_DIR/venv"
rm -rf "$BACKUP_DIR/__pycache__"
rm -rf "$BACKUP_DIR"/*.pyc
rm -rf "$BACKUP_DIR"/.git

# Create backup info file
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
FastTTS Backup Information
=========================
Backup Type: $BACKUP_TYPE
Created: $(date)
Source: $SOURCE_DIR
Files: $(find "$BACKUP_DIR" -type f | wc -l)
Size: $(du -sh "$BACKUP_DIR" | cut -f1)

Notes:
- This backup excludes venv, __pycache__, and .git folders
- Sessions data is included in sessions/ folder
- To restore: copy contents back to $SOURCE_DIR
EOF

echo "✅ Backup completed: $BACKUP_DIR"
echo "📊 Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"

# Cleanup old daily backups (keep last 7 days)
if [ "$BACKUP_TYPE" = "daily" ]; then
    echo "🧹 Cleaning old daily backups..."
    find "$BACKUP_BASE/Daily" -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;
fi

# Cleanup old weekly backups (keep last 4 weeks)
if [ "$BACKUP_TYPE" = "weekly" ]; then
    echo "🧹 Cleaning old weekly backups..."
    find "$BACKUP_BASE/Weekly" -maxdepth 1 -type d -mtime +28 -exec rm -rf {} \;
fi