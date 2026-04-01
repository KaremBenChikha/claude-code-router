#!/usr/bin/env python3
"""
Claude Code Router
Routes Claude Code → DeepSeek V3 or DeepSeek V3 (via NVIDIA) when limits hit.
"""

import os, json, uuid, socket
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import AsyncGenerator
import uvicorn

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

app      = FastAPI(title="Claude Code Router")
PORT     = int(os.environ.get("ROUTER_PORT", "8082"))
PROVIDER = os.environ.get("AI_PROVIDER", "deepseek")

PROVIDERS = {
    "deepseek": {
        "base_url":    "https://api.deepseek.com/v1",
        "api_key":     os.environ.get("DEEPSEEK_API_KEY", ""),
        "big_model":   os.environ.get("DEEPSEEK_BIG_MODEL",   "deepseek-chat"),
        "small_model": os.environ.get("DEEPSEEK_SMALL_MODEL", "deepseek-chat"),
    },
    "nvidia": {
        "base_url":    "https://integrate.api.nvidia.com/v1",
        "api_key":     os.environ.get("NVIDIA_API_KEY", ""),
        "big_model":   os.environ.get("NVIDIA_BIG_MODEL",   "deepseek-ai/deepseek-v3.2"),
        "small_model": os.environ.get("NVIDIA_SMALL_MODEL", "deepseek-ai/deepseek-v3.2"),
    },
    "gemini": {
        "base_url":    "https://generativelanguage.googleapis.com/v1beta",
        "api_key":     os.environ.get("GEMINI_API_KEY", ""),
        "big_model":   os.environ.get("GEMINI_BIG_MODEL", "gemini/gemini-3-flash-preview"),
        "small_model": os.environ.get("GEMINI_SMALL_MODEL", "gemini/gemini-2.5-flash-lite"),
        "default_model": os.environ.get("GEMINI_DEFAULT_MODEL", "gemini/gemini-2.5-flash"),
    },
}

# ─── Gemini Helper Function ─────────────────────────────────────────────────────

def gemini_model_name(model: str) -> str:
    """Strip LiteLLM's 'gemini/' prefix for direct Google API calls."""
    return model.split("/")[-1]  # "gemini/gemini-2.5-flash" → "gemini-2.5-flash"


# ─── Health (local only) ─────────────────────────────────────────────────────

@app.get("/health")
async def health():
    prov = PROVIDERS[PROVIDER]
    model = prov.get("default_model", prov["big_model"]) if PROVIDER == "gemini" else prov["big_model"]
    return {
        "status":   "ok",
        "provider": PROVIDER,
        "model":    model,
        "key_set":  bool(prov["api_key"]),
        "port":     PORT,
    }

# ─── Ping (real call to upstream to verify key + connectivity) ───────────────

