# Crypto Trade Simulator

A real-time cryptocurrency trading simulator that provides market impact analysis and execution cost estimates using live orderbook data.

## Features

- Real-time orderbook data streaming
- Market impact calculation using Almgren-Chriss model
- Execution cost analysis
- Maker/Taker ratio estimation
- Performance metrics monitoring
- User-friendly GUI interface

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

## Usage

1. Run the simulator:
```bash
python main.py
```

2. Enter simulation parameters:
   - Quantity: Trade size in USD
   - Volatility: Expected market volatility
   - Fee Tier: Exchange fee tier (VIP0-VIP5)
   - Order Type: Market or Limit

3. Click "Apply" to update parameters and view results.

## Requirements

- Python 3.8+
- Windows/Linux/Mac OS
- Internet connection for live data

## License

MIT License