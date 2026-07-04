# Problem Interpretation

Last updated: 2026-07-04

This file summarizes the current interpretation from the briefing photos and teacher comments. It should be updated after more official guidance is provided.

## Briefing Facts

- Track: large model / data.
- Core task: build an Agentic Harness based on Intern-S2-Preview.
- Required final demo must use Intern-S2-Preview API as the core model call.
- Development may use other auxiliary models or tools.
- Lab ecosystem mentioned in the briefing:
  - Intern-S2-Preview, unlimited API during the event.
  - Sciverse scientific data layer: <https://sciverse.space/>
  - MinerU document parsing: <https://mineru.net/>
  - OpenDataLab / Wanjuan data, XTuner fine-tuning, LMDeploy deployment, pretraining/evolution/data pipeline.
- Teacher framing: data and AI should drive each other.
- Official text confirms that the World Cup team direction targets the 2026 Canada/Mexico/USA World Cup Group E first-round match where Germany defeats Curacao 7:1.
- Official text requires code/config to expose API Base URL and API Key settings for organizer-side judging.

## Slide Details From Photos

The first slide frames the task as:

```text
Agent = LLM + Harness
```

Example directions shown:

- Code vulnerability detection.
- PPT generation and beautification.
- World Cup video commentary.
- Academic paper review.

Harness capabilities called out on the slide:

- Tool calling.
- Skills mechanism.
- Memory system.
- Sandbox isolation.

The second slide emphasizes broader research goals:

- Human-AI collaborative scientific research paradigm.
- Long-horizon tasks from hours to days.
- Continual and active learning through environment interaction.
- Unified representation and learning for scientific multimodality.
- Next-generation base model architecture.
- Inference-enhanced pretraining paradigm.

The third slide lists the contest directions and target goals:

| Direction | Type | Target |
| --- | --- | --- |
| Code vulnerability detection harness | Individual | Analyze open-source repositories, find security risks, and suggest fixes. |
| PPT generation and beautification harness | Individual | Automatically retrieve information and generate visually appealing PPT. |
| World Cup video commentary harness | Team | Identify key match events and generate energetic commentary scripts. |
| Academic paper review harness | Team | Read papers, summarize methods, and generate illustrated academic reviews. |

Contest notes visible on the slide:

- Participants choose one direction.
- Final presentation must use Intern-S2-Preview API as the core model call.
- Other models may assist during development.

## Current Candidate Directions

### World Cup Video Commentary Harness

Initial preference: strong.

Why it is attractive:

- Strong demo appeal and roadshow popularity potential.
- Naturally shows multimodal tool orchestration: video, audio, OCR, event detection, timeline construction, and text generation.
- Easy to explain as a harness rather than a prompt wrapper because the system needs extraction, verification, and script generation stages.

Primary risks:

- Video copyright and data availability.
- Event detection quality under a 24h build limit.
- Need to control scope: use clips, key events, and traceable evidence rather than full-match understanding.

### Academic Paper Review Harness

Initial preference: backup / strong alternative.

Why it is attractive:

- Closely aligned with Sciverse and MinerU.
- Evaluation is easier to defend with citations, source grounding, and structured review rubrics.
- Strong fit with scientific research and social value.

Primary risks:

- Less visually exciting for a roadshow.
- Many teams may choose this because it is directly aligned with the lab ecosystem.
- Needs careful hallucination control and citation verification to be credible.

## Current Recommendation

Default to the World Cup video commentary direction, but keep the academic review direction as a fallback until API modality, data access, and official task details are confirmed.

The MVP should avoid claiming full automated professional commentary. A defensible target is:

> Given a short soccer match clip, the harness extracts key evidence, builds a timestamped event timeline, asks Intern-S2-Preview to generate a Chinese energetic commentary script, verifies factual consistency, and outputs script plus trace.
