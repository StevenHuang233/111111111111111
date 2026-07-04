# Official Problem Statement Notes

Last updated: 2026-07-04

This is a repository-safe, redacted copy of the problem statement provided by the organizer. Private download credentials, API keys, and non-public attachment links must not be committed.

## Title

基于 Intern-S2-Preview 的 Agentic Harness 开发挑战。

## Core Definition

The contest asks teams to build an Agentic Harness around the organizer-provided Intern-S2-Preview API.

The harness should be more than a direct model API wrapper. It should be an executable, feedback-driven, verifiable task-completion system including:

- Task decomposition.
- Tool calling, such as file I/O or code execution.
- Context management.
- Result checking.
- Iterative optimization.
- Optional advanced mechanisms such as skills, memory, sandboxing, prompt-cache-aware prompt design, context compression, sub-agents, multi-agent collaboration, and plan mode.

## Available Directions

| Direction | Type | Required Goal |
| --- | --- | --- |
| Code vulnerability detection harness | Individual | Analyze either the Linux codebase or the verl codebase, identify security risks, explain causes, and suggest fixes or patches. |
| PPT generation and beautification harness | Individual | Generate a visually appealing presentation on "Shanghai AI Laboratory AGI4S research work in the past six months", preferably using MinerU and Sciverse if relevant. |
| World Cup video commentary harness | Team | For the 2026 Canada/Mexico/USA World Cup Group E first-round match where Germany defeats Curacao 7:1, generate commentary scripts, identify key events, and produce energetic style commentary or structured outputs for dubbing, subtitles, and highlight narration. |
| Academic literature review harness | Team | Generate an illustrated review on "World Models" by reading, organizing, classifying, and summarizing papers while avoiding hallucinated citations and unsupported claims. |

## Model Usage Rules

- During harness development, teams may use arbitrary large models or development tools to help design and implement the system.
- In the final task run, live demo, and judging tests, the core large-model call inside the harness must use the organizer-provided Intern-S2-Preview API.
- The organizer only provides Intern-series API resources, not third-party commercial model APIs.
- If other models or tools are used during development, the final submitted and demonstrated version must be switchable to Intern-S2-Preview and run correctly.
- The submitted code/config must expose standard API Base URL and API Key settings, preferably through environment variables.

## Provided Resources

- Intern-S2-Preview API key entry: <https://chat.intern-ai.org.cn>
- MinerU intelligent document parsing: <https://mineru.net/>
- MinerU API docs: <https://mineru.net/apiManage/docs>
- Sciverse scientific literature/data layer: <https://sciverse.space/>
- Sciverse docs: <https://sciverse.space/docs#sciverse/api>
- Organizer-provided baseline outputs are referenced in the official attachments.
- The organizer provides a full-match video for the World Cup commentary direction. The download address and access password are intentionally not stored in this repository.

## Delivery Requirements

Basic requirements:

- Complete a runnable harness prototype for the selected direction, with source code and necessary run instructions.
- Provide API Base URL and API Key configuration interfaces so organizers can insert a fresh Intern-S2-Preview API key and run the system.
- Submitted source code will be checked for semantic similarity. Excessive similarity to another team's code may be treated as plagiarism.
- Show outputs for the selected task direction, such as a security report, PPT, literature review, World Cup commentary text, or edited highlight video.
- Submit an analysis table describing Intern-S2-Preview limitations and possible improvements.
- In the presentation, clearly explain harness design, implementation, run results, and result analysis.
- If the team has more than one member, explain each member's responsibilities and contribution percentage in the presentation.

Bonus items:

- Provide a live demo showing the harness from input task to output result. If runtime is long, show a recorded fast-forward result.
- Support advanced mechanisms mentioned in the harness introduction, such as skills, memory, or sandboxing.

## Harness Design Points From Appendix

The appendix emphasizes that the goal is not to simply call Intern-S2-Preview inside existing coding agents. Teams should design their own harness and connect Intern-S2-Preview to it.

The agent loop should consider:

- What tools the task needs.
- How tool descriptions are written into prompts.
- Which paths each tool may access.
- How to handle tool failures.
- How to handle timeouts.
- How to truncate overly long tool outputs.
- Whether MCP is useful for managing many tools.

Skills system considerations:

- Progressive disclosure to save tokens and avoid context overload.
- Unified skill management.
- Skill discovery and loading.
- Context injection strategy.
- Skill unloading.

Memory system considerations:

- Progressive loading.
- Layered memory management.
- Retrieval strategy.
- Injection strategy.
- Manual maintenance and automatic summarization/write-back.
- Update strategy.
- Self-improvement based on experience extraction.

Sandbox considerations:

- Filesystem isolation.
- Snapshot rollback.
- Network control.
- Host-sandbox communication.

