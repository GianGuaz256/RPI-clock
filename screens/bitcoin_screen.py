"""
Bitcoin information screen for the Raspberry Pi Dashboard.
"""

from typing import Dict, Any
from screens.base_screen import BaseScreen
from api.bitcoin_api import BitcoinAPIManager
from utils.constants import WHITE, GREEN, GRAY, RED, SCREEN_WIDTH


class BitcoinScreen(BaseScreen):
    """Display Bitcoin price and blockchain information."""
    
    def __init__(self, app):
        """
        Initialize Bitcoin screen.
        
        Args:
            app: Reference to main application instance
        """
        super().__init__(app)
        self.bitcoin_manager = BitcoinAPIManager()
    
    def update(self) -> None:
        """Update Bitcoin data (data is updated via background thread)."""
        # Data is updated automatically by the API manager's caching system
        pass
    
    def draw(self, screen) -> None:
        """
        Draw Bitcoin information screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        screen.fill((0, 0, 0))  # Black background
        
        # Get Bitcoin data
        bitcoin_data = self.bitcoin_manager.get_data()
        status = bitcoin_data.get('status', 'unknown')
        
        # Draw title
        self.draw_title(screen, "Bitcoin Info", 30)
        
        if status in ['success', 'cached']:
            self._draw_bitcoin_data(screen, bitcoin_data)
        else:
            self._draw_error_state(screen, bitcoin_data)
        
        # Draw status indicator
        self.draw_status_indicator(screen, status, (450, 20))
    
    def _draw_bitcoin_data(self, screen, data: Dict[str, Any]) -> None:
        """
        Draw Bitcoin price and blockchain data.
        
        Args:
            screen: Pygame surface to draw on
            data: Bitcoin data dictionary
        """
        # Bitcoin price (large, centered)
        price = data.get('price', 0)
        price_text = f"${price:,.2f}"
        self.draw_text(screen, price_text, (SCREEN_WIDTH // 2, 100), 
                      self.font_large, WHITE, center=True)
        
        # Currency label
        self.draw_text(screen, "USD", (SCREEN_WIDTH // 2, 140), 
                      self.font_small, GRAY, center=True)
        
        # Block information
        y_offset = 170
        
        # Block height
        block_height = data.get('block_height', 0)
        self.draw_text(screen, "Block Height:", (20, y_offset), 
                      self.font_medium, GREEN)
        self.draw_text(screen, f"{block_height:,}", (20, y_offset + 25), 
                      self.font_medium, WHITE)
        
        # Latest block hash
        y_offset += 70
        self.draw_text(screen, "Latest Block:", (20, y_offset), 
                      self.font_medium, GREEN)
        
        block_hash = data.get('block_hash_short', 'N/A')
        self.draw_text(screen, block_hash, (20, y_offset + 25), 
                      self.font_small, GRAY)
        
        # Price change indicator (if available in future updates)
        self._draw_price_trend(screen, data)
    
    def _draw_price_trend(self, screen, data: Dict[str, Any]) -> None:
        """
        Draw price trend indicator (placeholder for future enhancement).
        
        Args:
            screen: Pygame surface to draw on
            data: Bitcoin data dictionary
        """
        # Placeholder for price trend - could be enhanced with historical data
        # For now, just show last update time
        last_updated = data.get('last_updated', 0)
        if last_updated:
            import time
            age_seconds = int(time.time() - last_updated)
            
            if age_seconds < 60:
                age_text = f"Updated {age_seconds}s ago"
            elif age_seconds < 3600:
                age_text = f"Updated {age_seconds // 60}m ago"
            else:
                age_text = f"Updated {age_seconds // 3600}h ago"
            
            self.draw_text(screen, age_text, (SCREEN_WIDTH // 2, 290), 
                          self.font_small, GRAY, center=True)
    
    def _draw_error_state(self, screen, data: Dict[str, Any]) -> None:
        """
        Draw error state when Bitcoin data is unavailable.
        
        Args:
            screen: Pygame surface to draw on
            data: Bitcoin data dictionary with error information
        """
        # Error message
        self.draw_text(screen, "Data Unavailable", (SCREEN_WIDTH // 2, 120), 
                      self.font_medium, RED, center=True)
        
        # Error details
        error_msg = data.get('error', 'Unknown error')
        
        # Truncate long error messages
        if len(error_msg) > 50:
            error_msg = error_msg[:47] + "..."
        
        self.draw_text(screen, error_msg, (SCREEN_WIDTH // 2, 160), 
                      self.font_small, RED, center=True)
        
        # Helpful message
        self.draw_text(screen, "Check internet connection", (SCREEN_WIDTH // 2, 200), 
                      self.font_small, GRAY, center=True)
    
    def get_bitcoin_summary(self) -> Dict[str, Any]:
        """
        Get Bitcoin data summary.
        
        Returns:
            Dictionary with Bitcoin information summary
        """
        data = self.bitcoin_manager.get_data()
        
        return {
            'price': data.get('price', 0),
            'price_formatted': data.get('price_formatted', '$0.00'),
            'block_height': data.get('block_height', 0),
            'status': data.get('status', 'unknown'),
            'last_updated': data.get('last_updated', 0),
            'is_available': data.get('status') in ['success', 'cached']
        }
    
    def force_refresh(self) -> bool:
        """
        Force refresh of Bitcoin data.
        
        Returns:
            True if refresh was successful, False otherwise
        """
        try:
            data = self.bitcoin_manager.get_data(force_refresh=True)
            return data.get('status') == 'success'
        except Exception as e:
            print(f"Error forcing Bitcoin data refresh: {e}")
            return False 