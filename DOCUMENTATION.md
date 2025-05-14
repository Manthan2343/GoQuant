# Crypto Trade Simulator Documentation

## Introduction

The Crypto Trade Simulator is a Python application designed to simulate cryptocurrency trading costs and market impact using real-time orderbook data. The simulator connects to cryptocurrency exchange websockets to receive live orderbook data, then calculates various trading metrics including slippage, fees, and market impact to provide a comprehensive view of the true cost of executing trades.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Key Components](#key-components)
   - [OrderBook](#orderbook)
   - [MarketImpactCalculator](#marketimpactcalculator)
   - [TradeSimulator](#tradesimulator)
   - [User Interface](#user-interface)
3. [Features](#features)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [Technical Details](#technical-details)
7. [Performance Metrics](#performance-metrics)

## System Architecture

The application follows an asynchronous architecture using Python's `asyncio` library to handle concurrent operations:

1. **Data Collection Layer**: Connects to exchange websockets to receive real-time orderbook data
2. **Calculation Layer**: Processes orderbook data and calculates trading metrics
3. **Presentation Layer**: Displays results through a PySimpleGUI interface

## Key Components

### OrderBook

The `OrderBook` class represents the current state of the market and maintains the order book for a specific trading pair.

**Key Responsibilities:**
- Store and organize bid and ask orders
- Track price history, spread history, and volume data
- Calculate volatility based on recent price movements
- Determine liquidity at various price levels

**Key Methods:**
- `update(data)`: Updates the orderbook with new data from the websocket
- `get_liquidity_at_level(usd_amount, side)`: Calculates the average execution price for a given order size
- `calculate_price_volatility(window_size)`: Estimates price volatility using historical price data

### MarketImpactCalculator

The `MarketImpactCalculator` class estimates the impact of trades on the market.

**Key Responsibilities:**
- Calculate expected slippage for a trade
- Estimate market impact based on order size and market conditions
- Determine maker/taker proportions for orders
- Calculate trading fees based on exchange tier structure

**Key Methods:**
- `calculate_slippage(quantity, side)`: Estimates price slippage for a given order size
- `calculate_market_impact(quantity, side, market_cap)`: Estimates the market impact of an order
- `estimate_maker_taker_proportion(quantity)`: Predicts the proportion of an order that will be filled as maker vs. taker
- `calculate_fees(quantity, fee_tier)`: Calculates expected fees based on exchange fee structures
- `get_net_cost(quantity, fee_tier, side)`: Provides comprehensive cost analysis including slippage, fees, and impact

### TradeSimulator

The `TradeSimulator` class serves as the main controller for the application.

**Key Responsibilities:**
- Manage websocket connections to exchanges
- Update the orderbook with incoming data
- Track performance metrics
- Coordinate simulation parameters and results

**Key Methods:**
- `connect_websocket()`: Establishes and maintains websocket connections
- `update_symbol_and_exchange(exchange, symbol)`: Changes the trading pair being monitored
- `get_performance_metrics()`: Reports system performance statistics
- `get_simulation_results()`: Retrieves calculated trading metrics

### User Interface

The application provides a graphical user interface built with PySimpleGUI with two main sections:

1. **Input Section:**
   - Exchange selection
   - Symbol selection
   - Order type selection
   - Quantity input
   - Volatility parameter
   - Fee tier selection

2. **Output Section:**
   - Market data display (bid/ask/spread)
   - Simulation results (slippage, fees, market impact)
   - Execution breakdown (maker/taker proportions)
   - Performance metrics

## Features

- **Real-time Market Data**: Connects to live exchange websockets for up-to-date orderbook data
- **Multi-Exchange Support**: Works with multiple exchanges (currently OKX and Binance)
- **Dynamic Volatility Calculation**: Estimates volatility from price movements
- **Fee Structure Modeling**: Accounts for different fee tiers across exchanges
- **Maker/Taker Proportion Estimation**: Predicts how orders will be filled
- **Performance Monitoring**: Tracks system performance metrics
- **Interactive UI**: Allows parameter adjustments in real-time

## Configuration

The application comes pre-configured with the following exchange endpoints:

```python
WEBSOCKET_ENDPOINTS = {
    "OKX": {
        "BTC-USDT-SWAP": "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP",
        "ETH-USDT-SWAP": "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/ETH-USDT-SWAP",
        "SOL-USDT-SWAP": "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/SOL-USDT-SWAP",
        "XRP-USDT-SWAP": "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/XRP-USDT-SWAP"
    },
    "Binance": {
        "BTC-USDT": "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/binance/BTC-USDT",
        "ETH-USDT": "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/binance/ETH-USDT",
        "SOL-USDT": "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/binance/SOL-USDT",
        "XRP-USDT": "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/binance/XRP-USDT"
    }
}
```

Fee structures are configured internally based on exchange VIP levels:

| Exchange | VIP Level | Maker Fee (%) | Taker Fee (%) |
|----------|-----------|---------------|---------------|
| OKX      | VIP0      | 0.080         | 0.100         |
| OKX      | VIP1      | 0.070         | 0.090         |
| OKX      | VIP2      | 0.060         | 0.080         |
| OKX      | VIP3      | 0.050         | 0.070         |
| OKX      | VIP4      | 0.030         | 0.050         |
| OKX      | VIP5      | 0.000         | 0.030         |
| Binance  | VIP0      | 0.100         | 0.100         |
| Binance  | VIP1      | 0.080         | 0.100         |
| Binance  | VIP2      | 0.060         | 0.080         |
| Binance  | VIP3      | 0.040         | 0.060         |
| Binance  | VIP4      | 0.020         | 0.040         |
| Binance  | VIP5      | 0.000         | 0.020         |

## Usage Guide

1. **Launch the Application**: Run the script to start the GUI
2. **Configure Parameters**:
   - Select an exchange (OKX or Binance)
   - Choose a trading pair (e.g., BTC-USDT-SWAP)
   - Select order type (market or limit)
   - Enter the order quantity in USD
   - Set expected volatility or use calculated value
   - Choose your fee tier based on exchange VIP level
3. **Apply Changes**: Click the "Apply" button to update parameters
4. **Monitor Results**:
   - View real-time market data
   - Observe calculated slippage, fees, and market impact
   - Check execution breakdown and performance metrics
5. **Exit**: Close the application when finished

## Technical Details

### Dependencies

- **asyncio**: For asynchronous operations
- **websockets**: For connecting to exchange websockets
- **PySimpleGUI**: For the graphical user interface
- **pandas & numpy**: For data processing and calculations
- **scipy**: For statistical calculations
- **logging**: For application logging

### Data Processing

The application processes orderbook data in the following manner:

1. **Data Reception**: Receives JSON data from exchange websockets
2. **Orderbook Update**: Updates internal orderbook representation
3. **Metric Calculation**: Calculates trading metrics based on current orderbook
4. **UI Update**: Displays results in the user interface

### Market Impact Model

The market impact model is based on square-root law commonly used in financial markets:

```
impact_factor = sigma * sqrt(T) * sqrt(quantity_in_usd / daily_volume_estimate)
```

Where:
- `sigma` is the price volatility
- `T` is the time horizon (normalized to 1 day)
- `quantity_in_usd` is the order size
- `daily_volume_estimate` is the estimated daily trading volume

## Performance Metrics

The application tracks several performance metrics:

- **Average Processing Time**: Mean time to process each websocket message
- **Maximum Processing Time**: Longest observed processing time
- **Minimum Processing Time**: Shortest observed processing time
- **Connection Status**: Current state of the websocket connection

These metrics help ensure the application is performing efficiently and provide insight into potential bottlenecks.
