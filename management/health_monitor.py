"""
Health monitoring and auto-recovery for servers
"""
import time
import threading
import logging
from typing import Dict
from .config import ServerStatus

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors server health and handles auto-recovery"""
    
    def __init__(self, servers: Dict, manager_instance):
        self.servers = servers
        self.manager = manager_instance
        self.monitor_thread: threading.Thread = None
        self.monitoring = False
        
    def start_monitoring(self):
        """Start the health monitoring thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Stop the health monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                for name, server in self.servers.items():
                    if server.status == ServerStatus.RUNNING:
                        if not server.check_health():
                            server.health_check_failures += 1
                            logger.warning(f"{name} server health check failed ({server.health_check_failures})")
                            
                            if server.health_check_failures >= 3:
                                logger.error(f"{name} server is unhealthy, attempting restart")
                                server.status = ServerStatus.UNHEALTHY
                                
                                # Attempt auto-recovery
                                success = self._recover_server(server)
                                if success:
                                    server.health_check_failures = 0
                                    logger.info(f"Successfully recovered {name} server")
                                else:
                                    logger.error(f"Failed to recover {name} server")
                        else:
                            # Reset failure counter on successful health check
                            if server.health_check_failures > 0:
                                logger.info(f"{name} server health recovered")
                                server.health_check_failures = 0
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)
    
    def _recover_server(self, server) -> bool:
        """Attempt to recover a failed server"""
        try:
            # Stop the failed server
            logger.info(f"Stopping failed {server.name} server")
            self.manager.stop_server(server.name)
            
            # Wait a moment
            time.sleep(5)
            
            # Restart the server
            logger.info(f"Restarting {server.name} server")
            success = self.manager.start_server(server.name)
            
            return success
            
        except Exception as e:
            logger.error(f"Error recovering server {server.name}: {e}")
            return False