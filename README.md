# claude-code-router

<div align="center">

<h3>🚀 Personal Claude Code Proxy for DeepSeek & NVIDIA</h3>

<p>When Claude Code hits rate limits, route to <strong>DeepSeek V3</strong> or <strong>NVIDIA Nemotron-3 Super 120B</strong> instead.</p>

<br>

<img src="https://img.shields.io/badge/🔧_DIY_Solution-black?style=for-the-badge" alt="DIY Solution">&nbsp;
<img src="https://img.shields.io/badge/🐍_Python_FastAPI-blue?style=for-the-badge" alt="Python FastAPI">&nbsp;
<img src="https://img.shields.io/badge/🔄_2_Providers-yellow?style=for-the-badge" alt="2 Providers">&nbsp;
<img src="https://img.shields.io/badge/💰_API_Keys-purple?style=for-the-badge" alt="API Keys">&nbsp;
<img src="https://img.shields.io/badge/⚡_Transparent_Proxy-green?style=for-the-badge" alt="Transparent Proxy">

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

> **Note**: This is a **personal, DIY proxy** for developers who want a simple solution to route Claude Code to alternative AI providers.

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

A local FastAPI proxy that transparently routes **Claude Code** API calls to **DeepSeek V3** or **NVIDIA Nemotron-3 Super 120B** when your Anthropic rate limits hit.

Claude Code thinks it's talking to Anthropic. The router intercepts every request, converts the Claude message format to OpenAI-compatible JSON, forwards it to your chosen provider, and converts the response back — completely transparent.

```
Claude Code ──► localhost:8082 ──► DeepSeek V3  (or NVIDIA Nemotron-3 Super 120B)
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

This project implements a sophisticated API proxy with the following key features:

### Architecture Overview
- **FastAPI-based proxy server** (`ai_router.py`) running on localhost:8082
- **Transparent format conversion** between Claude API and OpenAI-compatible formats
- **Shell integration** (`.zshrc.router`) for seamless switching between providers
- **Environment-based configuration** with `.env` file for API keys

### Key Technical Components

1. **Message Format Conversion** (`conv_messages()` function):
   - Converts Claude's complex message format (with tool use, images, multi-part content) to OpenAI format
   - Handles system messages, user messages with tool results, and assistant tool calls
   - Supports image content via base64 encoding

2. **Tool Support** (`conv_tools()` function):
   - Converts Claude tool definitions to OpenAI function calling format
   - Preserves tool names, descriptions, and input schemas

3. **Streaming Support** (`stream_oai_to_claude()` function):
   - Real-time conversion of OpenAI streaming responses to Claude SSE format
   - Handles text deltas and tool call streaming
   - Maintains proper event sequencing (message_start, content_block_start, etc.)

4. **Provider Abstraction**:
   - Configurable providers (DeepSeek, NVIDIA) with separate API endpoints and models
   - Automatic model selection based on Claude model type (big for Sonnet/Opus, small for Haiku)

5. **Shell Integration**:
   - `use-deepseek`, `use-nvidia`, `use-claude` commands for switching providers
   - Persistent state management via `.state` file
   - Health checks and diagnostic commands (`router-status`, `router-ping`, `router-logs`)

---

## Project Structure

```
~/Documents/claude-code-router/
├── ai_router.py        # Main FastAPI proxy server with format conversion logic
├── .zshrc.router       # Shell functions (use-deepseek, use-claude, etc.)
├── .env                # Your real API keys (git-ignored)
├── .env.example        # Template — safe to commit
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This documentation
└── venv/               # Python virtual environment (git-ignored)
```

### File Details

- **`ai_router.py`**: Core proxy server with:
  - `/v1/messages` endpoint for Claude API compatibility
  - `/health` and `/ping` endpoints for diagnostics
  - Complete format conversion between Claude and OpenAI APIs
  - Streaming and non-streaming response handling

- **`.zshrc.router`**: Shell functions that:
  - Start/stop the proxy server
  - Set/unset `ANTHROPIC_BASE_URL` environment variable
  - Provide status commands and aliases
  - Manage provider switching

- **`.env.example`**: Configuration template with:
  - Provider selection (`AI_PROVIDER`)
  - Port configuration (`ROUTER_PORT`)
  - API keys and model names for DeepSeek and NVIDIA

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
NVIDIA_BIG_MODEL=nvidia/nemotron-3-super-120b-a12b:free
NVIDIA_SMALL_MODEL=nvidia/nemotron-3-super-120b-a12b:free
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
1. `use-deepseek` starts the proxy in background and sets `ANTHROPIC_BASE_URL=http://localhost:8082`
2. Claude Code reads that env var and sends all requests to your local proxy instead of Anthropic
3. The proxy converts Claude API format → OpenAI format and forwards to DeepSeek or NVIDIA
4. Responses are converted back to Claude format and returned to Claude Code
5. `use-claude` kills the proxy and unsets the env var — direct Anthropic connection restored

### Detailed Technical Flow

#### 1. Request Interception
- Claude Code sends requests to `http://localhost:8082/v1/messages`
- FastAPI receives the request with Claude's native format
- Provider is determined from `AI_PROVIDER` environment variable

#### 2. Format Conversion (Claude → OpenAI)
- **Message conversion**: `conv_messages()` processes Claude's complex message structure
- **Tool conversion**: `conv_tools()` transforms Claude tools to OpenAI functions
- **Parameter mapping**: Temperature, top_p, max_tokens are passed through
- **Model selection**: `pick_model()` chooses big/small model based on Claude model name

#### 3. Upstream API Call
- HTTP request to provider's `/chat/completions` endpoint
- API key from `.env` added to Authorization header
- Streaming vs non-streaming handled differently

