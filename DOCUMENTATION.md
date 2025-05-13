# Crypto Trade Simulator Documentation

## Architecture

The simulator is built with a modular architecture:

- `main.py`: Entry point and UI event handling
- `models/`: Core business logic
  - `orderbook.py`: Orderbook state management
  - `calculator.py`: Market impact calculations
  - `simulator.py`: Trade simulation logic
- `ui/`: User interface components
- `utils/`: Helper functions and logging

## Components

### OrderBook

Maintains the current state of the market:
- Bid/Ask prices and quantities
- Historical price and volume data
- Spread calculations

### MarketImpactCalculator

Implements trading cost analysis:
- Almgren-Chriss market impact model
- Slippage estimation
- Maker/Taker ratio calculation
- Fee structure implementation

### TradeSimulator

Coordinates simulation components:
- WebSocket connection management
- Real-time data processing
- Performance monitoring
- Parameter management

## Configuration

Default parameters can be modified in `config.py`:
- WebSocket URL
- Update intervals
- Logging levels
- UI scaling

## Error Handling

The application implements comprehensive error handling:
- Network connection retry logic
- Input validation
- Graceful degradation
- Detailed logging

## Performance Optimization

- Async/await for non-blocking operations
- Efficient data structures
- Memory management for historical data
- UI update throttling