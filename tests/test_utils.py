"""
Tests for utility components (SystemMonitor, constants).
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from utils.system_monitor import SystemMonitor
from utils.constants import get_runtime_constants, WEATHER_ICONS, MOCK_WEATHER_DATA
from config.config_manager import ConfigManager
import os


class TestSystemMonitor:
    """Test the SystemMonitor functionality."""
    
    @patch('builtins.open', mock_open(read_data='45678\n'))
    def test_get_cpu_temperature(self):
        """Test getting CPU temperature."""
        temp = SystemMonitor.get_cpu_temperature()
        assert temp == 45.678
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_get_cpu_temperature_file_not_found(self):
        """Test CPU temperature when thermal file doesn't exist."""
        temp = SystemMonitor.get_cpu_temperature()
        assert temp == 0.0
    
    @patch('builtins.open', mock_open(read_data='invalid_data'))
    def test_get_cpu_temperature_invalid_data(self):
        """Test CPU temperature with invalid data."""
        temp = SystemMonitor.get_cpu_temperature()
        assert temp == 0.0
    
    @patch('psutil.cpu_percent', return_value=25.5)
    def test_get_cpu_usage(self, mock_cpu_percent):
        """Test getting CPU usage."""
        usage = SystemMonitor.get_cpu_usage()
        assert usage == 25.5
        mock_cpu_percent.assert_called_once()
    
    @patch('psutil.cpu_percent', side_effect=Exception("psutil error"))
    def test_get_cpu_usage_error(self, mock_cpu_percent):
        """Test CPU usage with psutil error."""
        usage = SystemMonitor.get_cpu_usage()
        assert usage == 0.0
    
    @patch('psutil.virtual_memory')
    def test_get_memory_usage(self, mock_virtual_memory):
        """Test getting memory usage."""
        mock_memory = Mock()
        mock_memory.percent = 65.2
        mock_virtual_memory.return_value = mock_memory
        
        usage = SystemMonitor.get_memory_usage()
        assert usage == 65.2
    
    @patch('psutil.virtual_memory', side_effect=Exception("memory error"))
    def test_get_memory_usage_error(self, mock_virtual_memory):
        """Test memory usage with error."""
        usage = SystemMonitor.get_memory_usage()
        assert usage == 0.0
    
    @patch('psutil.disk_usage')
    def test_get_disk_usage(self, mock_disk_usage):
        """Test getting disk usage."""
        mock_usage = Mock()
        mock_usage.percent = 42.8
        mock_disk_usage.return_value = mock_usage
        
        usage = SystemMonitor.get_disk_usage()
        assert usage == 42.8
    
    @patch('psutil.disk_usage', side_effect=Exception("disk error"))
    def test_get_disk_usage_error(self, mock_disk_usage):
        """Test disk usage with error."""
        usage = SystemMonitor.get_disk_usage('/')
        assert usage == 0.0
    
    @patch('psutil.net_io_counters')
    def test_get_network_usage(self, mock_net_io):
        """Test getting network usage."""
        mock_stats = Mock()
        mock_stats.bytes_sent = 1024000
        mock_stats.bytes_recv = 2048000
        mock_stats.packets_sent = 1000
        mock_stats.packets_recv = 1500
        mock_net_io.return_value = mock_stats
        
        usage = SystemMonitor.get_network_usage()
        
        assert 'bytes_sent_mb' in usage
        assert 'bytes_recv_mb' in usage
        assert usage['bytes_sent_mb'] == 1.0  # 1024000 / (1024*1024)
        assert usage['bytes_recv_mb'] == 2.0  # 2048000 / (1024*1024)
    
    @patch('psutil.net_io_counters', side_effect=Exception("network error"))
    def test_get_network_usage_error(self, mock_net_io):
        """Test network usage with error."""
        usage = SystemMonitor.get_network_usage()
        
        assert usage['bytes_sent_mb'] == 0.0
        assert usage['bytes_recv_mb'] == 0.0
    
    @patch('psutil.boot_time', return_value=1234567890)
    @patch('time.time', return_value=1234654290)  # 86400 seconds later
    def test_get_uptime(self, mock_time, mock_boot_time):
        """Test getting system uptime."""
        uptime = SystemMonitor.get_uptime()
        
        assert uptime == 86400  # 1 day in seconds
    
    @patch('psutil.boot_time', side_effect=Exception("uptime error"))
    def test_get_uptime_error(self, mock_boot_time):
        """Test uptime with error."""
        uptime = SystemMonitor.get_uptime()
        assert uptime == 0
    
    def test_format_uptime(self):
        """Test uptime formatting."""
        # Test various uptime values
        assert SystemMonitor.format_uptime(0) == "0:00:00"
        assert SystemMonitor.format_uptime(3661) == "1:01:01"  # 1h 1m 1s
        assert SystemMonitor.format_uptime(86400) == "1 day, 0:00:00"  # 1 day
        assert SystemMonitor.format_uptime(90061) == "1 day, 1:01:01"  # 1d 1h 1m 1s
        assert SystemMonitor.format_uptime(172800) == "2 days, 0:00:00"  # 2 days
    
    @patch('os.path.exists', return_value=True)
    def test_is_raspberry_pi_true(self, mock_exists):
        """Test Raspberry Pi detection when it is a Pi."""
        with patch('builtins.open', mock_open(read_data='Raspberry Pi 4 Model B Rev 1.4')):
            assert SystemMonitor.is_raspberry_pi() is True
    
    @patch('os.path.exists', return_value=False)
    def test_is_raspberry_pi_false_no_file(self, mock_exists):
        """Test Raspberry Pi detection when cpuinfo file doesn't exist."""
        assert SystemMonitor.is_raspberry_pi() is False
    
    @patch('os.path.exists', return_value=True)
    def test_is_raspberry_pi_false_wrong_content(self, mock_exists):
        """Test Raspberry Pi detection on non-Pi hardware."""
        with patch('builtins.open', mock_open(read_data='Intel(R) Core(TM) i7')):
            assert SystemMonitor.is_raspberry_pi() is False
    
    def test_get_complete_stats(self):
        """Test getting complete system statistics."""
        with patch.multiple(
            'utils.system_monitor.SystemMonitor',
            get_cpu_temperature=Mock(return_value=45.2),
            get_cpu_usage=Mock(return_value=15.5),
            get_memory_usage=Mock(return_value=35.8),
            get_disk_usage=Mock(return_value=12.3),
            get_uptime=Mock(return_value=86400),
            format_uptime=Mock(return_value="1 day, 0:00:00"),
            get_network_usage=Mock(return_value={'bytes_sent_mb': 1.0, 'bytes_recv_mb': 2.0}),
            is_raspberry_pi=Mock(return_value=True)
        ):
            stats = SystemMonitor.get_complete_stats()
            
            assert 'cpu_temp' in stats
            assert 'cpu_usage' in stats
            assert 'memory_usage' in stats
            assert 'disk_usage' in stats
            assert 'uptime_seconds' in stats
            assert 'uptime_formatted' in stats
            assert 'network' in stats
            assert 'is_raspberry_pi' in stats
            
            assert stats['cpu_temp'] == 45.2
            assert stats['cpu_usage'] == 15.5
            assert stats['is_raspberry_pi'] is True
    
    def test_get_health_status(self):
        """Test getting system health status."""
        with patch.multiple(
            'utils.system_monitor.SystemMonitor',
            get_cpu_temperature=Mock(return_value=45.2),
            get_cpu_usage=Mock(return_value=15.5),
            get_memory_usage=Mock(return_value=35.8)
        ):
            health = SystemMonitor.get_health_status()
            
            assert 'overall_status' in health
            assert 'warnings' in health
            assert 'critical_issues' in health
            assert health['overall_status'] in ['good', 'warning', 'critical']


