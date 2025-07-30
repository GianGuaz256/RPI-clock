"""
Tests for core components (DataCache, TouchHandler, DashboardApp).
"""

import time
import threading
import pytest
from unittest.mock import Mock, patch, MagicMock
import pygame
from core.cache import DataCache
from core.touch_handler import TouchHandler
from core.dashboard_app import DashboardApp
from config.config_manager import ConfigManager
import os


class TestDataCache:
    """Test the DataCache functionality."""
    
    def test_init(self):
        """Test DataCache initialization."""
        cache = DataCache()
        assert cache._cache == {}
        assert cache._lock is not None
    
    def test_set_and_get(self):
        """Test setting and getting cache values."""
        cache = DataCache()
        
        test_data = {'key': 'value', 'number': 42}
        cache.set('test_key', test_data)
        
        retrieved_data = cache.get('test_key')
        assert retrieved_data == test_data
    
    def test_get_nonexistent_key(self):
        """Test getting a non-existent key returns None."""
        cache = DataCache()
        assert cache.get('nonexistent') is None
    
    def test_is_expired(self):
        """Test cache expiration checking."""
        cache = DataCache()
        
        # Set data
        cache.set('test_key', {'data': 'value'})
        
        # Should not be expired immediately
        assert not cache.is_expired('test_key', max_age=10)
        
        # Should be expired with very small max_age
        assert cache.is_expired('test_key', max_age=0)
    
    def test_get_age(self):
        """Test getting cache entry age."""
        cache = DataCache()
        
        # Set data
        cache.set('test_key', {'data': 'value'})
        
        # Age should be close to 0
        age = cache.get_age('test_key')
        assert 0 <= age < 1  # Should be less than 1 second
        
        # Non-existent key should return 0
        assert cache.get_age('nonexistent') == 0
    
    def test_clear_specific_key(self):
        """Test clearing a specific cache key."""
        cache = DataCache()
        
        cache.set('key1', {'data': 'value1'})
        cache.set('key2', {'data': 'value2'})
        
        cache.clear('key1')
        
        assert cache.get('key1') is None
        assert cache.get('key2') is not None
    
    def test_clear_all(self):
        """Test clearing all cache data."""
        cache = DataCache()
        
        cache.set('key1', {'data': 'value1'})
        cache.set('key2', {'data': 'value2'})
        
        cache.clear()
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
    
    def test_get_all_keys(self):
        """Test getting all cache keys."""
        cache = DataCache()
        
        cache.set('key1', {'data': 'value1'})
        cache.set('key2', {'data': 'value2'})
        
        keys = cache.get_all_keys()
        assert 'key1' in keys
        assert 'key2' in keys
        assert len(keys) == 2
    
    def test_get_cache_info(self):
        """Test getting cache information."""
        cache = DataCache()
        
        cache.set('key1', {'data': 'value1'})
        
        info = cache.get_cache_info()
        assert 'total_entries' in info
        assert 'keys' in info
        assert info['total_entries'] == 1
        assert 'key1' in info['keys']
    
    def test_thread_safety(self):
        """Test cache thread safety."""
        cache = DataCache()
        results = []
        
        def worker(thread_id):
            for i in range(10):
                cache.set(f'thread_{thread_id}_key_{i}', {'thread': thread_id, 'value': i})
                data = cache.get(f'thread_{thread_id}_key_{i}')
                if data:
                    results.append(data)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have received data from all threads
        assert len(results) > 0


