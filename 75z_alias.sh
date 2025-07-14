# 75 Zen CLI Tracker Alias
# Add this to your ~/.zshrc or ~/.bashrc

# Main alias for 75z command
alias 75z='python3 ~/Desktop/Projects/seventyfive_zen/seventyfive_zen.py'

# Quick shortcuts for common commands
alias 75zc='75z check'      # Quick check: 75zc 4
alias 75zs='75z status'     # Show status
alias 75zr='75z reset_day'  # Reset today

# Convenience functions
75z_complete_all() {
    echo "🎯 Marking all tasks as complete..."
    for i in {1..7}; do
        75z check $i
    done
    75z status
}

75z_morning() {
    echo "☀️ Good morning! Here's your daily checklist:"
    75z status
}

75z_evening() {
    echo "🌙 Evening check-in:"
    75z status
    echo ""
    echo "Remember: Complete all 7 to keep your streak!"
}

# Optional: Auto-show status when opening new terminal
# Uncomment the line below if you want to see your checklist on terminal start
# 75z status 2>/dev/null || true
