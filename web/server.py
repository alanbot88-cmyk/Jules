"""FastAPI Web Server for Jules Dashboard"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
import uvicorn
from pathlib import Path

app = FastAPI(title="Jules Dashboard", version="3.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RuntimeState:
    """Global runtime state for dashboard"""
    def __init__(self, runtime):
        self.runtime = runtime
        self.connected_clients: List[WebSocket] = []
        self.task_queue: List[Dict] = []
        self.metrics = {
            "total_events": 0,
            "active_agents": len(runtime.agents),
            "uptime_seconds": 0,
            "last_event_time": None
        }

runtime_state: Optional[RuntimeState] = None

# ==================== Models ====================
class TaskRequest(BaseModel):
    task_id: str
    description: str
    priority: int = 1

class AgentStatus(BaseModel):
    agent_id: str
    status: str
    region: str
    tasks_completed: int

class SystemMetrics(BaseModel):
    total_events: int
    active_agents: int
    uptime_seconds: int
    agents: List[AgentStatus]
    event_history_count: int

# ==================== HTTP Endpoints ====================

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard"""
    return get_dashboard_html()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    if not runtime_state:
        raise HTTPException(status_code=503, detail="Runtime not initialized")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_agents": len(runtime_state.runtime.agents),
        "agents": [
            {
                "id": agent.agent_id,
                "region": str(agent.region),
                "running": agent._is_running
            }
            for agent in runtime_state.runtime.agents
        ]
    }

@app.get("/api/metrics")
async def get_metrics() -> SystemMetrics:
    """Get system metrics"""
    if not runtime_state:
        raise HTTPException(status_code=503, detail="Runtime not initialized")
    
    return SystemMetrics(
        total_events=len(runtime_state.runtime.bus.get_history()),
        active_agents=len(runtime_state.runtime.agents),
        uptime_seconds=int(asyncio.get_event_loop().time()),
        agents=[
            AgentStatus(
                agent_id=agent.agent_id,
                status="running" if agent._is_running else "stopped",
                region=str(agent.region),
                tasks_completed=0
            )
            for agent in runtime_state.runtime.agents
        ],
        event_history_count=len(runtime_state.runtime.bus.get_history())
    )

@app.get("/api/events")
async def get_events(limit: int = 100):
    """Get recent events from the bus"""
    if not runtime_state:
        raise HTTPException(status_code=503, detail="Runtime not initialized")
    
    history = runtime_state.runtime.bus.get_history()
    events = history[-limit:]
    
    return {
        "total": len(history),
        "returned": len(events),
        "events": [
            {
                "id": event.event_id,
                "type": event.event_type,
                "source": event.source_agent,
                "region": str(event.target_region),
                "timestamp": event.timestamp.isoformat() if hasattr(event, 'timestamp') else None,
                "payload": event.payload
            }
            for event in events
        ]
    }

