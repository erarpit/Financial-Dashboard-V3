from typing import Dict, Any, Optional
import logging
from datetime import datetime
from models.market import Market
from models.schemas import MarketStatus, MarketSummary

logger = logging.getLogger(__name__)

class MarketService:
    """Service for managing market status and summary data"""
    
    def __init__(self):
        self.markets = {
            "us": Market("us"),
            "india": Market("india"),
            "uk": Market("uk"),
            "canada": Market("canada"),
            "australia": Market("australia")
        }
    
    def get_market_status(self, market_key: str) -> Optional[MarketStatus]:
        """Get market status for a specific market"""
        try:
            if market_key not in self.markets:
                logger.warning(f"Market {market_key} not found")
                return None
            
            market = self.markets[market_key]
            status = market.status
            
            if not status:
                return None
            
            # Determine if market is open
            current_time = datetime.now()
            is_open = False
            
            if 'open' in status and 'close' in status:
                try:
                    open_time = status['open']
                    close_time = status['close']
                    is_open = open_time <= current_time <= close_time
                except Exception as e:
                    logger.warning(f"Error determining market status: {str(e)}")
            
            return MarketStatus(
                market=market_key,
                is_open=is_open,
                open_time=status.get('open').isoformat() if 'open' in status else None,
                close_time=status.get('close').isoformat() if 'close' in status else None,
                timezone=status.get('timezone', {}).get('short') if 'timezone' in status else None,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting market status for {market_key}: {str(e)}")
            return None
    
    def get_market_summary(self, market_key: str) -> Optional[MarketSummary]:
        """Get market summary for a specific market"""
        try:
            if market_key not in self.markets:
                logger.warning(f"Market {market_key} not found")
                return None
            
            market = self.markets[market_key]
            summary = market.summary
            
            if not summary:
                return None
            
            return MarketSummary(
                market=market_key,
                exchanges=summary,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting market summary for {market_key}: {str(e)}")
            return None
    
    def get_all_market_status(self) -> Dict[str, MarketStatus]:
        """Get status for all available markets"""
        all_status = {}
        for market_key in self.markets.keys():
            status = self.get_market_status(market_key)
            if status:
                all_status[market_key] = status
        return all_status
    
    def get_all_market_summaries(self) -> Dict[str, MarketSummary]:
        """Get summary for all available markets"""
        all_summaries = {}
        for market_key in self.markets.keys():
            summary = self.get_market_summary(market_key)
            if summary:
                all_summaries[market_key] = summary
        return all_summaries

# Global instance
market_service = MarketService()
