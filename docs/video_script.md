# Foundry: Video Submission Script (3 Minutes)

## Scene 1: The Problem (0:00 - 0:30)
**Visual:** Split screen. Left side: "Manual Annotation" with a clock spinning fast and $$$ signs rising. Right side: "Foundry" logo with a clean, calm interface.

**Voiceover:**
"Building computer vision models is exciting. Creating the datasets to train them? That's a nightmare.
It takes hundreds of hours of manual labor and costs thousands of dollars just to get started.
For small businesses and rapid prototyping, this bottleneck is a dealbreaker.
We asked: What if AI agents could do this work for us?"

## Scene 2: The Solution - Why Agents? (0:30 - 1:00)
**Visual:** Animated diagram showing the three agents (Miner, Curator, Annotator) appearing one by one.

**Voiceover:**
"Enter Foundry. A multi-agent system powered by Google Gemini 2.5 Flash.
We didn't just write a script; we built a team of specialized agents.
The **Miner Agent** explores the web for images.
The **Curator Agent** acts as a quality gatekeeper, filtering out irrelevant data.
And the **Annotator Agent** uses vision capabilities to detect objects and draw bounding boxes.
Each agent is an expert in its own domain."

## Scene 3: Architecture & ADK (1:00 - 1:45)
**Visual:** Show the ADK architecture diagram (LoopAgent -> SequentialAgent). Highlight the "Loop" and "Sequence" blocks.

**Voiceover:**
"To orchestrate this team, we used the Google Agent Development Kit.
We implemented a **Sequential Agent** pattern to define the workflow: Mine, then Curate, then Annotate.
But a linear path isn't enough. We wrapped this in a **Loop Agent** that intelligently manages the state.
It checks our progress against the target count and decides whether to spin up another iteration.
This isn't just a loop; it's an autonomous system that manages its own goals."

## Scene 4: Demo (1:45 - 2:30)
**Visual:** Screen recording of the terminal running `python pipeline.py`. Show the "Execution Plan", then the logs scrolling as agents work. Flash to the final `visualize_results.py` output showing annotated images.

**Voiceover:**
"Let's see it in action.
I simply ask: 'Create 10 images of people walking dogs in a park.'
The **Main Agent** parses my natural language request into a structured plan.
The **Miner** finds images. The **Curator** rejects a stock photo that's just a drawing.
The **Annotator** detects both the person and the dog.
And our **Quality Loop**—a self-correction mechanism—reviews the work. If it misses a dog, it catches the mistake and fixes it automatically."

## Scene 5: The Build & Conclusion (2:30 - 3:00)
**Visual:** Quick montage of the code (VS Code), the `config.yaml`, and the GitHub repo URL.

**Voiceover:**
"We built Foundry using Gemini 2.5 Flash for its speed and multimodal capabilities.
We used the ADK for robust orchestration and added parallel processing to make it 3x faster.
Foundry turns a week of manual work into a 5-minute coffee break.
This is the future of dataset creation.
Check out the code on GitHub."
