"""
System statistics screen for the Raspberry Pi Dashboard.
"""

import time
from typing import Dict, Any
from screens.base_screen import BaseScreen
from utils.system_monitor import SystemMonitor
from utils.constants import WHITE, GREEN, RED, GRAY, SCREEN_WIDTH, DEFAULT_SYSTEM_UPDATE_INTERVAL


class SystemStatsScreen(BaseScreen):
    """Display Raspberry Pi system statistics and hardware information."""
    
    def __init__(self, app):
        """
        Initialize system statistics screen.
        
        Args:
            app: Reference to main application instance
        """
        super().__init__(app)
        self.last_system_update = 0
        self.system_stats = {}
        self.update_interval = DEFAULT_SYSTEM_UPDATE_INTERVAL
    
    def update(self) -> None:
        """Update system statistics data."""
        current_time = time.time()
        
        # Update system stats every few seconds for real-time feel
        if current_time - self.last_system_update > self.update_interval:
            self.system_stats = SystemMonitor.get_complete_stats()
            self.last_system_update = current_time
        
        self.last_update = current_time
    
    def draw(self, screen) -> None:
        """
        Draw system statistics screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        screen.fill((0, 0, 0))  # Black background
        
        # Draw title
        self.draw_title(screen, "System Stats", 30)
        
        if self.system_stats.get('status') == 'success':
            self._draw_system_data(screen)
        else:
            self._draw_error_state(screen)
        
        # Draw status indicator
        status = self.system_stats.get('status', 'unknown')
        self.draw_status_indicator(screen, status, (450, 20))
    
    def _draw_system_data(self, screen) -> None:
        """
        Draw system statistics and information.
        
        Args:
            screen: Pygame surface to draw on
        """
        y_offset = 70
        
        # CPU Temperature
        self._draw_cpu_temperature(screen, y_offset)
        y_offset += 50
        
        # CPU Usage
        self._draw_cpu_usage(screen, y_offset)
        y_offset += 50
        
        # Memory Usage
        self._draw_memory_usage(screen, y_offset)
        y_offset += 50
        
        # System Uptime
        self._draw_uptime(screen, y_offset)
        y_offset += 35
        
        # Additional info
        self._draw_additional_info(screen, y_offset)
    
    def _draw_cpu_temperature(self, screen, y_pos: int) -> None:
        """
        Draw CPU temperature with color coding.
        
        Args:
            screen: Pygame surface to draw on
            y_pos: Y position to draw at
        """
        cpu_temp = self.system_stats.get('cpu_temperature', 0)
        
        # Color code based on temperature
        if cpu_temp > 80:
            temp_color = RED
        elif cpu_temp > 70:
            temp_color = (255, 165, 0)  # Orange
        else:
            temp_color = WHITE
        
        # Draw temperature
        self.draw_text(screen, "CPU Temperature:", (20, y_pos), 
                      self.font_medium, GREEN)
        self.draw_text(screen, f"{cpu_temp:.1f}°C", (20, y_pos + 25), 
                      self.font_medium, temp_color)
        
        # Draw temperature bar
        self._draw_temperature_bar(screen, (220, y_pos + 30), cpu_temp)
    
    def _draw_cpu_usage(self, screen, y_pos: int) -> None:
        """
        Draw CPU usage with progress bar.
        
        Args:
            screen: Pygame surface to draw on
            y_pos: Y position to draw at
        """
        cpu_percent = self.system_stats.get('cpu_usage', 0)
        
        # Color code based on usage
        if cpu_percent > 90:
            usage_color = RED
        elif cpu_percent > 75:
            usage_color = (255, 165, 0)  # Orange
        else:
            usage_color = WHITE
        
        # Draw CPU usage
        self.draw_text(screen, "CPU Usage:", (20, y_pos), 
                      self.font_medium, GREEN)
        self.draw_text(screen, f"{cpu_percent:.1f}%", (20, y_pos + 25), 
                      self.font_medium, usage_color)
        
        # Draw progress bar
        self.draw_progress_bar(screen, (150, y_pos + 30), (200, 12), 
                             cpu_percent, 100, fill_color=usage_color)
    
    def _draw_memory_usage(self, screen, y_pos: int) -> None:
        """
        Draw memory usage with progress bar.
        
        Args:
            screen: Pygame surface to draw on
            y_pos: Y position to draw at
        """
        memory_info = self.system_stats.get('memory', {})
        memory_percent = memory_info.get('percent', 0)
        memory_used_gb = memory_info.get('used_gb', 0)
        memory_total_gb = memory_info.get('total_gb', 0)
        
        # Color code based on usage
        if memory_percent > 90:
            memory_color = RED
        elif memory_percent > 80:
            memory_color = (255, 165, 0)  # Orange
        else:
            memory_color = WHITE
        
        # Draw memory usage
        self.draw_text(screen, "Memory Usage:", (20, y_pos), 
                      self.font_medium, GREEN)
        self.draw_text(screen, f"{memory_percent:.1f}%", (20, y_pos + 25), 
                      self.font_medium, memory_color)
        
        # Draw memory details
        if memory_total_gb > 0:
            memory_text = f"{memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB"
            self.draw_text(screen, memory_text, (250, y_pos + 5), 
                          self.font_small, GRAY)
        
        # Draw progress bar
        self.draw_progress_bar(screen, (150, y_pos + 30), (200, 12), 
                             memory_percent, 100, fill_color=memory_color)
    
    def _draw_uptime(self, screen, y_pos: int) -> None:
        """
        Draw system uptime.
        
        Args:
            screen: Pygame surface to draw on
            y_pos: Y position to draw at
        """
        uptime_info = self.system_stats.get('uptime', {})
        uptime_formatted = uptime_info.get('formatted', '0h 0m')
        
        self.draw_text(screen, "System Uptime:", (20, y_pos), 
                      self.font_medium, GREEN)
        self.draw_text(screen, uptime_formatted, (20, y_pos + 20), 
                      self.font_medium, WHITE)
    
    def _draw_additional_info(self, screen, y_pos: int) -> None:
        """
        Draw additional system information.
        
        Args:
            screen: Pygame surface to draw on
            y_pos: Y position to draw at
        """
        # Disk usage (if space permits)
        disk_info = self.system_stats.get('disk', {})
        if disk_info and y_pos < 280:
            disk_percent = disk_info.get('percent', 0)
            disk_used_gb = disk_info.get('used_gb', 0)
            disk_total_gb = disk_info.get('total_gb', 0)
            
            disk_color = RED if disk_percent > 90 else WHITE
            
            disk_text = f"Disk: {disk_percent:.1f}% ({disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB)"
            self.draw_text(screen, disk_text, (20, y_pos), 
                          self.font_small, disk_color)
        
        # Raspberry Pi indicator
        if SystemMonitor.is_raspberry_pi():
            self.draw_text(screen, "🥧 Raspberry Pi", (SCREEN_WIDTH - 120, 300), 
                          self.font_small, GREEN)
    
    def _draw_temperature_bar(self, screen, pos, temperature: float) -> None:
        """
        Draw temperature bar indicator.
        
        Args:
            screen: Pygame surface to draw on
            pos: Position (x, y)
            temperature: Temperature value
        """
        # Temperature range: 0-100°C for visualization
        max_temp = 100
        temp_percent = min(temperature / max_temp * 100, 100)
        
        # Color based on temperature zones
        if temperature > 80:
            color = RED
        elif temperature > 70:
            color = (255, 165, 0)  # Orange
        elif temperature > 50:
            color = (255, 255, 0)  # Yellow
        else:
            color = GREEN
        
        self.draw_progress_bar(screen, pos, (150, 8), temp_percent, 100, 
                             fill_color=color)
    
    def _draw_error_state(self, screen) -> None:
        """
        Draw error state when system stats are unavailable.
        
        Args:
            screen: Pygame surface to draw on
        """
        error_msg = self.system_stats.get('error', 'Unknown error')
        
        self.draw_text(screen, "System Data Unavailable", (SCREEN_WIDTH // 2, 120), 
                      self.font_medium, RED, center=True)
        
        # Truncate long error messages
        if len(error_msg) > 50:
            error_msg = error_msg[:47] + "..."
        
        self.draw_text(screen, error_msg, (SCREEN_WIDTH // 2, 160), 
                      self.font_small, RED, center=True)
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """
        Get system health summary with warnings.
        
        Returns:
            Dictionary with system health information
        """
        if not self.system_stats or self.system_stats.get('status') != 'success':
            return {
                'status': 'error',
                'health': 'unknown',
                'warnings': ['System monitoring unavailable']
            }
        
        warnings = []
        critical = []
        
        # Check CPU temperature
        cpu_temp = self.system_stats.get('cpu_temperature', 0)
        if cpu_temp > 80:
            critical.append(f"Critical CPU temperature: {cpu_temp:.1f}°C")
        elif cpu_temp > 70:
            warnings.append(f"High CPU temperature: {cpu_temp:.1f}°C")
        
        # Check CPU usage
        cpu_usage = self.system_stats.get('cpu_usage', 0)
        if cpu_usage > 90:
            warnings.append(f"High CPU usage: {cpu_usage:.1f}%")
        
        # Check memory usage
        memory_info = self.system_stats.get('memory', {})
        memory_percent = memory_info.get('percent', 0)
        if memory_percent > 90:
            critical.append(f"Critical memory usage: {memory_percent:.1f}%")
        elif memory_percent > 80:
            warnings.append(f"High memory usage: {memory_percent:.1f}%")
        
        # Determine overall health
        if critical:
            health = 'critical'
        elif warnings:
            health = 'warning'
        else:
            health = 'good'
        
        return {
            'status': 'success',
            'health': health,
            'warnings': warnings,
            'critical': critical,
            'cpu_temp': cpu_temp,
            'cpu_usage': cpu_usage,
            'memory_percent': memory_percent
        }
    
    def get_system_summary(self) -> Dict[str, Any]:
        """
        Get condensed system information summary.
        
        Returns:
            Dictionary with system summary
        """
        if not self.system_stats or self.system_stats.get('status') != 'success':
            return {'status': 'error'}
        
        uptime_info = self.system_stats.get('uptime', {})
        memory_info = self.system_stats.get('memory', {})
        
        return {
            'status': 'success',
            'cpu_temperature': self.system_stats.get('cpu_temperature', 0),
            'cpu_usage': self.system_stats.get('cpu_usage', 0),
            'memory_percent': memory_info.get('percent', 0),
            'uptime_formatted': uptime_info.get('formatted', '0h 0m'),
            'is_raspberry_pi': SystemMonitor.is_raspberry_pi()
        } 