# Neurolinked Enterprise v3.0 User Guide

Welcome to the Neurolinked cognitive runtime. This system is designed to coordinate multiple AI agents to solve complex tasks.

## How to use the system

Even if you have never coded before, you can interact with and extend this system.

### 1. Viewing the Live Dashboard
To see what the AI is thinking in real-time:
1. Open the **"Ports"** tab in your environment.
2. Find **Port 3000** and click the link.
3. This opens a dashboard showing every "thought" (event) the system generates.

### 2. Running a Task
You can trigger the AI to perform a task by running the demo script:
- Open a terminal and type: `python run_demo.py`
- This will inject a task (e.g., "Deploy security patches") and you can watch the agents coordinate on the dashboard.

### 3. Adding New "Skills"
Skills are tools the AI can use. Currently, it has:
- `write_file`: Can save text to files.
- `web_search`: Can find information.

To add a new skill, you (or an AI assistant like Copilot) can add a few lines to `src/neurolinked/core/runtime.py` in the `_init_skills` method.

## System Architecture

- **Ruflo (Planner)**: Breaks big tasks into small steps.
- **Octgent (Executor)**: Performs the steps using available skills.
- **ECC (Validator)**: Checks if the work was done correctly.
- **Reward Engine**: Learns from successes and failures.

## Troubleshooting

If the dashboard says "Offline", make sure the background runtime is running:
`python run_background.py`
