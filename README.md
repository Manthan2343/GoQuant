# Crypto Trade Simulator

A real-time cryptocurrency trading simulator that provides market impact analysis and execution cost estimates using live orderbook data.

## Overview

The Crypto Trade Simulator is a professional-grade tool designed to help traders and institutions estimate trading costs and market impact before executing large orders. It connects to live cryptocurrency exchange data to provide real-time analysis and cost predictions.

## Features

### Market Data Integration
- Real-time orderbook data streaming from major exchanges
- Websocket connection with automatic reconnection
- Order book depth visualization
- Bid-ask spread monitoring
- Market liquidity analysis

### Cost Analysis
- Market impact calculation using custom impact models
- Slippage estimation based on order book depth
- Fee structure analysis for different exchange tiers
- Maker/Taker ratio estimation
- Total execution cost prediction

### Performance Monitoring
- Processing latency tracking
- Connection health monitoring
- Order book update frequency
- System resource usage stats
- Real-time metrics dashboard

### User Interface
- Interactive parameter adjustment
- Real-time data visualization
- Performance metrics display
- Market status indicators
- Clean and intuitive design

## Technical Details

### Architecture
- Asynchronous WebSocket client using `asyncio`
- Event-driven architecture for real-time updates
- Multi-threaded processing for performance
- Modular design for easy extension

### Components
- OrderBook: Maintains the current state of the order book
- MarketImpactCalculator: Estimates trading costs and market impact
- TradeSimulator: Coordinates data flow and simulation logic
- GUI: Provides user interface using PySimpleGUI

### Supported Exchanges
- OKX (Primary)
- Binance (Planned)
- Coinbase (Planned)
- FTX (Planned)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto-trade-simulator.git
cd crypto-trade-simulator
```

2. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Exchange Settings
```yaml
exchange:
  name: "OKX"
  symbol: "BTC-USDT-SWAP"
  websocket_url: "wss://ws.okx.com:8443/ws/v5/public"
```

### Fee Tiers
```yaml
fee_tiers:
  vip0: {maker: 0.0008, taker: 0.0010}
  vip1: {maker: 0.0007, taker: 0.0009}
  vip2: {maker: 0.0006, taker: 0.0008}
  # ...
```

## Usage

### Basic Operation
1. Launch the simulator:
```bash
python main.py
```

2. Configure simulation parameters:
   - Quantity: Trade size in USD (1-1,000,000)
   - Volatility: Expected market volatility (0-100%)
   - Fee Tier: Exchange fee tier (VIP0-VIP5)
   - Order Type: Market or Limit order

3. Monitor results:
   - Expected slippage
   - Fee calculations
   - Market impact estimates
   - Total execution costs
   - Performance metrics

### Advanced Features
- Export simulation results to CSV
- Save configuration presets
- Custom impact model parameters
- Historical data analysis

## Requirements

### Software
- Python 3.8+
- Windows/Linux/Mac OS
- Internet connection for live data

### Python Packages
- websockets>=10.0
- numpy>=1.20.0
- pandas>=1.3.0
- PySimpleGUI>=4.60.0
- aiohttp>=3.8.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- GitHub Issues: Bug reports and feature requests
- Documentation: Wiki pages and inline code comments
- Email: support@example.com

## Roadmap

### Upcoming Features
- Additional exchange integrations
- Advanced order types
- Historical backtesting
- Custom impact models
- API integration
- Portfolio simulation

### Version History
- v1.0.0: Initial release
- v1.1.0: Added performance monitoring
- v1.2.0: Enhanced market impact models
