from __future__ import annotations

from typing import Any


def _title_case(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split())


def generate_ideas(config: dict[str, Any]) -> list[str]:
    niche = config["channel"]["niche"]
    ideas = [
        f"10 surprising facts about {niche}",
        f"Why {niche} matters more than you think",
        f"The biggest myths about {niche} (debunked)",
        f"A beginner's guide to {niche} in 6 minutes",
        f"Top 5 mistakes people make with {niche}",
        f"The untold history of {niche}",
        f"{niche}: the simple explanation everyone needs",
        f"Can you spot the truth in {niche}?",
        f"The fastest way to learn {niche}",
        f"The future of {niche} in the next 5 years",
    ]
    return ideas


def generate_script(config: dict[str, Any], idea: str) -> str:
    include_broll = bool(config["content"].get("include_broll_notes"))
    include_sfx = bool(config["content"].get("include_sound_design_notes"))
    sections = config["content"]["video_structure"]

    broll = " [BROLL: relevant visuals]" if include_broll else ""
    sfx = " [SFX: subtle whoosh]" if include_sfx else ""

    lines = [
        "HOOK:",
        f"{idea} is not what most people think.{broll}{sfx}",
        "",
        "SETUP:",
        "In the next few minutes, we will break it down in the simplest way possible.",
        "",
        "MAIN POINTS:",
        "1) The core idea in one sentence.",
        "2) A quick example everyone can relate to.",
        "3) The surprising part most people miss.",
        "",
        "RECAP:",
        "Let us quickly summarize the key takeaways.",
        "",
        "CALL TO ACTION:",
        "If this helped you, like the video and subscribe for more.",
        "",
    ]
    # If the user customized sections, include a small marker for each.
    lines.append("STRUCTURE CHECK:")
    for section in sections:
        lines.append(f"- {section}")

    return "\n".join(lines)


def generate_metadata(config: dict[str, Any], idea: str) -> dict[str, Any]:
    niche = config["channel"]["niche"]
    titles = [
        f"{_title_case(idea)}",
        f"{_title_case(niche)} Explained in Minutes",
        f"The Truth About {_title_case(niche)}",
        f"What Everyone Gets Wrong About {_title_case(niche)}",
        f"{_title_case(niche)}: The Simple Version",
    ]
    description = (
        f"In this video we break down: {idea}. You will learn the core idea, a simple example, "
        f"and the most surprising insight most people miss. If you enjoy quick, clear explainers "
        f"about {niche}, subscribe and turn on notifications for weekly uploads."
    )
    tags = [
        niche,
        "bangla",
        "explain",
        "facts",
        "learning",
        "education",
        "quick",
        "short",
        "tutorial",
        "explainer",
        "curious",
        "knowledge",
        "story",
        "youtube",
        "viral",
    ]
    return {
        "titles": titles,
        "description": description,
        "tags": tags,
        "pinned_comment": "Which idea should we cover next?",
    }


def generate_shorts(config: dict[str, Any], idea: str) -> list[str]:
    count = int(config["shorts"]["count"])
    shorts = []
    for idx in range(count):
        shorts.append(
            f"{idx + 1}. Hook: {idea} in 10 seconds. "
            "Core: One simple fact people ignore. CTA: Like and subscribe."
        )
    return shorts


def generate_thumbnail_text(idea: str) -> list[str]:
    return [
        "MIND BLOWN",
        "DID YOU KNOW",
        "SHOCKING TRUTH",
        "HIDDEN FACTS",
        "WATCH THIS",
    ]
