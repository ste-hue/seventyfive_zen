#!/bin/bash

# 75 Zen Installation Script

echo "🧘 Installing 75 Zen CLI Tracker..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Make the Python script executable
chmod +x "$SCRIPT_DIR/seventyfive_zen.py"

# Create symlink in /usr/local/bin
if [ -w /usr/local/bin ]; then
    ln -sf "$SCRIPT_DIR/seventyfive_zen.py" /usr/local/bin/75z
    echo "✅ Created symlink: /usr/local/bin/75z"
else
    echo "⚠️  Cannot write to /usr/local/bin. Trying with sudo..."
    sudo ln -sf "$SCRIPT_DIR/seventyfive_zen.py" /usr/local/bin/75z
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
        echo "alias 75z='python3 $SCRIPT_DIR/seventyfive_zen.py'" >> "$SHELL_RC"
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
echo "Usage:"
echo "  75z                 # Show checklist and streak"
echo "  75z check 4         # Mark item 4 as completed"
echo "  75z status          # Show current status + streak"
echo "  75z reset_day       # Clear and recreate today"
echo "  75z force_reset     # Manual streak reset"
echo ""
echo "Start your journey with: 75z"
