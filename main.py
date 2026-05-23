#!/usr/bin/env python3
"""
Main entry point for Neurolinked Jules System with Web Dashboard
"""
import asyncio
import os
from dotenv import load_dotenv
from loguru import logger
from src.neurolinked.core.runtime import Runtime
from web.server import start_web_server

# Configure logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Load environment variables
load_dotenv()

async def main():
    """Initialize and run the Neurolinked Runtime with Web Dashboard"""
    runtime = Runtime()
    
    logger.info("=" * 70)
    logger.info("🧠 JULES - Neurolinked Multi-Agent System v3.0")
    logger.info("=" * 70)
    
    try:
        # Start the runtime
        await runtime.start()
        
        logger.info("✅ System fully operational and ready for tasks!")
        logger.info("\n📊 Starting Web Dashboard...")
        
        # Start web server in a background task
        web_task = asyncio.create_task(start_web_server(runtime))
        
        logger.info("🌐 Dashboard available at: http://localhost:8000")
        logger.info("📡 WebSocket at: ws://localhost:8000/ws")
        logger.info("\nWaiting for tasks... (Press Ctrl+C to shutdown)\n")
        
        # Run until interrupted
        await runtime.run_until_interrupted()
        
    except KeyboardInterrupt:
        logger.info("\n⏹️  Shutdown signal received...")
    except Exception as e:
        logger.error(f"❌ Runtime error: {e}", exc_info=True)
    finally:
        await runtime.stop()
        logger.info("💤 System shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
