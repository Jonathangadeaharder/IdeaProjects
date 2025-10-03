#!/usr/bin/env python3
"""
Command Line Interface for LangPlug Server Manager
"""

import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from management.server_manager import ProfessionalServerManager


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python cli.py [start|stop|restart|status]")
        sys.exit(1)

    command = sys.argv[1].lower()
    manager = ProfessionalServerManager()

    try:
        if command == "start":
            print("Starting all servers...")
            success = manager.start_all()
            if success:
                print("All servers started successfully!")
                sys.exit(0)
            else:
                print("Failed to start some servers.")
                sys.exit(1)

        elif command == "stop":
            print("Stopping all servers...")
            success = manager.stop_all()
            if success:
                print("All servers stopped successfully!")
                sys.exit(0)
            else:
                print("Failed to stop some servers.")
                sys.exit(1)

        elif command == "restart":
            print("Restarting all servers...")
            success = manager.restart_all()
            if success:
                print("All servers restarted successfully!")
                sys.exit(0)
            else:
                print("Failed to restart some servers.")
                sys.exit(1)

        elif command == "status":
            print("Server Status:")
            manager.print_status()
            sys.exit(0)

        else:
            print(f"Unknown command: {command}")
            print("Available commands: start, stop, restart, status")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
