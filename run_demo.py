import asyncio
import sys
from loguru import logger
from src.neurolinked.core.runtime import Runtime
from src.neurolinked.core.events import BaseEvent

# Configure logger for the demo
logger.remove()
logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def main():
    logger.info("=== Starting Neurolinked v3.0 Demo Pipeline ===")

    runtime = Runtime()

    # Start the runtime
    await runtime.start()

    logger.info("Injecting task: 'Deploy security patches to production'")

    # Subscribe to the final event in the chain for demo termination
    completion_future = asyncio.get_running_loop().create_future()

    async def monitor_reward(event: BaseEvent):
        logger.info(f"DEMO MONITOR: Received reward update: {event.payload}")
        if not completion_future.done():
            completion_future.set_result(True)

    runtime.bus.subscribe("reward_update", monitor_reward)

    # Initial trigger
    await runtime.bus.publish(BaseEvent(
        source_agent="user_interface",
        event_type="task_request",
        payload={"description": "Deploy security patches to production"}
    ))

    try:
        # Wait for the full cognitive loop to finish (up to 5 seconds)
        await asyncio.wait_for(completion_future, timeout=5.0)
        logger.info("=== Cognitive Loop Completed Successfully ===")
    except asyncio.TimeoutError:
        logger.error("=== Demo timed out before completing loop ===")

    # Brief pause to see final logs
    await asyncio.sleep(1)

    await runtime.stop()
    logger.info("=== Demo Finished ===")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
