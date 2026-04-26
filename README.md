# Claude Code Router

<div align="center">

<h3>🚀 Transparent Proxy for Claude Code</h3>

<p>Route Claude Code to <strong>DeepSeek V4 Pro</strong> or <strong>DeepSeek V4 Flash</strong> when Claude rate limits hit.</p>

<br>

<img src="https://img.shields.io/badge/🔧_DIY_Solution-black?style=for-the-badge" alt="DIY Solution">&nbsp;
<img src="https://img.shields.io/badge/🐍_Python_FastAPI-blue?style=for-the-badge" alt="Python FastAPI">&nbsp;
<img src="https://img.shields.io/badge/💰_Cost_Saving-purple?style=for-the-badge" alt="Cost Saving">&nbsp;
<img src="https://img.shields.io/badge/⚡_Transparent-green?style=for-the-badge" alt="Transparent">

![Python](https://img.shields.io/badge/python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)

</div>

> **Note**: A personal proxy for developers needing an alternative AI provider when Claude Code faces rate limits.

> ⚠️ **DeepSeek V4 (April 2026)**: `deepseek-chat` and `deepseek-reasoner` are deprecated on **2026-07-24** — they now auto-map to `deepseek-v4-flash`. This repo uses `deepseek-v4-pro` and `deepseek-v4-flash` directly.

## Quick Summary

**What**: A transparent proxy that routes Claude Code requests to DeepSeek V4 Pro or DeepSeek V4 Flash  
**Why**: Avoid Claude Pro rate limits — save up to 97% on token costs  
**How**: Local FastAPI server converts Claude API format to OpenAI format  
**When**: `use-deepseek` when Claude limits hit → `use-claude` to switch back

## 🚀 Quick Start

```bash
# 1. Clone and setup
cd ~/Documents/claude-code-router
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env: add your DEEPSEEK_API_KEY from platform.deepseek.com

# 3. Install shell functions
source .zshrc.router

# 4. Switch to DeepSeek V4 (when Claude limits hit)
use-deepseek
# → Claude Sonnet/Opus  maps to  deepseek-v4-pro
# → Claude Haiku        maps to  deepseek-v4-flash

# 5. Use Claude Code normally
cd ~/your-project
claude
```

```
Claude Code ──► localhost:8082 ──► deepseek-v4-pro   (Sonnet/Opus tasks)
                 ai_router.py  └──► deepseek-v4-flash  (Haiku tasks)
```

## Why This Project Exists

### The Problem
Claude Code users face:
- **Rate limits** even with Max subscription
- **Account locks** and phone verification issues
- **High costs** at scale — $140–$234/month for 18M tokens
- **Single provider** (only Claude models)

### When to Use This Project
- ✅ **You want a DeepSeek-only, minimal proxy** — no bloat
- ✅ **You already have a DeepSeek API key**
- ✅ **You want a simple, transparent proxy** without complex features
- ✅ **You're comfortable with Python** and command line setup

---

## Project Structure

```
claude-code-router/
├── ai_router.py        # Main FastAPI proxy server
├── .zshrc.router       # Shell functions (use-deepseek, use-claude, etc.)
├── .env.example        # Template for API keys (safe to commit)
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
├── QUICKSTART.txt      # Quick reference guide
└── venv/               # Python virtual environment (git-ignored)
```

---

## Prerequisites

- macOS with Python 3.10+
- Claude Code installed (`npm install -g @anthropic-ai/claude-code`)
- A DeepSeek API key → [platform.deepseek.com](https://platform.deepseek.com)

---

## Installation (One Time)

### 1. Navigate to the project

```bash
cd ~/Documents/claude-code-router
```

### 2. Create virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your API key

```bash
cp .env.example .env
open -a "Visual Studio Code" .env
```

Fill in your real key:

```env
AI_PROVIDER=deepseek
ROUTER_PORT=8082

DEEPSEEK_API_KEY=sk-your-real-key-here
DEEPSEEK_BIG_MODEL=deepseek-v4-pro      # Sonnet/Opus → Pro
DEEPSEEK_SMALL_MODEL=deepseek-v4-flash  # Haiku → Flash
```

### 4. Wire the shell functions (one time only)

```bash
grep -v "claude-code-router\|Claude Code Router" ~/.zshrc > /tmp/zshrc_clean
echo '' >> /tmp/zshrc_clean
echo '# Claude Code Router' >> /tmp/zshrc_clean
echo '[ -f ~/Documents/claude-code-router/.zshrc.router ] && source ~/Documents/claude-code-router/.zshrc.router' >> /tmp/zshrc_clean
mv /tmp/zshrc_clean ~/.zshrc
source ~/.zshrc
```

### 5. Verify installation

```bash
type use-deepseek
# Expected: use-deepseek is a shell function
```

---

## Daily Usage

### Hit your Claude Pro limit? Switch to DeepSeek V4:

```bash
use-deepseek
```

### Claude limits reset? Go back:

```bash
use-claude
```

### Check which mode you are currently in:

```bash
claude-mode
```

### Then just use Claude Code normally:

```bash
cd ~/your-project
claude
```

---

## Switching Between V4 Flash and V4 Pro

The proxy maps Claude model names to DeepSeek models automatically:

| Claude Model | DeepSeek Model | Variable |
|---|---|---|
| Sonnet, Opus | `DEEPSEEK_BIG_MODEL` | `deepseek-v4-pro` (default) |
| Haiku | `DEEPSEEK_SMALL_MODEL` | `deepseek-v4-flash` (default) |

**Option 1 — Permanent (edit `.env`):**
```env
DEEPSEEK_BIG_MODEL=deepseek-v4-flash    # force Flash for all heavy tasks
DEEPSEEK_BIG_MODEL=deepseek-v4-pro      # force Pro for all heavy tasks
```

**Option 2 — Session override (no file edit):**
```bash
# Flash only for this session:
DEEPSEEK_BIG_MODEL=deepseek-v4-flash use-deepseek

# Pro everywhere for this session:
DEEPSEEK_BIG_MODEL=deepseek-v4-pro DEEPSEEK_SMALL_MODEL=deepseek-v4-pro use-deepseek
```

**Option 3 — Swap mid-session (inside Claude Code terminal):**
```bash
export DEEPSEEK_BIG_MODEL=deepseek-v4-flash
router-stop && router-start
```

---

## Verification Commands

```bash
# Check the proxy is running (no external call)
router-status
# Expected: {"status": "ok", "provider": "deepseek", "key_set": true, ...}

# Send a live test message to DeepSeek
router-ping
# Expected: {"status": "ok", "provider": "deepseek", "reply": "PONG"}

# Watch live proxy logs
router-logs
```

---

## Shutdown / End of Session

```bash
use-claude      # stop proxy, restore direct Anthropic connection
deactivate      # exit virtual environment
```

---

## DeepSeek V4 Pricing (Official, April 2026)

| Model | Input (cache miss) | Input (cache hit) | Output |
|---|---|---|---|
| `deepseek-v4-flash` | $0.14 / 1M | $0.028 / 1M | $0.28 / 1M |
| `deepseek-v4-pro` | $1.74 / 1M | $0.145 / 1M | $3.48 / 1M |

Both models carry a **1M-token context window** and up to **384K output tokens**.
Cache hits (repeated context) cut input costs by **80–90%** — highly relevant for long Claude Code sessions.

> `deepseek-chat` → deprecated 2026-07-24, auto-maps to `deepseek-v4-flash`

---

## Cost at 18M Tokens/Month (Vibe Coding Estimate)

Assuming a typical **60% input / 40% output** split across 18M tokens:

| Model | Monthly Cost | vs Claude Sonnet |
|---|---|---|
| **DeepSeek V4 Flash** | **~$3.53** | **97% cheaper** |
| **DeepSeek V4 Pro** | **~$43.85** | **69% cheaper** |
| Claude Haiku 4.5 | ~$46.80 | baseline cheap |
| Claude Sonnet 4.6 | ~$140.40 | — |
| Claude Opus 4.6 | ~$234.00 | 67% more expensive |

> At 18M tokens/month, **V4 Flash costs under $4**. V4 Pro costs under $45 — still cheaper than Haiku.

---

## How It Works

### High-Level Flow
1. `use-deepseek` starts proxy and sets `ANTHROPIC_BASE_URL=http://localhost:8082`
2. Claude Code sends requests to local proxy instead of Anthropic
3. Proxy converts Claude format → OpenAI format → DeepSeek
4. Responses converted back to Claude format
5. `use-claude` stops proxy and restores direct Anthropic connection

### Technical Flow
- **Request interception**: `http://localhost:8082/v1/messages`
- **Format conversion**: `conv_messages()` and `conv_tools()` functions
- **Model mapping**: `pick_model()` selects big/small based on Claude model name
- **Streaming support**: `stream_oai_to_claude()` converts real-time events
- **Shell integration**: `.zshrc.router` manages lifecycle and state

---

## Troubleshooting

### `use-deepseek: command not found`
```bash
source ~/Documents/claude-code-router/.zshrc.router
```

### `router-status` fails (connection refused)
```bash
router-start
```

### `router-ping` returns 401
Your `DEEPSEEK_API_KEY` in `.env` is wrong or expired. Check [platform.deepseek.com](https://platform.deepseek.com).

### Claude Code shows auth conflict warning
```bash
claude /logout
# When prompted to log in again → No
```

### `max_tokens` error from DeepSeek
Already handled — `max_tokens` is automatically capped at 8192 in `ai_router.py`.

### Port 8082 already in use
```bash
lsof -ti:8082 | xargs kill -9
```

### Shell functions not available in new terminal
```bash
source ~/Documents/claude-code-router/.zshrc.router
```

---

## Requirements

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

---

## Security Considerations

- **Never commit `.env`** — contains your API key
- **Local proxy only** on `127.0.0.1:8082` — no external exposure
- **No conversation logging** — only operational logs in `router.log`

---

## License

MIT — use freely, modify freely.

## Acknowledgments

- **Claude Code** for the excellent CLI tool
- **DeepSeek** for V4 Pro and V4 Flash APIs
- **FastAPI** and **httpx** for the robust Python web stack
