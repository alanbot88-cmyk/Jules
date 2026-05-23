# 🧠 Jules - Neurolinked Multi-Agent System

## System Overview

Jules is an advanced multi-agent orchestration system built on the Neurolinked framework. It integrates multiple AI models and specialized agents to handle complex task decomposition, execution, validation, and reward optimization.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Add your API keys to .env
```

### Running the System

```bash
# Start Jules with Web Dashboard
python main.py
```

Then open your browser to: **http://localhost:8000**

## 📊 Dashboard Features

### Real-time Monitoring
- **Live Agent Status**: See all 9 agents and their operational status
- **Event Stream**: Real-time event log showing cognitive bus activity
- **System Metrics**: Total events processed, active agents, system health

### Task Submission
- Submit tasks through the web interface
- Set priority levels for task processing
- Track task execution in real-time

### Agent Management
The system includes 9 specialized agents:

1. **RufloAgent** - Ruflo (Task Planning & Decomposition)
2. **OctgentAgent** - Oct-Gent (General Execution)
3. **ECCAgent** - Error Correction & Consistency (Validation)
4. **SupervisorAgent** - Task Orchestration & Coordination
5. **WatchdogAgent** - System Health Monitoring
6. **MemoryAgent** - Episodic Memory Management
7. **PersistenceAgent** - State Persistence
8. **UIRenderAgent** - User Interface Rendering
9. **RewardEngine** - Reinforcement Learning & Optimization

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────┐
│         Cognitive Bus (Event Hub)           │
│  - Event Publishing & Subscription          │
│  - Deterministic Event Propagation          │
│  - Event History & Telemetry               │
└─────────────────────────────────────────────┘
           ↑                    ↑
      ┌────┴────┬───────────────┴────┐
      │          │                    │
  ┌───▼──┐  ┌───▼──┐  ┌──────────┐  ┌▼────┐
  │Planning  │Execution│Validation│ │Memory│
  │Region   │Region  │Region    │ │Region│
  └────────┘ └───────┘ └──────────┘ └─────┘

```

### Data Flow

1. **Task Submission** → Task arrives at Planning Region
2. **Decomposition** → Ruflo AI generates step-by-step plan
3. **Execution** → Oct-Gent executes each step sequentially
4. **Validation** → ECC validates execution results
5. **Memory** → Results stored in episodic memory
6. **Reward** → Reward Engine updates policy

## 🔌 Web API Endpoints

### HTTP Endpoints

```
GET  /                    - Dashboard UI
GET  /api/health         - System health check
GET  /api/metrics        - Current system metrics
GET  /api/events         - Event history
GET  /api/agents         - Agent information
POST /api/tasks/submit   - Submit new task
```

### WebSocket

```
WS ws://localhost:8000/ws
```

Messages:
- `{"type": "ping"}` → Connection test
- `{"type": "get_state"}` → Request current state

## 📈 Event Types

- `task_submitted` - New task received
- `task_plan_generated` - Decomposition complete
- `execution_request` - Execution started
- `execution_completed` - Step execution done
- `validation_result` - Validation complete
- `error_detected` - Error occurred
- `health_alert` - System health warning

## 🎯 Cognitive Regions

1. **PLANNING** - Task decomposition and planning
2. **EXECUTION** - Action execution
3. **VALIDATION** - Error correction and consistency
4. **MEMORY** - Episodic and semantic memory
5. **ORCHESTRATION** - Agent coordination
6. **REWARD** - Learning and optimization

## 📊 System Metrics Tracked

- Total events processed
- Active agents count
- System uptime
- Agent status (running/stopped)
- Event history size
- Task queue depth
- Validation success rate
- Execution latency

## 🔧 Configuration

Edit `.env` to configure:

```env
GEMINI_API_KEY=your_key        # AI Task Decomposition
GROQ_API_KEY=your_key          # Execution Engine
DEEPSEEK_API_KEY=your_key      # Validation Engine
WEB_HOST=0.0.0.0               # Web Server Host
WEB_PORT=8000                  # Web Server Port
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src
```

## 📝 Example Task

```json
{
  "task_id": "task-001",
  "description": "Analyze customer feedback and generate insights",
  "priority": 8
}
```

## 🔐 Security

- API keys stored in `.env` (not in version control)
- WebSocket connections authenticated
- Input validation on all endpoints
- CORS enabled for dashboard

## 📚 Documentation

For detailed documentation, see:
- `src/neurolinked/core/` - Core framework
- `src/neurolinked/agents/` - Agent implementations
- `web/` - Web dashboard code

## 🐛 Troubleshooting

### WebSocket Connection Issues
```
Check: http://localhost:8000/api/health
Ensure uvicorn server is running on port 8000
```

### Agent Not Starting
```
Check logs for agent initialization errors
Verify all dependencies in requirements.txt are installed
```

### Task Not Processing
```
Check event stream in dashboard
Verify Planning Region agent is active
Check cognitive bus for event propagation
```

## 📜 License

MIT License - See LICENSE file

## 👥 Contributing

Contributions welcome! Please follow:
1. Create feature branch
2. Add tests
3. Submit pull request

---

**Built with ❤️ using Python, FastAPI, and Neurolinked Framework**
