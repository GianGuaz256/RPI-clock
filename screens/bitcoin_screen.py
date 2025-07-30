"""
Bitcoin information screen for the Raspberry Pi Dashboard.
"""

from typing import Dict, Any
import time
from screens.base_screen import BaseScreen
from api.bitcoin_api import BitcoinAPIManager
from utils.constants import WHITE, GREEN, GRAY, RED, SCREEN_WIDTH, SCREEN_HEIGHT, BLUE, ORANGE, YELLOW


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
        Draw comprehensive Bitcoin data from mempool.space.
        
        Args:
            screen: Pygame surface to draw on
            data: Bitcoin data dictionary
        """
        # Bitcoin price (top center, smaller to make room for more info)
        price = data.get('price', 0)
        price_text = f"${price:,.0f}"
        self.draw_text(screen, price_text, (SCREEN_WIDTH // 2, 60), 
                      self.font_large, WHITE, center=True)
        
        # Left column - Block and Network info
        left_x = 10
        y_offset = 90
        
        # Block information
        block_height = data.get('block_height', 0)
        self.draw_text(screen, f"Block: {block_height:,}", (left_x, y_offset), 
                      self.font_small, GREEN)
        y_offset += 20
        
        # Block details
        block_size = data.get('block_size', 0)
        block_tx_count = data.get('block_tx_count', 0)
        if block_size > 0:
            self.draw_text(screen, f"Size: {block_size/1000:.1f}kB", (left_x, y_offset), 
                          self.font_small, GRAY)
            y_offset += 15
        if block_tx_count > 0:
            self.draw_text(screen, f"TXs: {block_tx_count:,}", (left_x, y_offset), 
                          self.font_small, GRAY)
            y_offset += 20
        else:
            y_offset += 20
        
        # Hashrate
        hashrate = data.get('hashrate', {})
        hashrate_formatted = hashrate.get('formatted', '0 EH/s')
        self.draw_text(screen, f"Hashrate:", (left_x, y_offset), 
                      self.font_small, BLUE)
        y_offset += 15
        self.draw_text(screen, hashrate_formatted, (left_x, y_offset), 
                      self.font_small, WHITE)
        y_offset += 25
        
        # Difficulty
        difficulty = data.get('difficulty', {})
        diff_change = difficulty.get('change', 0)
        blocks_until = difficulty.get('blocks_until_retarget', 0)
        
        self.draw_text(screen, f"Difficulty:", (left_x, y_offset), 
                      self.font_small, ORANGE)
        y_offset += 15
        
        # Difficulty change indicator with color
        if diff_change > 0:
            diff_color = RED
            diff_text = f"+{diff_change:.1f}%"
        elif diff_change < 0:
            diff_color = GREEN
            diff_text = f"{diff_change:.1f}%"
        else:
            diff_color = GRAY
            diff_text = "0.0%"
        
        self.draw_text(screen, diff_text, (left_x, y_offset), 
                      self.font_small, diff_color)
        y_offset += 15
        
        if blocks_until > 0:
            self.draw_text(screen, f"~{blocks_until} blocks", (left_x, y_offset), 
                          self.font_small, GRAY)
        
        # Right column - Fees and Mempool
        right_x = SCREEN_WIDTH // 2 + 10
        y_offset = 90
        
        # Fee recommendations
        fees = data.get('fees', {})
        self.draw_text(screen, "Transaction Fees:", (right_x, y_offset), 
                      self.font_small, YELLOW)
        y_offset += 20
        
        # Fee tiers
        fee_tiers = [
            ('Fast:', fees.get('fastest', 0), GREEN),
            ('30min:', fees.get('half_hour', 0), BLUE),
            ('1hr:', fees.get('hour', 0), ORANGE),
            ('Eco:', fees.get('economy', 0), GRAY)
        ]
        
        for label, fee_rate, color in fee_tiers:
            if fee_rate > 0:
                self.draw_text(screen, f"{label} {fee_rate} sat/vB", (right_x, y_offset), 
                              self.font_small, color)
                y_offset += 15
        
        y_offset += 10
        
        # Mempool statistics
        mempool = data.get('mempool', {})
        mempool_count = mempool.get('count', 0)
        mempool_vsize = mempool.get('vsize', 0)
        
        if mempool_count > 0:
            self.draw_text(screen, "Mempool:", (right_x, y_offset), 
                          self.font_small, WHITE)
            y_offset += 15
            
            self.draw_text(screen, f"{mempool_count:,} TXs", (right_x, y_offset), 
                          self.font_small, GRAY)
            y_offset += 15
            
            if mempool_vsize > 0:
                mempool_mb = mempool_vsize / 1_000_000
                self.draw_text(screen, f"{mempool_mb:.1f} MB", (right_x, y_offset), 
                              self.font_small, GRAY)
        
        # Last update time at bottom
        self._draw_update_time(screen, data)
    
    def _draw_update_time(self, screen, data: Dict[str, Any]) -> None:
        """
        Draw last update time at bottom of screen.
        
        Args:
            screen: Pygame surface to draw on
            data: Bitcoin data dictionary
        """
        last_updated = data.get('last_updated', 0)
        if last_updated:
            age_seconds = int(time.time() - last_updated)
            
            if age_seconds < 60:
                age_text = f"Updated {age_seconds}s ago"
            elif age_seconds < 3600:
                age_text = f"Updated {age_seconds // 60}m ago"
            else:
                age_text = f"Updated {age_seconds // 3600}h ago"
            
            self.draw_text(screen, age_text, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30), 
                          self.font_small, GRAY, center=True)
    
    def _format_large_number(self, number: float) -> str:
        """
        Format large numbers for display.
        
        Args:
            number: Number to format
            
        Returns:
            Formatted string
        """
        if number >= 1_000_000_000:
            return f"{number / 1_000_000_000:.1f}B"
        elif number >= 1_000_000:
            return f"{number / 1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.1f}K"
        else:
            return f"{number:.0f}"
    
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
        self.draw_text(screen, "or mempool.space availability", (SCREEN_WIDTH // 2, 220), 
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