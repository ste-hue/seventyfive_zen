#!/bin/bash

# 75 Zen Installation Script - Interactive Version

echo "🧘 Installing 75 Zen CLI Tracker..."
echo ""
echo "Which version would you like to install?"
echo "1) Interactive mode (NEW! - just press numbers to check items)"
echo "2) Classic mode (original command-based interface)"
echo ""
read -p "Enter your choice (1 or 2): " choice

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Determine which script to use
if [ "$choice" = "1" ]; then
    SCRIPT_FILE="seventyfive_zen_interactive.py"
    echo "📱 Installing interactive version..."
else
    SCRIPT_FILE="seventyfive_zen.py"
    echo "📝 Installing classic version..."
fi

# Make the Python script executable
chmod +x "$SCRIPT_DIR/$SCRIPT_FILE"

# Create symlink in /usr/local/bin
if [ -w /usr/local/bin ]; then
    ln -sf "$SCRIPT_DIR/$SCRIPT_FILE" /usr/local/bin/75z
    echo "✅ Created symlink: /usr/local/bin/75z"
else
    echo "⚠️  Cannot write to /usr/local/bin. Trying with sudo..."
    sudo ln -sf "$SCRIPT_DIR/$SCRIPT_FILE" /usr/local/bin/75z
    echo "✅ Created symlink: /usr/local/bin/75z (with sudo)"
fi

# Alternative: Add alias to shell config
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    echo ""
    echo "Would you like to add an alias to your shell configuration? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "alias 75z='python3 $SCRIPT_DIR/$SCRIPT_FILE'" >> "$SHELL_RC"
        echo "✅ Added alias to $SHELL_RC"
        echo "   Run 'source $SHELL_RC' to use it immediately"
    fi
fi

# Create the .75zen directory
mkdir -p "$HOME/.75zen"
echo "✅ Created data directory: ~/.75zen"

echo ""
echo "🎉 Installation complete!"
echo ""

if [ "$choice" = "1" ]; then
    echo "Interactive Mode Usage:"
    echo "  75z                 # Start interactive mode"
    echo "  Press 1-7          # Toggle items on/off"
    echo "  Press 'r'          # Reset today"
    echo "  Press 'q'          # Quit"
    echo ""
    echo "You can still use classic commands:"
fi

echo "  75z check 4         # Mark item 4 as completed"
echo "  75z status          # Show current status (non-interactive)"
echo "  75z reset_day       # Clear and recreate today"
echo "  75z force_reset     # Manual streak reset"
echo ""
echo "Start your journey with: 75z"