class TestTouchHandler:
    """Test the TouchHandler functionality."""
    
    def test_init(self, temp_dir):
        """Test TouchHandler initialization."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            handler = TouchHandler(config)
            
            assert handler.config == config
            assert handler.is_touching is False
            assert handler.start_pos is None
    
    def test_handle_touch_start(self, temp_dir):
        """Test handling touch start events."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            handler = TouchHandler(config)
            
            # Simulate touch start
            result = handler.handle_touch_start((100, 200))
            
            assert handler.is_touching is True
            assert handler.start_pos == (100, 200)
            assert result is None  # No gesture on start
    
    def test_handle_touch_end_no_swipe(self, temp_dir):
        """Test handling touch end without swipe."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            handler = TouchHandler(config)
            
            # Start touch
            handler.handle_touch_start((100, 200))
            
            # End touch at similar position (no swipe)
            result = handler.handle_touch_end((110, 200))
            
            assert handler.is_touching is False
            assert result is None  # No swipe detected
    
    def test_handle_touch_end_left_swipe(self, temp_dir):
        """Test handling left swipe gesture."""
        env_content = "TOUCH_SWIPE_THRESHOLD=50"
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            handler = TouchHandler(config)
            
            # Start touch
            handler.handle_touch_start((200, 100))
            
            # End touch with left swipe (threshold is 50)
            result = handler.handle_touch_end((100, 100))  # 100 pixel left swipe
            
            assert result == 'swipe_left'
            assert handler.is_touching is False
    
    def test_handle_touch_end_right_swipe(self, temp_dir):
        """Test handling right swipe gesture."""
        env_content = "TOUCH_SWIPE_THRESHOLD=50"
        env_path = os.path.join(temp_dir, '.env')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            handler = TouchHandler(config)
            
            # Start touch
            handler.handle_touch_start((100, 100))
            
            # End touch with right swipe
            result = handler.handle_touch_end((200, 100))  # 100 pixel right swipe
            
            assert result == 'swipe_right'
            assert handler.is_touching is False
    
    def test_handle_touch_move(self, temp_dir):
        """Test handling touch move events."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            handler = TouchHandler(config)
            
            # Start touch
            handler.handle_touch_start((100, 100))
            
            # Move touch
            result = handler.handle_touch_move((150, 100))
            
            assert result is None  # Move events don't return gestures
            assert handler.current_pos == (150, 100)
    
    def test_cancel_touch(self, temp_dir):
        """Test canceling touch interaction."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            handler = TouchHandler(config)
            
            # Start touch
            handler.handle_touch_start((100, 100))
            assert handler.is_touching is True
            
            # Cancel touch
            handler.cancel_touch()
            
            assert handler.is_touching is False
            assert handler.start_pos is None
    
    def test_get_touch_info(self, temp_dir):
        """Test getting touch information."""
        with patch('os.getcwd', return_value=temp_dir):
            config = ConfigManager()
            handler = TouchHandler(config)
            
            # Start touch
            handler.handle_touch_start((100, 200))
            handler.handle_touch_move((150, 200))
            
            info = handler.get_touch_info()
            
            assert 'is_touching' in info
            assert 'start_pos' in info
            assert 'current_pos' in info
            assert info['is_touching'] is True
            assert info['start_pos'] == (100, 200)
            assert info['current_pos'] == (150, 200)


class TestDashboardApp:
    """Test the main DashboardApp functionality."""
    
    def test_init_config_only(self, temp_dir, mock_pygame):
        """Test DashboardApp initialization (config and basic setup only)."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'):
            
            app = DashboardApp()
            
            assert app.config_manager is not None
            assert app.runtime_config is not None
            assert app.current_screen_index == 0
            assert app.running is True
    
    def test_screen_navigation(self, temp_dir, mock_pygame):
        """Test screen navigation functionality."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            
            # Test initial screen
            assert app.current_screen_index == 0
            
            # Test next screen
            app.next_screen()
            assert app.current_screen_index == 1
            
            # Test previous screen
            app.previous_screen()
            assert app.current_screen_index == 0
    
    def test_get_current_screen(self, temp_dir, mock_pygame):
        """Test getting current screen."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            
            current_screen = app.get_current_screen()
            assert current_screen is not None
            assert hasattr(current_screen, 'draw')
            assert hasattr(current_screen, 'update')
    
    def test_handle_swipe_events(self, temp_dir, mock_pygame):
        """Test handling swipe events for navigation."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            initial_screen = app.current_screen_index
            
            # Test swipe right (next screen)
            app._handle_swipe('swipe_right')
            assert app.current_screen_index == (initial_screen + 1) % len(app.screens)
            
            # Test swipe left (previous screen)
            app._handle_swipe('swipe_left')
            assert app.current_screen_index == initial_screen
    
    def test_get_app_status(self, temp_dir, mock_pygame):
        """Test getting application status information."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            
            status = app.get_app_status()
            
            assert 'running' in status
            assert 'current_screen' in status
            assert 'total_screens' in status
            assert 'runtime_config' in status
            assert status['running'] is True
            assert status['total_screens'] == 4  # Clock, Bitcoin, Weather, System
    
    @patch('pygame.event.get')
    def test_handle_events(self, mock_event_get, temp_dir, mock_pygame):
        """Test event handling."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=mock_pygame), \
             patch('pygame.time.Clock'), \
             patch('threading.Thread'), \
             patch('pygame.font.Font'):
            
            app = DashboardApp()
            
            # Mock quit event
            quit_event = Mock()
            quit_event.type = pygame.QUIT
            mock_event_get.return_value = [quit_event]
            
            app.handle_events()
            
            assert app.running is False
    
    def test_error_handling_during_init(self, temp_dir):
        """Test error handling during initialization."""
        with patch('os.getcwd', return_value=temp_dir), \
             patch('pygame.init', side_effect=Exception("Pygame init failed")):
            
            with pytest.raises(Exception):
                DashboardApp() 