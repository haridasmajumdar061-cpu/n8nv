from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from jinja2 import Template
from rich.console import Console

from .llm import LLMClient
from .templates import (
    generate_ideas,
    generate_metadata,
    generate_script,
    generate_shorts,
    generate_thumbnail_text,
)
from .utils import load_yaml, make_output_dir, read_text, write_json, write_text

console = Console()


def _parse_numbered_list(text: str) -> list[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Remove leading numbering like "1." or "1)"
        if line[0].isdigit():
            while line and (line[0].isdigit() or line[0] in {".", ")", "-"}):
                line = line[1:].lstrip()
        lines.append(line)
    return lines


def _render_prompt(prompt_path: Path, context: dict[str, Any]) -> str:
    template = Template(read_text(prompt_path))
    return template.render(**context)


def run_pipeline(
    root_dir: Path,
    idea_index: int | None = None,
    idea_override: str | None = None,
    output_dir: Path | None = None,
) -> Path:
    load_dotenv()

    config = load_yaml(root_dir / "config" / "channel.yaml")
    provider = os.getenv("LLM_PROVIDER") or config["llm"]["provider"]
    model = os.getenv("OPENAI_MODEL") or config["llm"]["model"]
    temperature = float(config["llm"].get("temperature", 0.6))
    max_tokens = int(config["llm"].get("max_tokens", 1200))

    prompts_dir = root_dir / "config" / "prompts"
    context = config | {
        "content": config["content"],
        "shorts": config["shorts"],
    }

    if provider == "mock":
        ideas = generate_ideas(config)
    else:
        client = LLMClient(provider=provider, model=model, api_key=os.getenv("OPENAI_API_KEY"))
        prompt = _render_prompt(prompts_dir / "idea.txt", context)
        ideas = _parse_numbered_list(client.generate(prompt, max_tokens=max_tokens, temperature=temperature))

    if idea_override:
        idea = idea_override
    else:
        index = idea_index if idea_index is not None else 0
        if index < 0 or index >= len(ideas):
            index = 0
        idea = ideas[index]

    if provider == "mock":
        script = generate_script(config, idea)
        metadata = generate_metadata(config, idea)
        shorts = generate_shorts(config, idea)
        thumbnails = generate_thumbnail_text(idea)
    else:
        client = LLMClient(provider=provider, model=model, api_key=os.getenv("OPENAI_API_KEY"))
        script = client.generate(
            _render_prompt(prompts_dir / "script.txt", context | {"idea": idea}),
            max_tokens=max_tokens,
            temperature=temperature,
        )
        metadata_raw = client.generate(
            _render_prompt(prompts_dir / "metadata.txt", context | {"idea": idea}),
            max_tokens=max_tokens,
            temperature=temperature,
        )
        try:
            metadata = json.loads(metadata_raw)
        except json.JSONDecodeError:
            metadata = {"raw": metadata_raw}
        shorts = _parse_numbered_list(
            client.generate(
                _render_prompt(prompts_dir / "shorts.txt", context | {"idea": idea}),
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )
        thumbnails = _parse_numbered_list(
            client.generate(
                _render_prompt(prompts_dir / "thumbnail.txt", context | {"idea": idea}),
                max_tokens=max_tokens,
                temperature=temperature,
            )
        )

    base_dir = output_dir or Path(config["output"]["base_dir"])
    out_dir = make_output_dir(root_dir / base_dir, config["output"]["folder_prefix"])

    write_text(out_dir / "idea.txt", idea)
    write_text(out_dir / "ideas.txt", "\n".join(ideas))
    write_text(out_dir / "script.txt", script)
    write_json(out_dir / "metadata.json", metadata)
    write_text(out_dir / "shorts.txt", "\n".join(shorts))
    write_text(out_dir / "thumbnail.txt", "\n".join(thumbnails))
    write_json(
        out_dir / "manifest.json",
        {
            "provider": provider,
            "model": model,
            "idea": idea,
            "config": config,
        },
    )

    console.print(f"[green]Generated content pack:[/green] {out_dir}")
    return out_dir


def list_ideas(root_dir: Path) -> list[str]:
    load_dotenv()
    config = load_yaml(root_dir / "config" / "channel.yaml")
    provider = os.getenv("LLM_PROVIDER") or config["llm"]["provider"]
    model = os.getenv("OPENAI_MODEL") or config["llm"]["model"]
    temperature = float(config["llm"].get("temperature", 0.6))
    max_tokens = int(config["llm"].get("max_tokens", 1200))

    prompts_dir = root_dir / "config" / "prompts"
    context = config | {
        "content": config["content"],
        "shorts": config["shorts"],
    }

    if provider == "mock":
        return generate_ideas(config)

    client = LLMClient(provider=provider, model=model, api_key=os.getenv("OPENAI_API_KEY"))
    prompt = _render_prompt(prompts_dir / "idea.txt", context)
    return _parse_numbered_list(client.generate(prompt, max_tokens=max_tokens, temperature=temperature))