class TestConstants:
    """Test constants and utility functions."""
    
    def test_weather_icons_exist(self):
        """Test that weather icons dictionary contains expected values."""
        assert 'Clear' in WEATHER_ICONS
        assert 'Clouds' in WEATHER_ICONS
        assert 'Rain' in WEATHER_ICONS
        assert isinstance(WEATHER_ICONS['Clear'], str)
    
    def test_mock_weather_data_structure(self):
        """Test that mock weather data has correct structure."""
        assert isinstance(MOCK_WEATHER_DATA, list)
        assert len(MOCK_WEATHER_DATA) > 0
        
        for weather_item in MOCK_WEATHER_DATA:
            assert 'condition' in weather_item
            assert 'temperature' in weather_item
            assert 'humidity' in weather_item
            assert 'wind_speed' in weather_item
            assert isinstance(weather_item['temperature'], (int, float))
            assert isinstance(weather_item['humidity'], int)
    
    def test_get_runtime_constants(self, temp_dir):
        """Test getting runtime constants from configuration."""
        env_content = """
        APP_FPS=60
        TOUCH_SWIPE_THRESHOLD=75
        API_UPDATE_INTERVAL=180
        SYSTEM_UPDATE_INTERVAL=3
        DEBUG_MODE=true
        """
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            constants = get_runtime_constants(config)
            
            assert 'FPS' in constants
            assert 'SWIPE_THRESHOLD' in constants
            assert 'UPDATE_INTERVAL' in constants
            assert 'SYSTEM_UPDATE_INTERVAL' in constants
            assert 'DEBUG_MODE' in constants
            
            assert constants['FPS'] == 60
            assert constants['SWIPE_THRESHOLD'] == 75
            assert constants['UPDATE_INTERVAL'] == 180
            assert constants['DEBUG_MODE'] is True
    
    def test_get_runtime_constants_defaults(self, temp_dir):
        """Test getting runtime constants with default values."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            constants = get_runtime_constants(config)
            
            # Should use default values when no config provided
            assert constants['FPS'] == 30  # DEFAULT_FPS
            assert constants['SWIPE_THRESHOLD'] == 100  # DEFAULT_SWIPE_THRESHOLD
            assert constants['UPDATE_INTERVAL'] == 300  # DEFAULT_UPDATE_INTERVAL
            assert constants['SYSTEM_UPDATE_INTERVAL'] == 5  # DEFAULT_SYSTEM_UPDATE_INTERVAL
            assert constants['DEBUG_MODE'] is False 