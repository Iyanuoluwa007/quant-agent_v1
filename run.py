#!/usr/bin/env python3
"""
Startup script that loads .env and runs the trading agent.

Usage:
    python run.py          # Continuous mode (analysis every N minutes)
    python run.py --once   # Single analysis cycle
    python run.py --status # Print portfolio status only
"""
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[OK] Loaded environment from {env_path}")
    else:
        print(f"[!] No .env file found at {env_path}")
        print("    Copy .env.example to .env and fill in your API keys.")
        sys.exit(1)
except ImportError:
    print("[!] python-dotenv not installed. Using system environment variables.")

from agent import main

if __name__ == "__main__":
    main()
