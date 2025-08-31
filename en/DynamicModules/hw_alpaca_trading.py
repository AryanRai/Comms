"""
Alpaca Trading Dynamic Module for Comms Engine
===============================================

This module connects to the Alpaca API to stream live trading data
and trading signals through the Comms Engine system.

Features:
- Real-time market data streaming
- Paper trading integration
- Portfolio monitoring
- Risk management alerts
- Trading signals based on technical indicators
"""

import asyncio
import json
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import traceback

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import alpaca_trade_api as tradeapi
    import pandas as pd
    import numpy as np
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    tradeapi = None
    pd = None
    np = None

# Import the Stream class from the module init
from __init__ import Stream

@dataclass
class TradingSignal:
    """Trading signal data structure"""
    symbol: str
    signal_type: str  # 'buy', 'sell', 'hold'
    strength: float  # 0.0 to 1.0
    price: float
    reason: str
    timestamp: datetime

@dataclass
class PortfolioData:
    """Portfolio data structure"""
    buying_power: float
    cash: float
    portfolio_value: float
    day_trade_count: int
    positions: List[Dict]

class AlpacaTradingModule:
    """Main trading module class"""
    
    def __init__(self):
        self.config = {
            "update_rate": 1.0,  # Update every second
            "max_symbols": 50,
            "enable_paper_trading": True,
            "risk_management": True,
            "technical_indicators": True
        }
        
        # Alpaca API configuration
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = "https://paper-api.alpaca.markets"
        self.api = None
        
        # Trading universe - popular stocks and ETFs
        self.universe = [
            # AI/Tech
            'NVDA', 'GOOGL', 'MSFT', 'AAPL', 'AMZN', 'META', 'TSLA',
            # Growth
            'PLTR', 'SNOW', 'CRWD', 'DDOG', 'MDB', 'NET', 'OKTA',
            # ETFs
            'SPY', 'QQQ', 'VTI', 'ARKK', 'XLK', 'SMH',
            # Defensive
            'JNJ', 'PG', 'KO', 'WMT', 'BRK.B', 'VZ'
        ]
        
        # Initialize streams
        self.streams = {}
        self.setup_streams()
        
        # Trading state
        self.portfolio = None
        self.positions = {}
        self.signals = {}
        self.market_data = {}
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def setup_streams(self):
        """Initialize all trading streams"""
        # Portfolio streams
        self.streams["portfolio_value"] = Stream(
            stream_id="portfolio_value",
            name="Portfolio Value",
            datatype="float",
            unit="USD",
            status="active",
            metadata={"category": "portfolio", "type": "value"}
        )
        
        self.streams["buying_power"] = Stream(
            stream_id="buying_power",
            name="Buying Power",
            datatype="float",
            unit="USD",
            status="active",
            metadata={"category": "portfolio", "type": "buying_power"}
        )
        
        self.streams["cash"] = Stream(
            stream_id="cash",
            name="Cash",
            datatype="float",
            unit="USD",
            status="active",
            metadata={"category": "portfolio", "type": "cash"}
        )
        
        # Market data streams for key symbols
        key_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA']
        
        for symbol in key_symbols:
            # Price stream
            self.streams[f"{symbol}_price"] = Stream(
                stream_id=f"{symbol}_price",
                name=f"{symbol} Price",
                datatype="float",
                unit="USD",
                status="active",
                metadata={"category": "market_data", "symbol": symbol, "type": "price"}
            )
            
            # Volume stream
            self.streams[f"{symbol}_volume"] = Stream(
                stream_id=f"{symbol}_volume",
                name=f"{symbol} Volume",
                datatype="int",
                unit="shares",
                status="active",
                metadata={"category": "market_data", "symbol": symbol, "type": "volume"}
            )
            
            # Trading signal stream
            self.streams[f"{symbol}_signal"] = Stream(
                stream_id=f"{symbol}_signal",
                name=f"{symbol} Signal",
                datatype="string",
                unit="signal",
                status="active",
                metadata={"category": "trading_signal", "symbol": symbol, "type": "signal"}
            )
            
            # Signal strength stream
            self.streams[f"{symbol}_signal_strength"] = Stream(
                stream_id=f"{symbol}_signal_strength",
                name=f"{symbol} Signal Strength",
                datatype="float",
                unit="strength",
                status="active",
                metadata={"category": "trading_signal", "symbol": symbol, "type": "strength"}
            )
        
        # Market status streams
        self.streams["market_open"] = Stream(
            stream_id="market_open",
            name="Market Open",
            datatype="bool",
            unit="boolean",
            status="active",
            metadata={"category": "market_status", "type": "open"}
        )
        
        self.streams["market_hours"] = Stream(
            stream_id="market_hours",
            name="Market Hours",
            datatype="string",
            unit="hours",
            status="active",
            metadata={"category": "market_status", "type": "hours"}
        )
        
        # Risk management streams
        self.streams["portfolio_heat"] = Stream(
            stream_id="portfolio_heat",
            name="Portfolio Heat",
            datatype="float",
            unit="percentage",
            status="active",
            metadata={"category": "risk_management", "type": "heat"}
        )
        
        self.streams["risk_alert"] = Stream(
            stream_id="risk_alert",
            name="Risk Alert",
            datatype="string",
            unit="alert",
            status="active",
            metadata={"category": "risk_management", "type": "alert"}
        )
        
        self.logger.info(f"Initialized {len(self.streams)} trading streams")
    
    def initialize_alpaca(self):
        """Initialize Alpaca API connection"""
        if not ALPACA_AVAILABLE:
            self.logger.error("Alpaca API not available. Install with: pip install alpaca-trade-api")
            return False
        
        if not self.api_key or not self.secret_key:
            self.logger.error("Alpaca API credentials not found. Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables")
            return False
        
        try:
            self.api = tradeapi.REST(
                self.api_key,
                self.secret_key,
                self.base_url,
                api_version='v2'
            )
            
            # Test connection
            account = self.api.get_account()
            self.logger.info(f"Connected to Alpaca API - Account: {account.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Alpaca API: {e}")
            return False
    
    def get_portfolio_data(self):
        """Get current portfolio data"""
        if not self.api:
            return None
        
        try:
            account = self.api.get_account()
            positions = self.api.list_positions()
            
            portfolio = PortfolioData(
                buying_power=float(account.buying_power),
                cash=float(account.cash),
                portfolio_value=float(account.portfolio_value),
                day_trade_count=int(account.daytrade_count),
                positions=[{
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'side': pos.side,
                    'market_value': float(pos.market_value),
                    'cost_basis': float(pos.cost_basis),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc)
                } for pos in positions]
            )
            
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio data: {e}")
            return None
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get latest market data for symbols"""
        if not self.api:
            return {}
        
        try:
            # Get latest quotes
            quotes = self.api.get_latest_quotes(symbols, feed='iex')
            
            # Get latest bars for volume data
            bars = self.api.get_latest_bars(symbols, feed='iex')
            
            market_data = {}
            
            for symbol in symbols:
                if symbol in quotes and symbol in bars:
                    quote = quotes[symbol]
                    bar = bars[symbol]
                    
                    market_data[symbol] = {
                        'price': (quote.bid_price + quote.ask_price) / 2,
                        'bid': quote.bid_price,
                        'ask': quote.ask_price,
                        'volume': bar.volume,
                        'timestamp': quote.timestamp
                    }
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return {}
    
    def calculate_technical_indicators(self, symbol: str) -> Dict[str, float]:
        """Calculate technical indicators for a symbol"""
        if not self.api:
            return {}
        
        try:
            # Get historical data (last 50 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=50)
            
            bars = self.api.get_bars(
                symbol,
                tradeapi.TimeFrame.Day,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                feed='iex'
            )
            
            if not bars:
                return {}
            
            df = bars.df
            
            if len(df) < 20:
                return {}
            
            # Calculate indicators
            indicators = {}
            
            # Simple Moving Averages
            indicators['sma_5'] = df['close'].rolling(window=5).mean().iloc[-1]
            indicators['sma_20'] = df['close'].rolling(window=20).mean().iloc[-1]
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = 100 - (100 / (1 + rs.iloc[-1]))
            
            # Price momentum
            if len(df) >= 10:
                indicators['momentum_10d'] = (df['close'].iloc[-1] / df['close'].iloc[-10] - 1) * 100
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {}
    
    def generate_trading_signal(self, symbol: str, market_data: Dict, indicators: Dict) -> TradingSignal:
        """Generate trading signal based on market data and indicators"""
        if not market_data or not indicators:
            return TradingSignal(
                symbol=symbol,
                signal_type='hold',
                strength=0.0,
                price=0.0,
                reason='Insufficient data',
                timestamp=datetime.now()
            )
        
        current_price = market_data.get('price', 0.0)
        
        # Simple momentum strategy
        signal_type = 'hold'
        strength = 0.0
        reason = 'No clear signal'
        
        # Get indicators
        sma_5 = indicators.get('sma_5', 0)
        sma_20 = indicators.get('sma_20', 0)
        rsi = indicators.get('rsi', 50)
        momentum = indicators.get('momentum_10d', 0)
        
        # Buy signals
        if (sma_5 > sma_20 and  # Short MA above long MA
            rsi < 70 and        # Not overbought
            momentum > 2):      # Positive momentum
            signal_type = 'buy'
            strength = min(0.8, abs(momentum) / 10)
            reason = f'Bullish: SMA crossover, RSI={rsi:.1f}, Momentum={momentum:.1f}%'
        
        # Sell signals
        elif (sma_5 < sma_20 and  # Short MA below long MA
              rsi > 30 and        # Not oversold
              momentum < -2):     # Negative momentum
            signal_type = 'sell'
            strength = min(0.8, abs(momentum) / 10)
            reason = f'Bearish: SMA crossover, RSI={rsi:.1f}, Momentum={momentum:.1f}%'
        
        # Hold with weak signals
        else:
            strength = 0.2
            reason = f'Hold: RSI={rsi:.1f}, Momentum={momentum:.1f}%'
        
        return TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            strength=strength,
            price=current_price,
            reason=reason,
            timestamp=datetime.now()
        )
    
    def check_market_status(self):
        """Check if market is open"""
        if not self.api:
            return False
        
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except Exception as e:
            self.logger.error(f"Error checking market status: {e}")
            return False
    
    def calculate_portfolio_heat(self, portfolio: PortfolioData) -> float:
        """Calculate portfolio heat (risk exposure)"""
        if not portfolio.positions:
            return 0.0
        
        try:
            total_exposure = sum(abs(pos['market_value']) for pos in portfolio.positions)
            heat = total_exposure / portfolio.portfolio_value if portfolio.portfolio_value > 0 else 0.0
            return min(heat, 1.0)  # Cap at 100%
        except Exception as e:
            self.logger.error(f"Error calculating portfolio heat: {e}")
            return 0.0
    
    def update_streams(self):
        """Update all stream values"""
        try:
            # Update portfolio streams
            portfolio = self.get_portfolio_data()
            if portfolio:
                self.streams["portfolio_value"].update_value(portfolio.portfolio_value)
                self.streams["buying_power"].update_value(portfolio.buying_power)
                self.streams["cash"].update_value(portfolio.cash)
                
                # Update risk management
                heat = self.calculate_portfolio_heat(portfolio)
                self.streams["portfolio_heat"].update_value(heat)
                
                if heat > 0.8:  # 80% heat threshold
                    self.streams["risk_alert"].update_value("HIGH_HEAT")
                elif heat > 0.6:  # 60% heat threshold
                    self.streams["risk_alert"].update_value("MEDIUM_HEAT")
                else:
                    self.streams["risk_alert"].update_value("LOW_HEAT")
            
            # Update market status
            market_open = self.check_market_status()
            self.streams["market_open"].update_value(market_open)
            
            if market_open:
                self.streams["market_hours"].update_value("OPEN")
            else:
                self.streams["market_hours"].update_value("CLOSED")
            
            # Update market data and signals for key symbols
            key_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'TSLA']
            market_data = self.get_market_data(key_symbols)
            
            for symbol in key_symbols:
                if symbol in market_data:
                    data = market_data[symbol]
                    
                    # Update price and volume
                    self.streams[f"{symbol}_price"].update_value(data['price'])
                    self.streams[f"{symbol}_volume"].update_value(data['volume'])
                    
                    # Calculate indicators and generate signals
                    if self.config.get('technical_indicators', True):
                        indicators = self.calculate_technical_indicators(symbol)
                        signal = self.generate_trading_signal(symbol, data, indicators)
                        
                        self.streams[f"{symbol}_signal"].update_value(signal.signal_type)
                        self.streams[f"{symbol}_signal_strength"].update_value(signal.strength)
                        
                        # Store signal for logging
                        self.signals[symbol] = signal
            
            # Log summary
            active_signals = [sig for sig in self.signals.values() if sig.signal_type != 'hold']
            if active_signals:
                self.logger.info(f"Active signals: {len(active_signals)}")
                for signal in active_signals:
                    self.logger.info(f"  {signal.symbol}: {signal.signal_type.upper()} "
                                   f"(strength: {signal.strength:.2f}) - {signal.reason}")
            
        except Exception as e:
            self.logger.error(f"Error updating streams: {e}")
            traceback.print_exc()
    
    async def update_streams_forever(self):
        """Continuously update streams"""
        self.logger.info("Starting Alpaca Trading Module...")
        
        # Initialize Alpaca connection
        if not self.initialize_alpaca():
            self.logger.error("Failed to initialize Alpaca API")
            return
        
        self.logger.info("Alpaca Trading Module started successfully")
        
        while True:
            try:
                self.update_streams()
                await asyncio.sleep(self.config["update_rate"])
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

# Factory function for module creation
def create_module():
    """Create and return an instance of the trading module"""
    return AlpacaTradingModule()

# Main execution for testing
if __name__ == "__main__":
    module = create_module()
    asyncio.run(module.update_streams_forever())