#### 4. Response Conversion (OpenAI → Claude)
- **Non-streaming**: `oai_to_claude()` converts complete response
- **Streaming**: `stream_oai_to_claude()` converts Server-Sent Events in real-time
- **Tool call conversion**: OpenAI tool_calls → Claude tool_use format
- **Stop reason mapping**: OpenAI finish_reason → Claude stop_reason

#### 5. Shell Integration
- `.zshrc.router` functions manage proxy lifecycle
- `.state` file preserves `ANTHROPIC_BASE_URL` across terminal sessions
- Diagnostic commands provide visibility into proxy operation

---

## Provider Reference

### Current Supported Providers

| Provider | Model (big) | Model (small) | Pricing | API Endpoint | Notes |
|---|---|---|---|---|---|
| DeepSeek | `deepseek-chat` (V3) | `deepseek-chat` | Pay-per-use (very cheap) | `https://api.deepseek.com/v1` | 8192 token limit, good tool support |
| NVIDIA Nemotron | `nvidia/nemotron-3-super-120b-a12b:free` | `nvidia/nemotron-3-super-120b-a12b:free` | Free tier available | `https://integrate.api.nvidia.com/v1` | High-quality 120B parameter model, rate limits apply |

### Cost Comparison (Approximate)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | ~Cost per Request |
|-------|----------------------|----------------------|-------------------|
| **DeepSeek V3** | $0.14 | $0.28 | **$0.0002–0.001** |
| **NVIDIA Nemotron** | Free tier | Free tier | **$0** (with limits) |
| Claude Haiku 4.5 | $1.00 | $5.00 | $0.002–0.01 |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $0.006–0.03 |
| Claude Opus 4.6 | $5.00 | $25.00 | $0.01–0.05 |

### Extensible to Other Providers

The architecture supports adding more providers easily. Popular alternatives:

1. **OpenAI** (GPT-4o, GPT-4o-mini, o3-mini)
2. **Google** (Gemini 2.5 Flash, Gemini 2.5 Pro)
3. **Anthropic** (Claude models via direct API)
4. **xAI** (Grok models)
5. **MiniMax** (M2.7)
6. **Moonshot** (Kimi K2.5)

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

#### NVIDIA Nemotron
- **Free tier**: Limited requests per day
- **Model**: Nemotron-3 Super 120B (120 billion parameter model)
- **Rate limits**: Apply to free tier usage
- **API stability**: Enterprise-grade infrastructure
- **Tool calling**: Generally good compatibility

### Model Mapping Logic
The proxy uses simple heuristics to map Claude models to provider models:
- **Claude Sonnet/Opus** → Provider's "big_model" (e.g., `deepseek-chat`)
- **Claude Haiku** → Provider's "small_model" (e.g., `deepseek-chat`)

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
- **Never commit `.env` file** - It contains your actual API keys
- **Use `.env.example` as a template** - Commit only the example file
- **API keys are stored locally** - The proxy forwards them to the selected provider
- **No key encryption** - Keys are stored in plain text in `.env`

### Network Security
- **Local proxy only** - Runs on `127.0.0.1:8082`, not exposed to network
- **No authentication** - The proxy accepts requests from localhost only
- **SSL/TLS** - Upstream calls to DeepSeek/NVIDIA use HTTPS

### Data Privacy
- **Your prompts and responses** pass through the local proxy
- **No logging of conversation content** - Only operational logs in `router.log`
- **Third-party providers** - DeepSeek and NVIDIA receive your API requests

## Limitations

### Feature Compatibility
- **✅ Full support**: Text generation, basic tool calling
- **⚠️ Partial support**: Image content (base64 only, no URL images)
- **❌ Not supported**: File uploads, audio processing, some advanced tool features

### Provider Differences
- **Model capabilities** vary between Claude, DeepSeek, and NVIDIA
- **Token limits** differ (DeepSeek has 8192 max_tokens hard cap)
- **Tool support** may have subtle differences in implementation

### Performance Considerations
- **Additional latency** from format conversion and proxy overhead
- **Streaming conversion** adds minor processing delay
- **Local resource usage** from running Python FastAPI server

## Development Notes

### Code Quality
- **Well-structured** with clear separation of concerns
- **Comprehensive error handling** for API failures
- **Type hints** and async/await patterns throughout
- **Modular design** for easy extension to new providers

### Extensibility
- **Provider abstraction** makes adding new AI services straightforward
- **Format conversion** logic is centralized and reusable
- **Shell integration** provides user-friendly interface

### Potential Enhancements
This project could be extended with additional features:

1. **Multiple Provider Support**
   ```python
   # Add to PROVIDERS dictionary in ai_router.py
   "openai": {
       "base_url": "https://api.openai.com/v1",
       "api_key": os.environ.get("OPENAI_API_KEY", ""),
       "big_model": "gpt-4o",
       "small_model": "gpt-4o-mini",
   }
   ```

2. **Smart Routing**
   - Implement simple heuristics to choose cheapest capable model
   - Add fallback chains for error recovery

3. **Usage Statistics**
   - Track tokens, costs, and model usage
   - Calculate savings vs Claude Pro

4. **Model Switching Commands**
   - Extend shell functions for quick model changes
   - Add `/model` command support within Claude Code

### Testing Considerations
- **Manual testing** required for provider switching
- **API compatibility** testing needed for new Claude Code versions
- **Streaming validation** important for real-time use cases

## License

MIT — use freely, modify freely.


## Acknowledgments

- **Claude Code** for the excellent CLI tool
- **DeepSeek** and **NVIDIA** for providing alternative AI APIs
- **FastAPI** and **httpx** for the robust Python web stack
