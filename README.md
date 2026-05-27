# Hermes AI — Standalone Android APK

Discord-controlled AI assistant for Android. No Termux required.

## Features

- **Standalone APK** — install like any Android app
- **Discord Gateway** — control via DM
- **LLM-powered** — uses opencode-zen or any OpenAI-compatible API
- **Foreground service** — persistent notification, survives app close
- **Shell access** — run commands on the device (!shell)
- **Boot autostart** — starts on phone boot (RECEIVE_BOOT_COMPLETED)

## Commands (Discord DM)

| Command | Description |
|---------|-------------|
| `!ask <prompt>` | Ask the AI anything |
| `!chat <msg>` | Multi-turn conversation |
| `!config key <key>` | Set API key |
| `!config model <name>` | Set model name |
| `!config url <url>` | Set API endpoint |
| `!status` | Show gateway status |
| `!shell <cmd>` | Run shell command on phone |
| `!reset` | Clear chat history |
| `!debug` | Show debug log |
| `!help` | This help |

## Build from source

### GitHub Actions (recommended)

1. Fork/push this repo to GitHub
2. Go to **Settings → Secrets and variables → Actions**
3. Add secrets (optional, for build-time injection):
   - `DISCORD_BOT_TOKEN`
   - `DISCORD_AUTHORIZED_USER`
4. Go to **Actions → Build Hermes APK → Run workflow**
5. Download APK from artifacts

### Local build (Linux)

```bash
sudo apt install git zip unzip openjdk-17-jdk autoconf automake libtool \
  pkg-config zlib1g-dev libffi-dev libssl-dev python3-dev ccache cmake make patchelf

pip install buildozer cython
buildozer android debug
```

APK will be in `bin/`.

## Setup after install

1. Install the APK on your Android device
2. Open the app once (starts the background service)
3. Send a DM to your bot from Discord
4. Configure via DM:
   ```
   !config key YOUR_API_KEY
   !status
   ```

Or pre-configure at build time by adding `config.py`:
```python
BOT_TOKEN = "your_discord_bot_token"
AUTHORIZED_USER = "your_discord_user_id"
API_KEY = "your_llm_api_key"
```

## Architecture

```
┌──────────────┐     Discord DM     ┌──────────────────┐
│  Discord Bot  │◄─────────────────►│     You (user)    │
│  (gateway.py)  │                   └──────────────────┘
└──────┬───────┘
       │ REST API + WebSocket
┌──────▼───────┐
│  LLM Bridge   │──► opencode-zen / OpenAI API
│  (gateway.py) │──► !shell → subprocess (Android)
└──────────────┘
       │
┌──────▼───────┐
│  Foreground   │──► Notification, boot autostart
│  Service      │
└──────────────┘
```