@app.get("/ping")
async def ping():
    prov = PROVIDERS[PROVIDER]
    if not prov["api_key"]:
        return JSONResponse({"status": "error", "reason": f"No API key for '{PROVIDER}'"}, status_code=500)

    if PROVIDER == "gemini":
        # Gemini API uses different format
        payload = {
            "contents": [{
                "parts": [{"text": "Hi! Reply with only the word: PONG"}],
                "role": "user"
            }],
            "generationConfig": {
                "maxOutputTokens": 10,
                "temperature": 0.1,
            }
        }
        headers = {"Content-Type": "application/json"}
        url = f"{prov['base_url']}/models/{gemini_model_name(prov['default_model'])}:generateContent?key={prov['api_key']}"
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.post(url, json=payload, headers=headers)
            if r.status_code == 200:
                reply = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                return {"status": "ok", "provider": PROVIDER, "reply": reply.strip() if reply else ""}
            return JSONResponse({"status": "error", "http": r.status_code, "body": r.text}, status_code=r.status_code)
        except httpx.ConnectError as e:
            return JSONResponse({"status": "error", "reason": str(e)}, status_code=503)
        except Exception as e:
            return JSONResponse({"status": "error", "reason": str(e)}, status_code=500)
    else:
        # OpenAI-compatible providers (DeepSeek, NVIDIA)
        payload = {
            "model":      prov["big_model"],
            "messages":   [{"role": "user", "content": "Hi! Reply with only the word: PONG"}],
            "max_tokens": 10,
            "stream":     False,
        }
        # NVIDIA (DeepSeek via NVIDIA) specific configuration
        if PROVIDER == "nvidia":
            payload["extra_body"] = {
                "chat_template_kwargs": {"thinking": True}
            }
        headers = {"Authorization": f"Bearer {prov['api_key']}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.post(f"{prov['base_url']}/chat/completions", json=payload, headers=headers)
            if r.status_code == 200:
                reply = r.json()["choices"][0]["message"]["content"]
                return {"status": "ok", "provider": PROVIDER, "reply": reply.strip() if reply else ""}
            return JSONResponse({"status": "error", "http": r.status_code, "body": r.text}, status_code=r.status_code)
        except httpx.ConnectError as e:
            return JSONResponse({"status": "error", "reason": str(e)}, status_code=503)
        except Exception as e:
            return JSONResponse({"status": "error", "reason": str(e)}, status_code=500)

# ─── Claude → OpenAI conversion ──────────────────────────────────────────────

def pick_model(prov: dict, claude_model: str) -> str:
    if PROVIDER == "gemini":
        # Gemini has three model tiers
        if "opus" in claude_model:
            return prov["big_model"]  # gemini/gemini-3-flash-preview
        elif "haiku" in claude_model:
            return prov["small_model"]  # gemini/gemini-2.5-flash-lite
        else:
            # Default to gemini/gemini-2.5-flash for sonnet and others
            return prov.get("default_model", prov["big_model"])
    else:
        # Other providers use big/small model selection
        return prov["small_model"] if "haiku" in claude_model else prov["big_model"]

def conv_messages(body: dict) -> list:
    msgs = []
    if sys := body.get("system"):
        text = sys if isinstance(sys, str) else "\n".join(
            b.get("text", "") for b in sys if b.get("type") == "text"
        )
        if text:
            msgs.append({"role": "system", "content": text})

    for m in body.get("messages", []):
        role, content = m["role"], m["content"]
        if isinstance(content, str):
            msgs.append({"role": role, "content": content})
            continue

        if role == "user":
            tool_results = [b for b in content if b.get("type") == "tool_result"]
            text_blocks  = [b for b in content if b.get("type") == "text"]
            for tr in tool_results:
                tc = tr.get("content", "")
                if isinstance(tc, list):
                    tc = "\n".join(b.get("text", "") for b in tc if b.get("type") == "text")
                msgs.append({"role": "tool", "tool_call_id": tr.get("tool_use_id", ""), "content": tc})
            if text_blocks:
                msgs.append({"role": "user", "content": "\n".join(b.get("text", "") for b in text_blocks)})
            elif not tool_results:
                parts = []
                for b in content:
                    if b.get("type") == "text":
                        parts.append({"type": "text", "text": b["text"]})
                    elif b.get("type") == "image":
                        src = b.get("source", {})
                        if src.get("type") == "base64":
                            parts.append({"type": "image_url", "image_url": {
                                "url": f"{src['media_type']};base64,{src['data']}"}})
                msgs.append({"role": "user", "content": parts or ""})

        elif role == "assistant":
            tool_uses   = [b for b in content if b.get("type") == "tool_use"]
            text_blocks = [b for b in content if b.get("type") == "text"]
            out = {"role": "assistant", "content": "\n".join(b.get("text", "") for b in text_blocks)}
            if tool_uses:
                out["tool_calls"] = [
                    {"id": tu.get("id", f"call_{i}"), "type": "function",
                     "function": {"name": tu["name"], "arguments": json.dumps(tu.get("input", {}))}}
                    for i, tu in enumerate(tool_uses)
                ]
            msgs.append(out)
    return msgs

def conv_tools(tools: list) -> list:
    return [{"type": "function", "function": {
        "name": t["name"],
        "description": t.get("description", ""),
        "parameters": t.get("input_schema", {"type": "object", "properties": {}})
    }} for t in tools]

def build_oai_req(body: dict, model: str) -> dict:
    req = {
        "model":      model,
        "messages":   conv_messages(body),
        "max_tokens": min(body.get("max_tokens", 8096), 8192),  # DeepSeek hard cap
        "stream":     body.get("stream", False),
    }
    for k in ("temperature", "top_p"):
        if k in body:
            req[k] = body[k]
    if "tools" in body:
        req["tools"] = conv_tools(body["tools"])
    if tc := body.get("tool_choice"):
        req["tool_choice"] = (
            {"type": "function", "function": {"name": tc["name"]}}
            if isinstance(tc, dict) and tc.get("type") == "tool"
            else tc.get("type", "auto")
        )
    # NVIDIA (DeepSeek via NVIDIA) specific configuration
    if PROVIDER == "nvidia":
        req["extra_body"] = {
            "chat_template_kwargs": {"thinking": True}
        }
    return req

# ─── Gemini-specific conversion ──────────────────────────────────────────────

def conv_messages_to_gemini(body: dict) -> list:
    """Convert Claude messages to Gemini format."""
    contents = []
    system_parts = []

    # Handle system message
    if sys := body.get("system"):
        text = sys if isinstance(sys, str) else "\n".join(
            b.get("text", "") for b in sys if b.get("type") == "text"
        )
        if text:
            system_parts.append({"text": f"System: {text}"})

    # Convert messages
    for m in body.get("messages", []):
        role, content = m["role"], m["content"]

        if role == "user":
            parts = []
            if system_parts:
                parts.extend(system_parts)
                system_parts = []  # Clear system parts after first use

            if isinstance(content, str):
                parts.append({"text": content})
            else:
                for b in content:
                    if b.get("type") == "text":
                        parts.append({"text": b["text"]})
                    elif b.get("type") == "image":
                        src = b.get("source", {})
                        if src.get("type") == "base64":
                            # Gemini supports inline data images
                            parts.append({
                                "inline_data": {
                                    "mime_type": src["media_type"],
                                    "data": src["data"]
                                }
                            })

            if parts:
                contents.append({"role": "user", "parts": parts})

        elif role == "assistant":
            parts = []
            for b in content:
                if b.get("type") == "text":
                    parts.append({"text": b["text"]})
                elif b.get("type") == "tool_use":
                    # Gemini doesn't support tool calls in the same way
                    # We'll convert to text representation
                    parts.append({"text": f"[Tool call: {b['name']} with input {json.dumps(b.get('input', {}))}]"})

            if parts:
                contents.append({"role": "model", "parts": parts})

    return contents

def build_gemini_req(body: dict, model: str) -> dict:
    """Build Gemini API request."""
    req = {
        "contents": conv_messages_to_gemini(body),
        "generationConfig": {
            "maxOutputTokens": min(body.get("max_tokens", 8096), 8192),
        }
    }

    # Add optional parameters
    if temp := body.get("temperature"):
        req["generationConfig"]["temperature"] = temp
    if top_p := body.get("top_p"):
        req["generationConfig"]["topP"] = top_p

    # Note: Gemini has limited tool/function calling support
    # We'll handle basic tool calls as text for now

    return req

def gemini_to_claude(gemini_resp: dict, orig_model: str) -> dict:
    """Convert Gemini response to Claude format."""
    if "candidates" not in gemini_resp or not gemini_resp["candidates"]:
        raise HTTPException(500, "No candidates in Gemini response")

    candidate = gemini_resp["candidates"][0]
    content_parts = candidate.get("content", {}).get("parts", [])

    # Convert Gemini parts to Claude content
    content = []
    for part in content_parts:
        if "text" in part:
            content.append({"type": "text", "text": part["text"]})
        # Note: Gemini may return other part types, but we handle text for now

    return {
        "id":            f"msg_{uuid.uuid4().hex[:12]}",
        "type":          "message",
        "role":          "assistant",
        "model":         orig_model,
        "content":       content,
        "stop_reason":   "end_turn",  # Gemini doesn't provide detailed stop reasons
        "stop_sequence": None,
        "usage": {
            "input_tokens":  gemini_resp.get("usageMetadata", {}).get("promptTokenCount", 0),
            "output_tokens": gemini_resp.get("usageMetadata", {}).get("candidatesTokenCount", 0),
        },
    }

async def stream_gemini_to_claude(resp: httpx.Response) -> AsyncGenerator[str, None]:
    """Convert Gemini streaming response to Claude SSE format."""
    mid = f"msg_{uuid.uuid4().hex[:12]}"
    E   = lambda t, d: f"event: {t}\n {json.dumps(d)}\n\n"

    yield E("message_start", {"type": "message_start", "message": {
        "id": mid, "type": "message", "role": "assistant", "content": [],
        "model": "proxy", "stop_reason": None, "stop_sequence": None,
        "usage": {"input_tokens": 0, "output_tokens": 0}}})
    yield E("content_block_start", {"type": "content_block_start", "index": 0,
                                     "content_block": {"type": "text", "text": ""}})
    yield E("ping", {"type": "ping"})

    buffer = ""
    async for line in resp.aiter_lines():
        if line.startswith("data: "):
            data = line[6:]
            if data.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                if "candidates" in chunk and chunk["candidates"]:
                    for candidate in chunk["candidates"]:
                        if "content" in candidate and candidate["content"].get("parts"):
                            for part in candidate["content"]["parts"]:
                                if "text" in part:
                                    buffer += part["text"]
                                    # Send accumulated text
                                    if buffer:
                                        yield E("content_block_delta", {
                                            "type": "content_block_delta",
                                            "index": 0,
                                            "delta": {"type": "text_delta", "text": buffer}
                                        })
                                        buffer = ""
            except:
                pass

    # Send any remaining buffered text
    if buffer:
        yield E("content_block_delta", {
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": buffer}
        })

    yield E("content_block_stop", {"type": "content_block_stop", "index": 0})
    yield E("message_delta", {"type": "message_delta",
        "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 0}})
    yield E("message_stop", {"type": "message_stop"})

# ─── OpenAI → Claude conversion ──────────────────────────────────────────────

STOP_MAP = {"stop": "end_turn", "tool_calls": "tool_use", "length": "max_tokens"}

def oai_to_claude(oai: dict, orig_model: str) -> dict:
    choice  = oai["choices"][0]
    msg     = choice["message"]
    content = []
    if msg.get("content"):
        content.append({"type": "text", "text": msg["content"]})
    for tc in msg.get("tool_calls") or []:
        try:    args = json.loads(tc["function"]["arguments"])
        except: args = {}
        content.append({"type": "tool_use", "id": tc["id"],
                         "name": tc["function"]["name"], "input": args})
    return {
        "id":            oai.get("id", f"msg_{uuid.uuid4().hex[:12]}"),
        "type":          "message",
        "role":          "assistant",
        "model":         orig_model,
        "content":       content,
        "stop_reason":   STOP_MAP.get(choice.get("finish_reason", "stop"), "end_turn"),
        "stop_sequence": None,
        "usage": {
            "input_tokens":  oai.get("usage", {}).get("prompt_tokens", 0),
            "output_tokens": oai.get("usage", {}).get("completion_tokens", 0),
        },
    }

async def stream_oai_to_claude(resp: httpx.Response) -> AsyncGenerator[str, None]:
    mid = f"msg_{uuid.uuid4().hex[:12]}"
    E   = lambda t, d: f"event: {t}\n {json.dumps(d)}\n\n"

    yield E("message_start", {"type": "message_start", "message": {
        "id": mid, "type": "message", "role": "assistant", "content": [],
        "model": "proxy", "stop_reason": None, "stop_sequence": None,
        "usage": {"input_tokens": 0, "output_tokens": 0}}})
    yield E("content_block_start", {"type": "content_block_start", "index": 0,
                                     "content_block": {"type": "text", "text": ""}})
    yield E("ping", {"type": "ping"})

    tcs: dict[int, dict] = {}

    async for line in resp.aiter_lines():
        if not line.startswith(" "): continue
        data = line[6:]
        if data.strip() == "[DONE]": break
        try:
            delta = json.loads(data).get("choices", [{}])[0].get("delta", {})
            # Handle DeepSeek thinking content (via NVIDIA)
            text_to_send = ""
            if delta.get("reasoning_content"):
                text_to_send += f"<thinking>{delta['reasoning_content']}</thinking>"
            if delta.get("content"):
                text_to_send += delta["content"]
            if text_to_send:
                yield E("content_block_delta", {"type": "content_block_delta", "index": 0,
                    "delta": {"type": "text_delta", "text": text_to_send}})
            for tc in delta.get("tool_calls", []):
                i = tc.get("index", 0)
                if i not in tcs: tcs[i] = {"id": "", "name": "", "arguments": ""}
                if tc.get("id"):                             tcs[i]["id"]        = tc["id"]
                if tc.get("function", {}).get("name"):      tcs[i]["name"]      += tc["function"]["name"]
                if tc.get("function", {}).get("arguments"): tcs[i]["arguments"] += tc["function"]["arguments"]
        except: pass

    yield E("content_block_stop", {"type": "content_block_stop", "index": 0})

    for i, tc in tcs.items():
        bi = i + 1
        yield E("content_block_start", {"type": "content_block_start", "index": bi,
            "content_block": {"type": "tool_use", "id": tc["id"], "name": tc["name"], "input": {}}})
        yield E("content_block_delta", {"type": "content_block_delta", "index": bi,
            "delta": {"type": "input_json_delta", "partial_json": tc["arguments"]}})
        yield E("content_block_stop", {"type": "content_block_stop", "index": bi})

    stop = "tool_use" if tcs else "end_turn"
    yield E("message_delta", {"type": "message_delta",
        "delta": {"stop_reason": stop, "stop_sequence": None}, "usage": {"output_tokens": 0}})
    yield E("message_stop", {"type": "message_stop"})

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.post("/v1/messages")
async def messages(request: Request):
    body       = await request.json()
    orig_model = body.get("model", "claude-3-5-sonnet-20241022")
    prov       = PROVIDERS[PROVIDER]

    if not prov["api_key"]:
        raise HTTPException(500, f"No API key for '{PROVIDER}'. Check ~/claude-code-router/.env")

    if PROVIDER == "gemini":
        # Handle Gemini API
        model = pick_model(prov, orig_model)
        gemini_body = build_gemini_req(body, model)
        url = f"{prov['base_url']}/models/{gemini_model_name(model)}:generateContent?key={prov['api_key']}"

        if body.get("stream", False):
            # Streaming request
            stream_url = f"{prov['base_url']}/models/{gemini_model_name(model)}:streamGenerateContent?key={prov['api_key']}"
            async def generate():
                async with httpx.AsyncClient(timeout=300) as c:
                    async with c.stream("POST", stream_url,
                                        json=gemini_body, headers={"Content-Type": "application/json"}) as r:
                        if r.status_code != 200:
                            err = await r.aread()
                            yield f'event: error\n {json.dumps({"type":"error","error":{"type":"api_error","message":err.decode()}})}\n\n'
                            return
                        async for chunk in stream_gemini_to_claude(r):
                            yield chunk
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            # Non-streaming request
            async with httpx.AsyncClient(timeout=300) as c:
                r = await c.post(url, json=gemini_body, headers={"Content-Type": "application/json"})
                if r.status_code != 200:
                    raise HTTPException(r.status_code, r.text)
                return JSONResponse(gemini_to_claude(r.json(), orig_model))
    else:
        # Handle OpenAI-compatible providers (DeepSeek, NVIDIA)
        oai_body = build_oai_req(body, pick_model(prov, orig_model))
        hdrs     = {"Authorization": f"Bearer {prov['api_key']}", "Content-Type": "application/json"}

        if oai_body.get("stream"):
            async def generate():
                async with httpx.AsyncClient(timeout=300) as c:
                    async with c.stream("POST", f"{prov['base_url']}/chat/completions",
                                        json=oai_body, headers=hdrs) as r:
                        if r.status_code != 200:
                            err = await r.aread()
                            yield f'event: error\n {json.dumps({"type":"error","error":{"type":"api_error","message":err.decode()}})}\n\n'
                            return
                        async for chunk in stream_oai_to_claude(r):
                            yield chunk
            return StreamingResponse(generate(), media_type="text/event-stream")

        async with httpx.AsyncClient(timeout=300) as c:
            r = await c.post(f"{prov['base_url']}/chat/completions", json=oai_body, headers=hdrs)
            if r.status_code != 200:
                raise HTTPException(r.status_code, r.text)
            return JSONResponse(oai_to_claude(r.json(), orig_model))

@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [
        {"id": "claude-3-5-sonnet-20241022", "object": "model"},
        {"id": "claude-3-5-haiku-20241022",  "object": "model"},
        {"id": "claude-opus-4-5",            "object": "model"},
    ]}

def is_port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", port))
        return True
    except OSError:
        return False

if __name__ == "__main__":
    prov = PROVIDERS[PROVIDER]

    if not is_port_available(PORT):
        print(f"\n❌  Port {PORT} is already in use.")
        print(f"    Kill with: lsof -ti:{PORT} | xargs kill -9")
        print(f"    Or change ROUTER_PORT in .env\n")
        exit(1)

    print(f"\n{'═'*45}")
    print(f"  🚀  Claude Code Router")
    print(f"{'═'*45}")
    model = prov.get("default_model", prov["big_model"]) if PROVIDER == "gemini" else prov["big_model"]
    print(f"  Provider : {PROVIDER.upper()}")
    print(f"  Model    : {model}")
    print(f"  Key set  : {'✅' if prov['api_key'] else '❌  — check .env'}")
    print(f"  Port     : {PORT}")
    print(f"{'═'*45}\n")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
