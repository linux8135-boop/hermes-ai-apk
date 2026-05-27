#!/data/data/com.termux/files/usr/bin/bash
# Hermes AI APK — one-time setup on phone
# Run this after installing the APK

echo "=== Hermes AI APK Setup ==="

# Ensure config dir
mkdir -p ~/.hermes

# Check if config already exists
if [ -f ~/.hermes/config.json ]; then
    echo "📋 Config already exists at ~/.hermes/config.json"
    cat ~/.hermes/config.json
    echo ""
    read -p "Overwrite? (y/N): " yn
    if [ "$yn" != "y" ]; then
        echo "Keeping existing config."
        exit 0
    fi
fi

# Gather config
echo ""
echo "Step 1: Create a Discord Bot"
echo "  Go to https://discord.com/developers/applications"
echo "  New Application → Bot → Reset Token → Copy"
echo ""
read -p "Discord Bot Token: " BOT_TOKEN

echo ""
echo "Step 2: Your Discord User ID"
echo "  Settings → Advanced → Developer Mode"
echo "  Right-click your name → Copy ID"
echo ""
read -p "Your Discord User ID: " USER_ID

echo ""
echo "Step 3: API Key (for LLM)"
echo "  Get one from https://opencode.ai (free tier works)"
echo ""
read -p "API Key: " API_KEY

# Write config
cat > ~/.hermes/config.json << EOF
{
  "bot_token": "$BOT_TOKEN",
  "api_key": "$API_KEY",
  "authorized_user": "$USER_ID",
  "api_url": "https://opencode.ai/zen/v1/chat/completions",
  "api_model": "deepseek-v4-flash-free"
}
EOF

echo ""
echo "✅ Config saved to ~/.hermes/config.json"
echo ""
echo "Now:"
echo "  1. Install the Hermes AI APK on your phone"
echo "  2. Open the app once (starts background service)"
echo "  3. Send a DM to your bot on Discord"
echo "  4. Type !status to verify"

# Generate invite link
if command -v python3 &>/dev/null; then
    INVITE_URL="https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=3072&scope=bot"
    echo ""
    echo "⚠️  To invite your bot to a server (optional):"
    echo "  $INVITE_URL"
    echo "  (Replace YOUR_CLIENT_ID with your bot's Application ID)"
fi

echo ""
echo "Done! 🚀"
