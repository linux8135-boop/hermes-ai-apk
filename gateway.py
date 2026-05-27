"""Hermes AI — Discord bot gateway.
Minimal Discord client using raw WebSocket + REST API.
No discord.py dependency needed — pure stdlib + websockets + requests."""
import asyncio
import json
import os
import sys
import struct
import time
import traceback
import urllib.request
from pathlib import Path

# --- Config ---
CONFIG_DIR = str(Path.home() / ".hermes")
CONFIG_PATH = CONFIG_DIR + "/config.json"
DEBUG_LOG = str(Path.home() / "hermes_debug.log")

BOT_TOKEN = None
API_KEY = None
API_URL = "https://opencode.ai/zen/v1/chat/completions"
API_MODEL = "deepseek-v4-flash-free"
AUTHORIZED_USER = None
REST_API = "https://discord.com/api/v10"

# --- Build-time config injection ---
try:
    import config as _cfg
    BOT_TOKEN = getattr(_cfg, "BOT_TOKEN", BOT_TOKEN)
    API_KEY = getattr(_cfg, "API_KEY", API_KEY)
    AUTHORIZED_USER = getattr(_cfg, "AUTHORIZED_USER", AUTHORIZED_USER)
except ImportError:
    pass

# --- Logging ---
def debug(msg):
    try:
        with open(DEBUG_LOG, "a") as f:
            f.write(f"{msg}\n")
    except:
        pass

# --- Config persistence ---
def ensure_cfg_dir():
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)

def load_config():
    global BOT_TOKEN, API_KEY, AUTHORIZED_USER
    try:
        p = Path(CONFIG_PATH)
        if p.exists():
            cfg = json.loads(p.read_text())
            BOT_TOKEN = cfg.get("bot_token", BOT_TOKEN)
            API_KEY = cfg.get("api_key", "")
            AUTHORIZED_USER = cfg.get("authorized_user", "")
            return True
    except:
        pass
    return False

def save_config(bot_token, api_key="", authorized_user=""):
    ensure_cfg_dir()
    cfg = {"bot_token": bot_token, "api_key": api_key, "authorized_user": authorized_user, "api_url": API_URL, "api_model": API_MODEL}
    Path(CONFIG_PATH).write_text(json.dumps(cfg, indent=2))
    return True

# --- Discord REST API ---
def discord_headers():
    return {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}

