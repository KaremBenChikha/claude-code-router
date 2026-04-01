#!/usr/bin/env python3
"""
Claude Code Router
Routes Claude Code → DeepSeek V3, NVIDIA, or Gemini when limits hit.
"""

import os, json, uuid, socket
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import AsyncGenerator
import uvicorn
import sys

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
        # Using Google's brand new OpenAI-compatible endpoint!
        "base_url":    "https://generativelanguage.googleapis.com/v1beta/openai",
        "api_key":     os.environ.get("GEMINI_API_KEY", ""),
        "big_model":   os.environ.get("GEMINI_BIG_MODEL", "gemini/gemini-3-flash-preview"),
        "small_model": os.environ.get("GEMINI_SMALL_MODEL", "gemini/gemini-2.5-flash-lite"),
        "default_model": os.environ.get("GEMINI_DEFAULT_MODEL", "gemini/gemini-2.5-flash"),
    },
}

def gemini_model_name(model: str) -> str:
    """Strip LiteLLM's 'gemini/' prefix for direct Google API calls."""
    return model.split("/")[-1]

def pick_model(prov: dict, claude_model: str) -> str:
    if PROVIDER == "gemini":
        if "opus" in claude_model: return gemini_model_name(prov["big_model"])
        elif "haiku" in claude_model: return gemini_model_name(prov["small_model"])
        else: return gemini_model_name(prov.get("default_model", prov["big_model"]))
    else:
        return prov["small_model"] if "haiku" in claude_model else prov["big_model"]

@app.get("/health")
async def health():
    prov = PROVIDERS[PROVIDER]
    return {
        "status":   "ok",
        "provider": PROVIDER,
        "model":    pick_model(prov, "claude-3-5-sonnet"),
        "key_set":  bool(prov["api_key"]),
        "port":     PORT,
    }

@app.get("/ping")
async def ping():
    prov = PROVIDERS[PROVIDER]
    if not prov["api_key"]:
        return JSONResponse({"status": "error", "reason": f"No API key for '{PROVIDER}'"}, status_code=500)

    payload = {
        "model":      pick_model(prov, "claude-3-5-sonnet"),
        "messages":   [{"role": "user", "content": "Hi! Reply with only the word: PONG"}],
        "max_tokens": 10,
        "stream":     False,
    }
    
    if PROVIDER == "nvidia":
        payload["extra_body"] = {"chat_template_kwargs": {"thinking": True}}
        
    headers = {"Authorization": f"Bearer {prov['api_key']}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(f"{prov['base_url']}/chat/completions", json=payload, headers=headers)
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            return {"status": "ok", "provider": PROVIDER, "reply": reply.strip() if reply else ""}
        return JSONResponse({"status": "error", "http": r.status_code, "body": r.text}, status_code=r.status_code)
    except Exception as e:
        return JSONResponse({"status": "error", "reason": str(e)}, status_code=500)


def conv_messages(body: dict) -> list:
    msgs = []
    if sys := body.get("system"):
        text = sys if isinstance(sys, str) else "\n".join(b.get("text", "") for b in sys if b.get("type") == "text")
        if text: msgs.append({"role": "system", "content": text})

    for m in body.get("messages", []):
        role, content = m["role"], m["content"]
        if isinstance(content, str):
            msgs.append({"role": role, "content": content})
            continue

        if role == "user":
            tool_results = [b for b in content if b.get("type") == "tool_result"]
            text_blocks  = [b for b in content if b.get("type") == "text"]
            
            if PROVIDER == "gemini" and tool_results:
                # Gemini Bug Workaround: Flatten tool history to avoid thought_signature errors
                parts = []
                if text_blocks:
                    parts.append({"type": "text", "text": "\n".join(b.get("text", "") for b in text_blocks)})
                
                for tr in tool_results:
                    tc = tr.get("content", "")
                    if isinstance(tc, str):
                        parts.append({"type": "text", "text": f"[Tool Result]:\n{tc}"})
                    elif isinstance(tc, list):
                        for b in tc:
                            if b.get("type") == "text":
                                parts.append({"type": "text", "text": f"[Tool Result]:\n{b['text']}"})
                            elif b.get("type") == "image":
                                src = b.get("source", {})
                                if src.get("type") == "base64":
                                    parts.append({"type": "image_url", "image_url": {
                                        "url": f"data:{src['media_type']};base64,{src['data']}"}})
                
                if all(p["type"] == "text" for p in parts):
                    msgs.append({"role": "user", "content": "\n\n".join(p["text"] for p in parts)})
                else:
                    msgs.append({"role": "user", "content": parts})
                    
            else:
                # Standard OpenAI format for DeepSeek/NVIDIA
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
                                    "url": f"data:{src['media_type']};base64,{src['data']}"}})
                    msgs.append({"role": "user", "content": parts or ""})

        elif role == "assistant":
            tool_uses   = [b for b in content if b.get("type") == "tool_use"]
            text_blocks = [b for b in content if b.get("type") == "text"]
            
            if PROVIDER == "gemini" and tool_uses:
                # Gemini Bug Workaround: Flatten tool calls into text
                text_str = ""
                if text_blocks:
                    text_str += "\n".join(b.get("text", "") for b in text_blocks) + "\n\n"
                for tu in tool_uses:
                    args_str = json.dumps(tu.get("input", {}))
                    text_str += f"[Called Tool: {tu['name']} with arguments: {args_str}]\n"
                msgs.append({"role": "assistant", "content": text_str.strip()})
            else:
                # Standard OpenAI formatting
                out = {"role": "assistant", "content": "\n".join(b.get("text", "") for b in text_blocks)}
                if tool_uses:
                    out["tool_calls"] = [
                        {"id": tu.get("id", f"call_{i}"), "type": "function",
                         "function": {"name": tu["name"], "arguments": json.dumps(tu.get("input", {}))}}
                        for i, tu in enumerate(tool_uses)
                    ]
                msgs.append(out)
                
    return msgs