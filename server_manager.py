#!/usr/bin/env python3
"""
LangPlug Server Manager
Clean entry point using modular server management components
"""

import sys
import argparse
import time
from pathlib import Path

# Add management module to path
sys.path.insert(0, str(Path(__file__).parent))

from management.server_manager import ProfessionalServerManager


def main():
    """Main entry point for server management"""
    parser = argparse.ArgumentParser(description="LangPlug Server Manager")
    parser.add_argument("action", nargs="?", default="start",
                      choices=["start", "stop", "restart", "status"],
                      help="Action to perform")
    parser.add_argument("--server", help="Specific server to manage")
    parser.add_argument("--no-monitor", action="store_true", help="Disable health monitoring")
    
    args = parser.parse_args()
    
    # Install required dependencies if needed
    try:
        import psutil
        import requests
    except ImportError:
        print("Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "requests"])
    
    manager = ProfessionalServerManager()
    
    if args.action == "start":
        if args.server:
            success = manager.start_server(args.server)
        else:
            success = manager.start_all()
        
        if not success:
            sys.exit(1)
            
    elif args.action == "stop":
        if args.server:
            manager.stop_server(args.server)
        else:
            manager.stop_all()
            
    elif args.action == "restart":
        if args.server:
            manager.stop_server(args.server)
            time.sleep(2)
            manager.start_server(args.server)
        else:
            manager.restart_all()
            
    elif args.action == "status":
        manager.print_status()
    
    # Keep running if monitoring is enabled
    if args.action == "start" and not args.no_monitor:
        try:
            print("\nServers are running with health monitoring. Press Ctrl+C to stop...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            manager.stop_all()


if __name__ == "__main__":
    main()