#!/usr/bin/env python3
"""
Port cleanup utility for Backend startup
Kills any process using the specified port before starting
"""

import os
import sys
import subprocess


def kill_process_on_port(port):
    """Kill any process using the specified port"""
    print(f"[CLEANUP] Checking port {port}...")

    try:
        # Windows command to find and kill process on port
        result = subprocess.run(
            f'powershell.exe -Command "Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}"',
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"[CLEANUP] Port {port} cleared successfully")
        else:
            print(f"[CLEANUP] Port {port} was already free")

    except Exception as e:
        print(f"[CLEANUP] Warning: Could not clear port {port}: {e}")


def kill_all_python_processes():
    """Kill all Python processes (more aggressive)"""
    print("[CLEANUP] Killing all Python processes...")

    try:
        result = subprocess.run(
            'taskkill /F /IM python.exe',
            shell=True,
            capture_output=True,
            text=True
        )

        if "SUCCESS" in result.stdout:
            print("[CLEANUP] Python processes killed")
        else:
            print("[CLEANUP] No Python processes found")

    except Exception as e:
        print(f"[CLEANUP] Warning: {e}")


if __name__ == "__main__":
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    # First try to kill process on specific port
    kill_process_on_port(port)

    # Also clear common Backend ports
    for p in [8000, 8001, 8002, 8003]:
        if p != port:
            kill_process_on_port(p)