def discord_send(channel_id, content):
    """Send a message to a Discord channel via REST."""
    url = f"{REST_API}/channels/{channel_id}/messages"
    payload = json.dumps({"content": content[:1900]}).encode()
    req = urllib.request.Request(url, data=payload, headers=discord_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        debug(f"Discord send error {e.code}: {e.read().decode()[:200]}")
        return None

def discord_get_me():
    """Get bot user info."""
    req = urllib.request.Request(f"{REST_API}/users/@me", headers=discord_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except:
        return None

# --- LLM call ---
def ask_llm(messages):
    if not API_KEY:
        return "❌ No API key. Set: `!config key YOUR_KEY`"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    payload = json.dumps({"model": API_MODEL, "messages": messages, "max_tokens": 2048}).encode()
    try:
        req = urllib.request.Request(API_URL, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        return f"❌ API {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return f"❌ Error: {e}"

# --- Command handler ---
async def handle_cmd(cmd, args, channel_id):
    global API_KEY, API_MODEL, API_URL

    if cmd == "help":
        return (
            "**Hermes AI — Commands:**\n"
            "`!ask <prompt>` — Ask AI anything\n"
            "`!chat <msg>` — Continue conversation\n"
            "`!config key <key>` — Set API key\n"
            "`!config model <name>` — Set model name\n"
            "`!config url <url>` — Set API endpoint\n"
            "`!status` — Gateway status\n"
            "`!reset` — Clear chat history\n"
            "`!shell <cmd>` — Run shell command\n"
            "`!debug` — Last 20 debug lines"
        )

    if cmd == "ask":
        if not args:
            return "Usage: `!ask <question>`"
        discord_send(channel_id, "⏳ Thinking...")
        msgs = [{"role": "system", "content": "You are Hermes AI, a helpful coding assistant on Android. Be concise."}, {"role": "user", "content": args}]
        return ask_llm(msgs)

    if cmd == "chat":
        if not hasattr(handle_cmd, "hist"):
            handle_cmd.hist = []
        if not args:
            return "Usage: `!chat <msg>`"
        handle_cmd.hist.append({"role": "user", "content": args})
        msgs = [{"role": "system", "content": "You are Hermes AI, a helpful coding assistant on Android."}] + handle_cmd.hist[-20:]
        discord_send(channel_id, "⏳ Thinking...")
        reply = ask_llm(msgs)
        handle_cmd.hist.append({"role": "assistant", "content": reply})
        return reply

    if cmd == "reset":
        handle_cmd.hist = []
        return "✅ Reset."

    if cmd == "config":
        sub = args.split(maxsplit=1)
        if not sub:
            return f"Model: `{API_MODEL}` | URL: `{API_URL}` | Key: {'✅' if API_KEY else '❌'}"
        k, v = sub[0], sub[1] if len(sub) > 1 else ""
        if k == "key" and v:
            API_KEY = v
            save_config(BOT_TOKEN, API_KEY, AUTHORIZED_USER)
            return "✅ API key saved."
        if k == "model" and v:
            API_MODEL = v
            return f"✅ Model = `{API_MODEL}`"
        if k == "url" and v:
            API_URL = v
            return f"✅ URL = `{API_URL}`"
        return f"Model: `{API_MODEL}` | URL: `{API_URL}`"

    if cmd == "status":
        return f"**Hermes AI**\n├ Model: `{API_MODEL}`\n├ URL: `{API_URL}`\n├ Key: {'✅' if API_KEY else '❌'}\n└ Auth: {'✅' if AUTHORIZED_USER else '❌'}"

    if cmd == "shell":
        if not args:
            return "Usage: `!shell <cmd>`"
        try:
            import subprocess
            r = subprocess.run(args, shell=True, capture_output=True, text=True, timeout=30)
            out = r.stdout.strip()[:1500]
            err = r.stderr.strip()[:500]
            reply = f"```\n{out or '(no output)'}\n```"
            if err:
                reply += f"\n⚠️```\n{err}\n```"
            return reply
        except subprocess.TimeoutExpired:
            return "⏰ Timed out."
        except Exception as e:
            return f"❌ {e}"

    if cmd == "debug":
        try:
            log = Path(DEBUG_LOG)
            if log.exists():
                return f"```\n{chr(10).join(log.read_text().splitlines()[-20:])}\n```"
            return "No log."
        except:
            return "Can't read log."

    return "❌ Unknown. Try `!help`"

# --- WebSocket Discord client ---
class DiscordBot:
    def __init__(self):
        self.ws = None
        self.heartbeat_interval = 41250
        self.heartbeat_task = None
        self.seq = None
        self.bot_id = None
        self.bot_name = None
        self._running = True
        self._ready = False

    async def connect(self):
        import websockets
        self.ws = await websockets.connect("wss://gateway.discord.gg/?v=10&encoding=json")
        # Wait for Hello
        data = json.loads(await self.ws.recv())
        if data.get("op") == 10:  # Hello
            self.heartbeat_interval = data["d"]["heartbeat_interval"] / 1000

        # Identify
        payload = {
            "op": 2,
            "d": {
                "token": BOT_TOKEN,
                "properties": {"os": "android", "browser": "hermes", "device": "hermes-ai"},
                "intents": 1 << 15,  # MESSAGE_CONTENT
            }
        }
        await self.ws.send(json.dumps(payload))

        # Wait for Ready
        while True:
            data = json.loads(await self.ws.recv())
            if data.get("op") == 0 and data.get("t") == "READY":
                self.bot_id = int(data["d"]["user"]["id"])
                self.bot_name = data["d"]["user"]["username"]
                self.seq = data.get("s")
                self._ready = True
                debug(f"Bot online: {self.bot_name} ({self.bot_id})")
                break
            elif data.get("op") == 0:
                self.seq = data.get("s")

    async def heartbeat_loop(self):
        while self._running:
            await asyncio.sleep(self.heartbeat_interval)
            if self.ws:
                try:
                    await self.ws.send(json.dumps({"op": 1, "d": self.seq}))
                except:
                    break

    async def recv_loop(self):
        while self._running:
            try:
                data = json.loads(await self.ws.recv())
            except:
                break

            op = data.get("op")

            if op == 0:  # Dispatch
                self.seq = data.get("s")
                t = data.get("t")

                if t == "MESSAGE_CREATE":
                    msg = data["d"]
                    await self.handle_message(msg)

                elif t == "HEARTBEAT_ACK":
                    pass  # heartbeat confirmed

            elif op == 7:  # Reconnect
                debug("Discord requested reconnect")
                break

            elif op == 9:  # Invalid Session
                debug("Invalid session, reconnecting...")
                break

    async def handle_message(self, msg):
        if msg["author"]["id"] == str(self.bot_id):
            return
        if msg["channel_id"] is None:  # DM check
            return
        # Check if it's a DM (channel type 1)
        content = msg.get("content", "")
        if not content.startswith("!"):
            return

        # Get channel info to confirm DM
        try:
            req = urllib.request.Request(f"{REST_API}/channels/{msg['channel_id']}", headers=discord_headers())
            with urllib.request.urlopen(req, timeout=5) as r:
                ch = json.loads(r.read())
            if ch.get("type") != 1:  # DM = type 1
                return
        except:
            return

        # Check authorization
        if str(msg["author"]["id"]) != AUTHORIZED_USER:
            discord_send(msg["channel_id"], "⛔ Unauthorized")
            return

        # Parse command
        parts = content.strip().split()
        cmd = parts[0][1:].lower()
        args = " ".join(parts[1:])

        debug(f"CMD: !{cmd} from {msg['author']['id']}")

        try:
            result = await handle_cmd(cmd, args, msg["channel_id"])
            if result:
                discord_send(msg["channel_id"], result)
        except Exception as e:
            debug(traceback.format_exc())
            discord_send(msg["channel_id"], f"❌ {e}")

    async def start(self):
        import websockets
        while self._running:
            try:
                self._ready = False
                await self.connect()
                debug("Connected to Discord gateway")
                # Start heartbeat
                self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                # Receive messages
                await self.recv_loop()
            except Exception as e:
                debug(f"Gateway error: {e}")
            finally:
                if self.heartbeat_task:
                    self.heartbeat_task.cancel()
                    self.heartbeat_task = None
                if self.ws:
                    try:
                        await self.ws.close()
                    except:
                        pass
                    self.ws = None
                debug("Reconnecting in 5s...")
                await asyncio.sleep(5)

    def stop(self):
        self._running = False

# --- Entry point ---
async def start():
    load_config()
    if not BOT_TOKEN:
        debug("No bot token configured")
        return
    # Test REST connection
    me = discord_get_me()
    if me:
        debug(f"REST OK: {me.get('username')}")
    else:
        debug("REST connection failed - check token")
        return
    bot = DiscordBot()
    await bot.start()

# --- CLI setup helper ---
def setup_cli():
    """Run from terminal to configure the bot."""
    print("=== Hermes AI APK — Setup ===")
    bt = input("Discord Bot Token: ").strip()
    uid = input("Authorized Discord User ID: ").strip()
    key = input("API Key (opencode-zen or similar): ").strip()
    if bt:
        save_config(bt, key, uid)
        print("✅ Saved to ~/.hermes/config.json")
    else:
        print("Token required")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_cli()
    else:
        asyncio.run(start())