@app.post("/api/tasks/submit")
async def submit_task(task: TaskRequest):
    """Submit a new task to the system"""
    if not runtime_state:
        raise HTTPException(status_code=503, detail="Runtime not initialized")
    
    task_dict = task.dict()
    runtime_state.task_queue.append(task_dict)
    
    # Publish task event to bus
    await runtime_state.runtime.bus.publish(
        from src.neurolinked.core.events import BaseEvent, CognitiveRegion
        BaseEvent(
            source_agent="dashboard",
            event_type="task_submitted",
            payload={"task_id": task.task_id, "description": task.description},
            target_region=CognitiveRegion.PLANNING
        )
    )
    
    logger.info(f"📝 Task submitted via dashboard: {task.task_id}")
    
    return {
        "status": "queued",
        "task_id": task.task_id,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/agents")
async def get_agents():
    """Get all agents information"""
    if not runtime_state:
        raise HTTPException(status_code=503, detail="Runtime not initialized")
    
    return {
        "total": len(runtime_state.runtime.agents),
        "agents": [
            {
                "id": agent.agent_id,
                "type": agent.__class__.__name__,
                "region": str(agent.region),
                "status": "active" if agent._is_running else "inactive"
            }
            for agent in runtime_state.runtime.agents
        ]
    }

# ==================== WebSocket Endpoint ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await websocket.accept()
    runtime_state.connected_clients.append(websocket)
    
    logger.info(f"🔗 Client connected to WebSocket. Total clients: {len(runtime_state.connected_clients)}")
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Connected to Jules Dashboard",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
            elif message.get("type") == "get_state":
                state = await get_dashboard_state()
                await websocket.send_json(state)
    
    except WebSocketDisconnect:
        runtime_state.connected_clients.remove(websocket)
        logger.info(f"🔌 Client disconnected. Remaining clients: {len(runtime_state.connected_clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        runtime_state.connected_clients.remove(websocket)

async def broadcast_update(update_type: str, data: dict):
    """Broadcast update to all connected WebSocket clients"""
    if not runtime_state:
        return
    
    message = {
        "type": update_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    disconnected = []
    for client in runtime_state.connected_clients:
        try:
            await client.send_json(message)
        except:
            disconnected.append(client)
    
    for client in disconnected:
        runtime_state.connected_clients.remove(client)

async def get_dashboard_state() -> dict:
    """Get complete dashboard state"""
    if not runtime_state:
        return {"error": "Runtime not initialized"}
    
    agents_info = [
        {
            "id": agent.agent_id,
            "type": agent.__class__.__name__,
            "region": str(agent.region),
            "status": "✅ Active" if agent._is_running else "⏸️ Inactive"
        }
        for agent in runtime_state.runtime.agents
    ]
    
    events = runtime_state.runtime.bus.get_history()[-50:]
    events_info = [
        {
            "type": event.event_type,
            "source": event.source_agent,
            "region": str(event.target_region)
        }
        for event in events
    ]
    
    return {
        "type": "state_update",
        "metrics": {
            "total_events": len(runtime_state.runtime.bus.get_history()),
            "active_agents": sum(1 for a in runtime_state.runtime.agents if a._is_running),
            "total_agents": len(runtime_state.runtime.agents)
        },
        "agents": agents_info,
        "recent_events": events_info
    }

# ==================== Utilities ====================

def get_dashboard_html() -> str:
    """Generate dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Jules Dashboard - Neurolinked System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
                color: #fff;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            header {
                text-align: center;
                margin-bottom: 40px;
                animation: fadeIn 0.8s ease-in;
            }
            h1 {
                font-size: 2.5em;
                background: linear-gradient(45deg, #00d4ff, #0099ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #b0b0b0;
                font-size: 1.1em;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
                transition: all 0.3s ease;
            }
            .card:hover {
                background: rgba(255, 255, 255, 0.08);
                border-color: rgba(0, 212, 255, 0.3);
                transform: translateY(-5px);
            }
            .card h2 {
                font-size: 1.3em;
                margin-bottom: 15px;
                color: #00d4ff;
            }
            .metric {
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            .metric:last-child { border-bottom: none; }
            .metric-label { color: #b0b0b0; }
            .metric-value {
                font-weight: bold;
                color: #00d4ff;
                font-size: 1.1em;
            }
            .agent-item {
                background: rgba(0, 212, 255, 0.05);
                border-left: 3px solid #00d4ff;
                padding: 12px;
                margin: 8px 0;
                border-radius: 4px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .agent-status {
                font-size: 0.9em;
                padding: 4px 8px;
                background: rgba(0, 255, 0, 0.1);
                border-radius: 4px;
                color: #00ff00;
            }
            .event-log {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
                max-height: 400px;
                overflow-y: auto;
            }
            .event-item {
                background: rgba(255, 255, 255, 0.03);
                padding: 10px;
                margin: 5px 0;
                border-radius: 4px;
                border-left: 2px solid #0099ff;
                font-size: 0.9em;
            }
            .event-type { color: #00d4ff; font-weight: bold; }
            .event-source { color: #b0b0b0; }
            .task-input-area {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 30px;
            }
            input[type="text"],
            textarea,
            input[type="number"] {
                width: 100%;
                padding: 12px;
                margin-bottom: 10px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                color: #fff;
                font-family: inherit;
                transition: all 0.3s ease;
            }
            input:focus,
            textarea:focus {
                background: rgba(255, 255, 255, 0.08);
                border-color: #00d4ff;
                outline: none;
                box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
            }
            button {
                background: linear-gradient(45deg, #00d4ff, #0099ff);
                color: #000;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
            }
            button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
            }
            .status-indicator {
                display: inline-block;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #00ff00;
                animation: pulse 2s infinite;
                margin-right: 8px;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .connection-status {
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 10px 15px;
                background: rgba(0, 255, 0, 0.1);
                border: 1px solid #00ff00;
                border-radius: 6px;
                font-size: 0.9em;
            }
            .connection-status.connected { color: #00ff00; }
            .connection-status.disconnected { 
                color: #ff0000;
                background: rgba(255, 0, 0, 0.1);
                border-color: #ff0000;
            }
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-track {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(0, 212, 255, 0.3);
                border-radius: 10px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: rgba(0, 212, 255, 0.6);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🧠 Jules Dashboard</h1>
                <p class="subtitle">Neurolinked Multi-Agent System v3.0 - Real-time Preview</p>
            </header>

            <div class="task-input-area">
                <h2 style="margin-bottom: 15px; color: #00d4ff;">📝 Submit Task</h2>
                <input type="text" id="taskId" placeholder="Task ID (e.g., task-001)" />
                <textarea id="taskDesc" placeholder="Task Description..." rows="3"></textarea>
                <input type="number" id="priority" placeholder="Priority (1-10)" min="1" max="10" value="5" />
                <button onclick="submitTask()">🚀 Submit Task</button>
            </div>

            <div class="grid">
                <div class="card">
                    <h2>📊 System Metrics</h2>
                    <div class="metric">
                        <span class="metric-label">Total Events:</span>
                        <span class="metric-value" id="totalEvents">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Active Agents:</span>
                        <span class="metric-value" id="activeAgents">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">System Status:</span>
                        <span class="metric-value">
                            <span class="status-indicator"></span>
                            <span id="status">Initializing...</span>
                        </span>
                    </div>
                </div>

                <div class="card">
                    <h2>🤖 Agent Overview</h2>
                    <div id="agentsContainer"></div>
                </div>

                <div class="card">
                    <h2>🔌 Connection Status</h2>
                    <div id="connectionInfo"></div>
                </div>
            </div>

            <div class="event-log">
                <h2 style="margin-bottom: 15px; color: #00d4ff;">📡 Real-time Event Stream</h2>
                <div id="eventContainer"></div>
            </div>
        </div>

        <div class="connection-status connected" id="connStatus">
            <span class="status-indicator"></span>
            <span id="connText">Connecting...</span>
        </div>

        <script>
            let ws;
            let eventCount = 0;
            
            function connectWebSocket() {
                ws = new WebSocket(`ws://${window.location.host}/ws`);
                
                ws.onopen = () => {
                    console.log('✅ Connected to Jules');
                    updateConnectionStatus(true);
                    requestStateUpdate();
                };
                
                ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    handleMessage(message);
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    updateConnectionStatus(false);
                };
                
                ws.onclose = () => {
                    console.log('❌ Disconnected from Jules');
                    updateConnectionStatus(false);
                    setTimeout(connectWebSocket, 3000);
                };
            }
            
            function handleMessage(message) {
                if (message.type === 'state_update') {
                    updateDashboard(message);
                }
            }
            
            function updateDashboard(state) {
                // Update metrics
                document.getElementById('totalEvents').textContent = state.metrics.total_events;
                document.getElementById('activeAgents').textContent = state.metrics.active_agents + '/' + state.metrics.total_agents;
                document.getElementById('status').textContent = 'Operational';
                
                // Update agents
                const agentsContainer = document.getElementById('agentsContainer');
                agentsContainer.innerHTML = state.agents.map(agent => `
                    <div class="agent-item">
                        <div>
                            <strong>${agent.id}</strong>
                            <br><small style="color: #b0b0b0;">${agent.type} (${agent.region})</small>
                        </div>
                        <span class="agent-status">${agent.status}</span>
                    </div>
                `).join('');
                
                // Update events
                const eventContainer = document.getElementById('eventContainer');
                eventContainer.innerHTML = state.recent_events.map(evt => `
                    <div class="event-item">
                        <div class="event-type">${evt.type}</div>
                        <div class="event-source">From: ${evt.source} → ${evt.region}</div>
                    </div>
                `).join('');
            }
            
            function requestStateUpdate() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({type: 'get_state'}));
                }
            }
            
            function updateConnectionStatus(connected) {
                const status = document.getElementById('connStatus');
                const text = document.getElementById('connText');
                if (connected) {
                    status.classList.remove('disconnected');
                    status.classList.add('connected');
                    text.textContent = 'Connected to Jules';
                } else {
                    status.classList.remove('connected');
                    status.classList.add('disconnected');
                    text.textContent = 'Disconnected';
                }
            }
            
            async function submitTask() {
                const taskId = document.getElementById('taskId').value;
                const taskDesc = document.getElementById('taskDesc').value;
                const priority = document.getElementById('priority').value;
                
                if (!taskId || !taskDesc) {
                    alert('Please fill in all fields');
                    return;
                }
                
                try {
                    const response = await fetch('/api/tasks/submit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            task_id: taskId,
                            description: taskDesc,
                            priority: parseInt(priority)
                        })
                    });
                    
                    if (response.ok) {
                        document.getElementById('taskId').value = '';
                        document.getElementById('taskDesc').value = '';
                        alert('✅ Task submitted successfully!');
                        requestStateUpdate();
                    }
                } catch (e) {
                    alert('❌ Error: ' + e.message);
                }
            }
            
            // Update dashboard every 2 seconds
            setInterval(requestStateUpdate, 2000);
            
            // Connect on load
            window.addEventListener('load', connectWebSocket);
        </script>
    </body>
    </html>
    """

async def start_web_server(runtime):
    """Start the web server"""
    global runtime_state
    runtime_state = RuntimeState(runtime)
    
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()
