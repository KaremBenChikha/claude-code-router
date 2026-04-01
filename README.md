# Claude Code Router

<div align="center">

<h3>🚀 Transparent Proxy for Claude Code</h3>

<p>Route Claude Code to <strong>DeepSeek V3</strong> or <strong>DeepSeek V3 via NVIDIA</strong> when Claude rate limits hit.</p>

<br>

<img src="https://img.shields.io/badge/🔧_DIY_Solution-black?style=for-the-badge" alt="DIY Solution">&nbsp;
<img src="https://img.shields.io/badge/🐍_Python_FastAPI-blue?style=for-the-badge" alt="Python FastAPI">&nbsp;
<img src="https://img.shields.io/badge/🔄_2_Providers-yellow?style=for-the-badge" alt="2 Providers">&nbsp;
<img src="https://img.shields.io/badge/💰_Cost_Saving-purple?style=for-the-badge" alt="Cost Saving">&nbsp;
<img src="https://img.shields.io/badge/⚡_Transparent-green?style=for-the-badge" alt="Transparent">

![Python](https://img.shields.io/badge/python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)

</div>

> **Note**: A personal proxy for developers needing alternative AI providers when Claude Code faces rate limits.

## Quick Summary

**What**: A transparent proxy that routes Claude Code requests to DeepSeek V3 or DeepSeek V3 via NVIDIA
**Why**: Avoid Claude Pro rate limits and reduce costs
**How**: Local FastAPI server converts Claude API format to OpenAI format
**When**: Use `use-deepseek` or `use-nvidia` when Claude limits hit, `use-claude` to switch back

## 🚀 Quick Start

```bash
# 1. Clone and setup
cd ~/Documents/claude-code-router
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your DeepSeek/NVIDIA API keys

# 3. Install shell functions
source .zshrc.router

# 4. Switch to DeepSeek (when Claude limits hit)
use-deepseek

# 5. Use Claude Code normally
cd ~/your-project
claude
```

A local FastAPI proxy that transparently routes **Claude Code** API calls to **DeepSeek V3** or **DeepSeek V3 via NVIDIA** when your Anthropic rate limits hit.

Claude Code thinks it's talking to Anthropic. The router intercepts every request, converts the Claude message format to OpenAI-compatible JSON, forwards it to your chosen provider, and converts the response back — completely transparent.

```
Claude Code ──► localhost:8082 ──► DeepSeek V3  (or DeepSeek via NVIDIA)
                 ai_router.py        ▲ your API key here
```

## Why This Project Exists

### The Problem
Claude Code users face:
- **Rate limits** even with Max subscription
- **Account locks** and phone verification issues
- **High costs** ($200/month) with limited usage
- **Single provider** (only Claude models)

### When to Use This Project
- ✅ **You prefer open source** and want to understand/modify the code
- ✅ **You only need DeepSeek or NVIDIA** models
- ✅ **You already have API keys** for these providers
- ✅ **You want a simple, transparent proxy** without complex features
- ✅ **You're comfortable with Python** and command line setup

## Project Analysis

### Architecture Overview
- **FastAPI proxy server** (`ai_router.py`) on localhost:8082
- **Format conversion** between Claude API and OpenAI-compatible formats
- **Shell integration** (`.zshrc.router`) for easy provider switching
- **Environment-based configuration** with `.env` for API keys

### Key Features
1. **Message Format Conversion**: Converts Claude's complex message format to OpenAI format
2. **Tool Support**: Transforms Claude tool definitions to OpenAI function calling format
3. **Streaming Support**: Real-time conversion of streaming responses
4. **Provider Abstraction**: Configurable providers (DeepSeek, NVIDIA)
5. **Shell Commands**: `use-deepseek`, `use-nvidia`, `use-claude` for switching
6. **Diagnostic Tools**: `router-status`, `router-ping`, `router-logs` for monitoring

---

## Project Structure

```
claude-code-router/
├── ai_router.py        # Main FastAPI proxy server
├── .zshrc.router       # Shell functions (use-deepseek, etc.)
├── .env.example        # Template for API keys (safe to commit)
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
├── QUICKSTART.txt      # Quick reference guide
└── venv/               # Python virtual environment (git-ignored)
```

### File Details

- **`ai_router.py`**: Core proxy with `/v1/messages` endpoint, format conversion, and streaming support
- **`.zshrc.router`**: Shell functions for starting/stopping proxy and switching providers
- **`.env.example`**: Template for `AI_PROVIDER`, `ROUTER_PORT`, and API keys
- **`requirements.txt`**: FastAPI, httpx, uvicorn, python-dotenv

---

## Prerequisites

- macOS with Python 3.10+
- Claude Code installed (`npm install -g @anthropic-ai/claude-code`)
- A DeepSeek API key → [platform.deepseek.com](https://platform.deepseek.com)
- A NVIDIA API key → [build.nvidia.com](https://build.nvidia.com)

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

### 3. Add your API keys

```bash
cp .env.example .env
open -a "Visual Studio Code" .env
```

Fill in your real keys:

```env
AI_PROVIDER=deepseek
ROUTER_PORT=8082

DEEPSEEK_API_KEY=sk-your-real-key-here
DEEPSEEK_BIG_MODEL=deepseek-chat
DEEPSEEK_SMALL_MODEL=deepseek-chat

NVIDIA_API_KEY=nvapi-your-real-key-here
NVIDIA_BIG_MODEL=deepseek-ai/deepseek-v3.2
NVIDIA_SMALL_MODEL=deepseek-ai/deepseek-v3.2
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

### Hit your Claude Pro limit? Switch to DeepSeek:

```bash
use-deepseek
```

### Switch to NVIDIA Nemotron instead:

```bash
use-nvidia
```

### Switch to Google Gemini:

```bash
use-gemini
```

### Claude limits reset? Go back to Claude Pro:

```bash
use-claude
```

### Check which mode you are currently in:

```bash
claude-mode
```

### Then just use Claude Code normally — no other changes:

```bash
cd ~/your-project
claude
```

---

## Verification Commands

```bash
# Check the proxy is running (no external call)
router-status
# Expected: {"status": "ok", "provider": "deepseek", "key_set": true, ...}

# Send a live test message to the upstream API
router-ping
# Expected: {"status": "ok", "provider": "deepseek", "reply": "PONG"}

# Watch live proxy logs
router-logs
```

---

## Shutdown / End of Session

```bash
# Stop proxy and restore Claude Pro
use-claude

# Exit virtual environment in current terminal
deactivate
```

---

## Troubleshooting

### `use-deepseek: command not found`
The shell functions are not loaded. Run:
```bash
source ~/Documents/claude-code-router/.zshrc.router
type use-deepseek
```

### `router-status` fails (connection refused)
The proxy is not running. Start it manually:
```bash
router-start
```

### `router-ping` returns error 401
Your API key in `.env` is wrong or expired.

### `router-ping` returns ConnectError
No internet or the upstream API (DeepSeek/NVIDIA) is down.

### Claude Code shows auth conflict warning
You are logged into claude.ai AND the `ANTHROPIC_API_KEY` is set. Run once:
```bash
claude /logout
# When prompted to log in again → No
```
When you switch back with `use-claude`, run `claude` and it will re-authenticate via browser.

### `max_tokens` error from DeepSeek
Already handled in `ai_router.py` — `max_tokens` is automatically capped at 8192.

### Python import errors
Ensure virtual environment is activated and dependencies installed:
```bash
cd ~/Documents/claude-code-router
source venv/bin/activate
pip install -r requirements.txt
```

### Port 8082 already in use
Check what's using the port and stop it, or change `ROUTER_PORT` in `.env`:
```bash
lsof -ti:8082 | xargs kill -9
# Or edit .env: ROUTER_PORT=8083
```

### Shell functions not available in new terminal
The functions are loaded from `.zshrc`. Either:
1. Source the router file manually: `source ~/Documents/claude-code-router/.zshrc.router`
2. Open a new terminal (should auto-load from `.zshrc`)
3. Check `.zshrc` includes the router source line

### Streaming responses not working
Check if the upstream provider supports streaming for your selected model. Some models or API tiers may not support streaming.

### Tool calling failures
Different providers have varying tool calling implementations. Check:
1. Tool definitions are compatible with OpenAI function calling format
2. Required parameters are properly defined in input_schema
3. Tool names don't contain special characters

---

## How It Works

### High-Level Flow
1. `use-deepseek` starts proxy and sets `ANTHROPIC_BASE_URL=http://localhost:8082`
2. Claude Code sends requests to local proxy instead of Anthropic
3. Proxy converts Claude format → OpenAI format → DeepSeek/NVIDIA
4. Responses converted back to Claude format
5. `use-claude` stops proxy and restores direct Anthropic connection

### Technical Flow
- **Request interception**: `http://localhost:8082/v1/messages`
- **Format conversion**: `conv_messages()` and `conv_tools()` functions
- **Provider selection**: Based on `AI_PROVIDER` environment variable
- **Model mapping**: `pick_model()` selects big/small based on Claude model
- **Streaming support**: `stream_oai_to_claude()` converts real-time events
- **Shell integration**: `.zshrc.router` manages lifecycle and state

---

## Provider Reference

### Current Supported Providers

| Provider | Model (big) | Model (small) | Pricing | API Endpoint | Notes |
|---|---|---|---|---|---|
| DeepSeek | `deepseek-chat` (V3) | `deepseek-chat` | Pay-per-use (very cheap) | `https://api.deepseek.com/v1` | 8192 token limit, good tool support |
| NVIDIA (DeepSeek V3) | `deepseek-ai/deepseek-v3.2` | `deepseek-ai/deepseek-v3.2` | Free tier available | `https://integrate.api.nvidia.com/v1` | DeepSeek V3 via NVIDIA, rate limits apply |
| Gemini | `gemini/gemini-3-flash-preview` | `gemini/gemini-2.5-flash-lite` | Pay-per-use | `https://generativelanguage.googleapis.com/v1beta` | Google's Gemini models, three-tier mapping |

### Cost Comparison (Approximate)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | ~Cost per Request |
|-------|----------------------|----------------------|-------------------|
| **DeepSeek V3** | $0.14 | $0.28 | **$0.0002–0.001** |
| **NVIDIA DeepSeek V3** | Free tier | Free tier | **$0** (with limits) |
| **Gemini 2.5 Flash** | $0.075 | $0.30 | **$0.0001–0.001** |
| Claude Haiku 4.5 | $1.00 | $5.00 | $0.002–0.01 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $0.006–0.03 |
| Claude Opus 4.6 | $5.00 | $25.00 | $0.01–0.05 |

### Extensible to Other Providers

The architecture supports adding more providers easily. Popular alternatives:

1. **OpenAI** (GPT-4o, GPT-4o-mini, o3-mini)
2. **Anthropic** (Claude models via direct API)
3. **xAI** (Grok models)
4. **MiniMax** (M2.7)
5. **Moonshot** (Kimi K2.5)

To add a new provider:
1. Add entry to `PROVIDERS` dictionary in `ai_router.py`
2. Update `.env.example` with new API key variable
3. Add shell function in `.zshrc.router` (optional)

### Provider-Specific Notes

#### DeepSeek
- **Token limit**: 8192 max_tokens (automatically capped by proxy)
- **Streaming**: Supported for most models
- **Tool calling**: Good compatibility with OpenAI format
- **Image support**: Limited (base64 only via proxy conversion)
- **Cost**: ~$0.14 per 1M tokens input, $0.28 per 1M tokens output

#### NVIDIA (DeepSeek V3)
- **Free tier**: Limited requests per day
- **Model**: DeepSeek V3.2 via NVIDIA endpoint (deepseek-ai/deepseek-v3.2)
- **Rate limits**: Apply to free tier usage
- **API stability**: Enterprise-grade NVIDIA infrastructure
- **Thinking feature**: Supported with `thinking: True` configuration
- **Tool calling**: Good compatibility with OpenAI format

#### Gemini
- **Three-tier mapping**: Default (sonnet), Big (opus), Small (haiku) models
- **API format**: Uses Google's Generative Language API format (not OpenAI-compatible)
- **Image support**: Limited base64 image support via proxy conversion
- **Tool calling**: Basic support (converted to text representation)
- **Streaming**: Supported for most models
- **Cost**: Competitive pricing with Gemini 2.5 Flash series

### Model Mapping Logic
The proxy uses simple heuristics to map Claude models to provider models:
- **Claude Sonnet/Opus** → Provider's "big_model" (e.g., `deepseek-chat`)
- **Claude Haiku** → Provider's "small_model" (e.g., `deepseek-chat`)

For Gemini specifically:
- **Claude Opus** → `GEMINI_BIG_MODEL` (gemini/gemini-3-flash-preview)
- **Claude Sonnet** → `GEMINI_DEFAULT_MODEL` (gemini/gemini-2.5-flash)
- **Claude Haiku** → `GEMINI_SMALL_MODEL` (gemini/gemini-2.5-flash-lite)

This can be customized in `.env` by setting different model names for `*_BIG_MODEL` and `*_SMALL_MODEL`.

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

### API Key Security
- **Never commit `.env` file** - Contains actual API keys
- **Use `.env.example` as template** - Safe to commit
- **Keys stored locally** in plain text, forwarded to providers

### Network Security
- **Local proxy only** on `127.0.0.1:8082`
- **No authentication** - Accepts localhost requests only
- **Upstream HTTPS** to DeepSeek/NVIDIA

### Data Privacy
- **Prompts/responses** pass through local proxy
- **No conversation logging** - Only operational logs in `router.log`
- **Third-party providers** receive your API requests

## Limitations

### Feature Compatibility
- **✅ Full support**: Text generation, basic tool calling
- **⚠️ Partial support**: Image content (base64 only)
- **❌ Not supported**: File uploads, audio processing

### Provider Differences
- **Model capabilities** vary between providers
- **Token limits**: DeepSeek has 8192 max_tokens hard cap
- **Tool support** may have implementation differences

### Performance
- **Additional latency** from format conversion
- **Streaming conversion** adds processing delay
- **Local resource usage** from FastAPI server

## Development Notes

### Code Quality
- **Well-structured** with separation of concerns
- **Comprehensive error handling** for API failures
- **Type hints** and async/await patterns
- **Modular design** for easy extension

### Extensibility
- **Provider abstraction** for adding new AI services
- **Centralized format conversion** logic
- **Shell integration** for user-friendly interface

### Potential Enhancements
1. **Multiple Provider Support** (OpenAI, Google Gemini, etc.)
2. **Smart Routing** with fallback chains
3. **Usage Statistics** tracking tokens and costs
4. **Enhanced Model Switching** commands

### Testing
- **Manual testing** for provider switching
- **API compatibility** testing for Claude Code updates
- **Streaming validation** for real-time use

## License

MIT — use freely, modify freely.


## Acknowledgments

- **Claude Code** for the excellent CLI tool
- **DeepSeek** and **NVIDIA** for providing alternative AI APIs
- **FastAPI** and **httpx** for the robust Python web stack
