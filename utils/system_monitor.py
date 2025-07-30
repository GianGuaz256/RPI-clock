"""
System monitoring utilities for Raspberry Pi hardware statistics.
"""

import psutil
import time
from typing import Dict, Any, Optional


class SystemMonitor:
    """Monitor Raspberry Pi system statistics and hardware information."""
    
    @staticmethod
    def get_cpu_temperature() -> float:
        """
        Get CPU temperature in Celsius.
        
        Returns:
            CPU temperature in Celsius or 0.0 if unavailable
        """
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return temp
        except (FileNotFoundError, ValueError, PermissionError):
            # Fallback for non-Pi systems or permission issues
            return 0.0
    
    @staticmethod
    def get_cpu_usage() -> float:
        """
        Get current CPU usage percentage.
        
        Returns:
            CPU usage percentage (0-100)
        """
        try:
            return psutil.cpu_percent(interval=1)
        except Exception:
            return 0.0
    
    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """
        Get memory usage information.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                'total_gb': memory.total / (1024**3),
                'used_gb': memory.used / (1024**3),
                'available_gb': memory.available / (1024**3)
            }
        except Exception:
            return {
                'total': 0, 'available': 0, 'used': 0, 'percent': 0,
                'total_gb': 0, 'used_gb': 0, 'available_gb': 0
            }
    
    @staticmethod
    def get_disk_info() -> Dict[str, Any]:
        """
        Get disk usage information for root partition.
        
        Returns:
            Dictionary with disk statistics
        """
        try:
            disk = psutil.disk_usage('/')
            return {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': (disk.used / disk.total) * 100,
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'free_gb': disk.free / (1024**3)
            }
        except Exception:
            return {
                'total': 0, 'used': 0, 'free': 0, 'percent': 0,
                'total_gb': 0, 'used_gb': 0, 'free_gb': 0
            }
    
    @staticmethod
    def get_uptime() -> Dict[str, Any]:
        """
        Get system uptime information.
        
        Returns:
            Dictionary with uptime statistics
        """
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return {
                'total_seconds': uptime_seconds,
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'formatted': f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"
            }
        except Exception:
            return {
                'total_seconds': 0, 'days': 0, 'hours': 0, 'minutes': 0,
                'formatted': '0h 0m'
            }
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """
        Get network interface information.
        
        Returns:
            Dictionary with network statistics
        """
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'mb_sent': net_io.bytes_sent / (1024**2),
                'mb_recv': net_io.bytes_recv / (1024**2)
            }
        except Exception:
            return {
                'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0,
                'mb_sent': 0, 'mb_recv': 0
            }
    
    @staticmethod
    def get_complete_stats() -> Dict[str, Any]:
        """
        Get complete system statistics.
        
        Returns:
            Dictionary with all system information
        """
        try:
            return {
                'cpu_temperature': SystemMonitor.get_cpu_temperature(),
                'cpu_usage': SystemMonitor.get_cpu_usage(),
                'memory': SystemMonitor.get_memory_info(),
                'disk': SystemMonitor.get_disk_info(),
                'uptime': SystemMonitor.get_uptime(),
                'network': SystemMonitor.get_network_info(),
                'timestamp': time.time(),
                'status': 'success'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """
        Get system health status with warnings.
        
        Returns:
            Dictionary with health information and warnings
        """
        stats = SystemMonitor.get_complete_stats()
        
        if stats['status'] == 'error':
            return stats
        
        warnings = []
        critical = []
        
        # CPU temperature checks
        cpu_temp = stats['cpu_temperature']
        if cpu_temp > 80:
            critical.append(f"Critical CPU temperature: {cpu_temp:.1f}°C")
        elif cpu_temp > 70:
            warnings.append(f"High CPU temperature: {cpu_temp:.1f}°C")
        
        # CPU usage checks
        cpu_usage = stats['cpu_usage']
        if cpu_usage > 90:
            warnings.append(f"High CPU usage: {cpu_usage:.1f}%")
        
        # Memory usage checks
        memory_percent = stats['memory']['percent']
        if memory_percent > 90:
            critical.append(f"Critical memory usage: {memory_percent:.1f}%")
        elif memory_percent > 80:
            warnings.append(f"High memory usage: {memory_percent:.1f}%")
        
        # Disk usage checks
        disk_percent = stats['disk']['percent']
        if disk_percent > 95:
            critical.append(f"Critical disk usage: {disk_percent:.1f}%")
        elif disk_percent > 85:
            warnings.append(f"High disk usage: {disk_percent:.1f}%")
        
        # Determine overall health
        if critical:
            health_status = 'critical'
        elif warnings:
            health_status = 'warning'
        else:
            health_status = 'good'
        
        stats.update({
            'health_status': health_status,
            'warnings': warnings,
            'critical': critical
        })
        
        return stats
    
    @staticmethod
    def is_raspberry_pi() -> bool:
        """
        Check if running on a Raspberry Pi.
        
        Returns:
            True if running on Raspberry Pi, False otherwise
        """
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                return 'Raspberry Pi' in cpuinfo
        except (FileNotFoundError, PermissionError):
            return False 