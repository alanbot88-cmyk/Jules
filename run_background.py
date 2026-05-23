import asyncio
import sys
import os
from loguru import logger
from src.neurolinked.core.runtime import Runtime
from src.neurolinked.core.events import BaseEvent

# Configure logger
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def main():
    logger.info("=== Starting Neurolinked v3.0 Background Runtime ===")

    runtime = Runtime()
    await runtime.start()

    tasks = [
        "Optimize neural pathways",
        "Synchronize prefrontal cortex",
        "Clear hippocampus cache",
        "Execute motor response sequence"
    ]

    try:
        while True:
            for task in tasks:
                logger.info(f"Background task: {task}")
                await runtime.bus.publish(BaseEvent(
                    source_agent="background_worker",
                    event_type="task_request",
                    payload={"description": task}
                ))
                await asyncio.sleep(10) # Run a task every 10 seconds
    except asyncio.CancelledError:
        await runtime.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
