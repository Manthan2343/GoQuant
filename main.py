import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import websockets
from scipy import stats
import PySimpleGUI as sg
from PySimpleGUI import Window

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("trade_simulator")

WEBSOCKET_URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
MAX_ORDERBOOK_LEVELS = 50
UPDATE_INTERVAL_MS = 100

class OrderBook:
    def __init__(self):
        self.asks = []
        self.bids = []
        self.timestamp = None
        self.symbol = ""
        self.exchange = ""
        self.last_update_time = time.time()
        self.price_history = []
        self.spread_history = []
        self.mid_price_history = []
        self.volume_history = []
        
    def update(self, data: Dict):
        self.timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        self.symbol = data["symbol"]
        self.exchange = data["exchange"]
        
        self.asks = [(float(price), float(qty)) for price, qty in data["asks"][:MAX_ORDERBOOK_LEVELS]]
        self.bids = [(float(price), float(qty)) for price, qty in data["bids"][:MAX_ORDERBOOK_LEVELS]]
        
        self.asks.sort(key=lambda x: x[0])
        self.bids.sort(key=lambda x: x[0], reverse=True)
        
        current_time = time.time()
        self.last_update_time = current_time
        
        if self.asks and self.bids:
            best_ask = self.asks[0][0]
            best_bid = self.bids[0][0]
            mid_price = (best_ask + best_bid) / 2
            spread = best_ask - best_bid
            
            self.price_history.append((current_time, mid_price))
            self.spread_history.append((current_time, spread))
            self.mid_price_history.append(mid_price)
            
            threshold = mid_price * 0.001
            near_ask_volume = sum(qty for price, qty in self.asks if price <= mid_price + threshold)
            near_bid_volume = sum(qty for price, qty in self.bids if price >= mid_price - threshold)
            self.volume_history.append((current_time, near_ask_volume + near_bid_volume))
            
            max_history = 300
            if len(self.price_history) > max_history:
                self.price_history = self.price_history[-max_history:]
                self.spread_history = self.spread_history[-max_history:]
                self.mid_price_history = self.mid_price_history[-max_history:]
                self.volume_history = self.volume_history[-max_history:]
    
    def get_liquidity_at_level(self, usd_amount: float, side: str = "buy") -> Tuple[float, float]:
        if not self.asks or not self.bids:
            return 0.0, 0.0
            
        levels = self.asks if side.lower() == "buy" else self.bids
        remaining_amount = usd_amount
        executed_quantity = 0.0
        total_cost = 0.0
        
        for price, quantity in levels:
            level_volume = price * quantity
            if remaining_amount <= 0:
                break
                
            take_volume = min(remaining_amount, level_volume)
            take_quantity = take_volume / price
            
            total_cost += take_quantity * price
            executed_quantity += take_quantity
            remaining_amount -= take_volume
        
        avg_price = total_cost / executed_quantity if executed_quantity > 0 else 0
        return avg_price, executed_quantity


class MarketImpactCalculator:
    def __init__(self, orderbook: OrderBook):
        self.orderbook = orderbook
        self.volatility = 0.0
        
    def update_volatility(self, volatility: float):
        self.volatility = volatility
        
    def calculate_slippage(self, quantity: float, side: str = "buy") -> float:
        if not self.orderbook.asks or not self.orderbook.bids:
            return 0.0
            
        mid_price = (self.orderbook.asks[0][0] + self.orderbook.bids[0][0]) / 2
        expected_price, _ = self.orderbook.get_liquidity_at_level(quantity, side)
        
        if expected_price == 0:
            return 0.0
            
        slippage_pct = ((expected_price / mid_price) - 1) * 100 if side == "buy" else ((mid_price / expected_price) - 1) * 100
        return slippage_pct
    
    def calculate_market_impact(self, quantity: float, side: str = "buy", market_cap: float = 1e10) -> float:
        if not self.orderbook.mid_price_history:
            return 0.0
            
        mid_price = self.orderbook.mid_price_history[-1]
        
        if len(self.orderbook.volume_history) > 10:
            recent_volumes = [vol for _, vol in self.orderbook.volume_history[-10:]]
            avg_tick_volume = sum(recent_volumes) / len(recent_volumes)
            daily_volume_estimate = avg_tick_volume * 86400
        else:
            daily_volume_estimate = market_cap * 0.05
        
        sigma = self.volatility if self.volatility > 0 else 0.02
        T = 1/86400
        
        quantity_in_usd = quantity
        impact_factor = sigma * np.sqrt(T) * np.sqrt(quantity_in_usd / daily_volume_estimate)
        impact_pct = impact_factor * 100
        
        return impact_pct
    
    def estimate_maker_taker_proportion(self, quantity: float) -> Tuple[float, float]:
        if not self.orderbook.asks or not self.orderbook.bids:
            return 0.0, 100.0
            
        mid_price = (self.orderbook.asks[0][0] + self.orderbook.bids[0][0]) / 2
        best_ask_size = self.orderbook.asks[0][1] * self.orderbook.asks[0][0]
        best_bid_size = self.orderbook.bids[0][1] * self.orderbook.bids[0][0]
        
        relative_size = (best_ask_size + best_bid_size) / (2 * quantity)
        
        taker_pct = 100 / (1 + np.exp(relative_size - 1))
        maker_pct = 100 - taker_pct
        
        return maker_pct, taker_pct
    
    def calculate_fees(self, quantity: float, fee_tier: str = "vip0") -> float:
        fee_structure = {
            "vip0": {"maker": 0.0008, "taker": 0.0010},
            "vip1": {"maker": 0.0007, "taker": 0.0009},
            "vip2": {"maker": 0.0006, "taker": 0.0008},
            "vip3": {"maker": 0.0005, "taker": 0.0007},
            "vip4": {"maker": 0.0003, "taker": 0.0005},
            "vip5": {"maker": 0.0000, "taker": 0.0003},
        }
        
        tier_fees = fee_structure.get(fee_tier.lower(), fee_structure["vip0"])
        maker_fee = tier_fees["maker"]
        taker_fee = tier_fees["taker"]
        
        maker_pct, taker_pct = self.estimate_maker_taker_proportion(quantity)
        
        weighted_fee_rate = (maker_pct/100 * maker_fee) + (taker_pct/100 * taker_fee)
        fee_pct = weighted_fee_rate * 100
        
        return fee_pct
    
    def get_net_cost(self, quantity: float, fee_tier: str = "vip0", side: str = "buy") -> Dict:
        slippage_pct = self.calculate_slippage(quantity, side)
        fee_pct = self.calculate_fees(quantity, fee_tier)
        market_impact_pct = self.calculate_market_impact(quantity, side)
        
        maker_pct, taker_pct = self.estimate_maker_taker_proportion(quantity)
        
        net_cost_pct = slippage_pct + fee_pct + market_impact_pct
        
        return {
            "slippage_pct": slippage_pct,
            "fee_pct": fee_pct,
            "market_impact_pct": market_impact_pct,
            "maker_pct": maker_pct,
            "taker_pct": taker_pct,
            "net_cost_pct": net_cost_pct
        }


class TradeSimulator:
    def __init__(self):
        self.orderbook = OrderBook()
        self.market_impact_calculator = MarketImpactCalculator(self.orderbook)
        self.running = True
        self.exchange = "OKX"
        self.symbol = "BTC-USDT-SWAP"
        self.order_type = "market"
        self.quantity = 100.0
        self.volatility = 0.02
        self.fee_tier = "vip0"
        
        self.process_times = []
        self.last_tick_time = time.time()
        
    async def connect_websocket(self):
        max_retries = 5
        retry_delay = 2
        retry_count = 0
        
        while self.running and retry_count < max_retries:
            try:
                logger.info(f"Connecting to {WEBSOCKET_URL}")
                async with websockets.connect(WEBSOCKET_URL) as websocket:
                    retry_count = 0
                    while self.running:
                        try:
                            start_time = time.time()
                            self.last_tick_time = start_time
                            
                            response = await websocket.recv()
                            data = json.loads(response)
                            
                            self.orderbook.update(data)
                            self.market_impact_calculator.update_volatility(self.volatility)
                            
                            end_time = time.time()
                            process_time = (end_time - start_time) * 1000
                            self.process_times.append(process_time)
                            
                            if len(self.process_times) > 100:
                                self.process_times = self.process_times[-100:]
                                
                        except websockets.exceptions.ConnectionClosed:
                            logger.error("WebSocket connection closed")
                            break
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {e}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing data: {e}")
                            await asyncio.sleep(1)
                            
            except Exception as e:
                retry_count += 1
                logger.error(f"Connection attempt {retry_count} failed: {e}")
                if retry_count < max_retries:
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Stopping connection attempts.")
                    break
    
    def get_performance_metrics(self) -> Dict:
        if not self.process_times:
            return {"avg_latency": 0, "max_latency": 0, "min_latency": 0}
            
        return {
            "avg_latency": sum(self.process_times) / len(self.process_times),
            "max_latency": max(self.process_times),
            "min_latency": min(self.process_times)
        }
    
    def get_simulation_results(self) -> Dict:
        results = self.market_impact_calculator.get_net_cost(
            self.quantity, 
            self.fee_tier, 
            "buy"
        )
        
        performance = self.get_performance_metrics()
        results.update(performance)
        
        return results


def create_layout():
    input_column = [
        [sg.Text("Exchange:", size=(15, 1)), sg.InputText("OKX", key="-EXCHANGE-", size=(20, 1), disabled=True)],
        [sg.Text("Symbol:", size=(15, 1)), sg.InputText("BTC-USDT-SWAP", key="-SYMBOL-", size=(20, 1), disabled=True)],
        [sg.Text("Order Type:", size=(15, 1)), 
         sg.Combo(["market", "limit"], default_value="market", key="-ORDER_TYPE-", size=(20, 1))],
        [sg.Text("Quantity (USD):", size=(15, 1)), 
         sg.InputText("100", key="-QUANTITY-", size=(20, 1))],
        [sg.Text("Volatility (%):", size=(15, 1)), 
         sg.InputText("2", key="-VOLATILITY-", size=(20, 1))],
        [sg.Text("Fee Tier:", size=(15, 1)), 
         sg.Combo(["vip0", "vip1", "vip2", "vip3", "vip4", "vip5"], 
                  default_value="vip0", key="-FEE_TIER-", size=(20, 1))],
        [sg.Button("Apply", key="-APPLY-")],
        [sg.HSeparator()],
        [sg.Text("Market Data", font=("Helvetica", 12, "bold"))],
        [sg.Text("Best Bid:", size=(15, 1)), sg.Text("", key="-BEST_BID-", size=(20, 1))],
        [sg.Text("Best Ask:", size=(15, 1)), sg.Text("", key="-BEST_ASK-", size=(20, 1))],
        [sg.Text("Spread (%):", size=(15, 1)), sg.Text("", key="-SPREAD-", size=(20, 1))],
        [sg.Text("Last Update:", size=(15, 1)), sg.Text("", key="-LAST_UPDATE-", size=(20, 1))],
    ]
    
    output_column = [
        [sg.Text("Simulation Results", font=("Helvetica", 12, "bold"))],
        [sg.Text("Expected Slippage (%):", size=(20, 1)), sg.Text("", key="-SLIPPAGE-", size=(15, 1))],
        [sg.Text("Expected Fees (%):", size=(20, 1)), sg.Text("", key="-FEES-", size=(15, 1))],
        [sg.Text("Market Impact (%):", size=(20, 1)), sg.Text("", key="-MARKET_IMPACT-", size=(15, 1))],
        [sg.Text("Net Cost (%):", size=(20, 1)), sg.Text("", key="-NET_COST-", size=(15, 1), font=("Helvetica", 10, "bold"))],
        [sg.HSeparator()],
        [sg.Text("Execution Breakdown", font=("Helvetica", 12, "bold"))],
        [sg.Text("Maker Proportion (%):", size=(20, 1)), sg.Text("", key="-MAKER-", size=(15, 1))],
        [sg.Text("Taker Proportion (%):", size=(20, 1)), sg.Text("", key="-TAKER-", size=(15, 1))],
        [sg.HSeparator()],
        [sg.Text("Performance Metrics", font=("Helvetica", 12, "bold"))],
        [sg.Text("Avg Processing Time (ms):", size=(20, 1)), sg.Text("", key="-AVG_LATENCY-", size=(15, 1))],
        [sg.Text("Max Processing Time (ms):", size=(20, 1)), sg.Text("", key="-MAX_LATENCY-", size=(15, 1))],
        [sg.Text("Min Processing Time (ms):", size=(20, 1)), sg.Text("", key="-MIN_LATENCY-", size=(15, 1))],
        [sg.Text("Connection Status:", size=(20, 1)), sg.Text("Disconnected", key="-STATUS-", size=(15, 1))],
    ]
    
    layout = [
        [sg.Text("Crypto Trade Simulator", font=("Helvetica", 16))],
        [
            sg.Column(input_column, vertical_alignment='top'),
            sg.VSeparator(),
            sg.Column(output_column, vertical_alignment='top')
        ],
        [sg.Button("Exit")]
    ]
    
    return layout


async def update_ui(window, simulator):
    while simulator.running:
        try:
            if simulator.orderbook.asks and simulator.orderbook.bids:
                best_ask = simulator.orderbook.asks[0][0]
                best_bid = simulator.orderbook.bids[0][0]
                spread_pct = (best_ask - best_bid) / best_bid * 100
                
                window["-BEST_BID-"].update(f"{best_bid:.2f}")
                window["-BEST_ASK-"].update(f"{best_ask:.2f}")
                window["-SPREAD-"].update(f"{spread_pct:.4f}%")
                
                last_update = datetime.fromtimestamp(simulator.last_tick_time).strftime("%H:%M:%S.%f")[:-3]
                window["-LAST_UPDATE-"].update(last_update)
                window["-STATUS-"].update("Connected", text_color="green")
            
            results = simulator.get_simulation_results()
            
            window["-SLIPPAGE-"].update(f"{results['slippage_pct']:.4f}%")
            window["-FEES-"].update(f"{results['fee_pct']:.4f}%")
            window["-MARKET_IMPACT-"].update(f"{results['market_impact_pct']:.4f}%")
            window["-NET_COST-"].update(f"{results['net_cost_pct']:.4f}%")
            window["-MAKER-"].update(f"{results['maker_pct']:.2f}%")
            window["-TAKER-"].update(f"{results['taker_pct']:.2f}%")
            
            window["-AVG_LATENCY-"].update(f"{results['avg_latency']:.2f}")
            window["-MAX_LATENCY-"].update(f"{results['max_latency']:.2f}")
            window["-MIN_LATENCY-"].update(f"{results['min_latency']:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating UI: {e}")
        
        await asyncio.sleep(UPDATE_INTERVAL_MS / 1000)


async def handle_events(window, simulator):
    while simulator.running:
        event, values = window.read(timeout=10)
        
        if event in (sg.WIN_CLOSED, "Exit"):
            simulator.running = False
            break
            
        elif event == "-APPLY-":
            try:
                simulator.quantity = float(values["-QUANTITY-"])
                simulator.volatility = float(values["-VOLATILITY-"]) / 100
                simulator.fee_tier = values["-FEE_TIER-"]
                simulator.order_type = values["-ORDER_TYPE-"]
                logger.info(f"Updated parameters: quantity={simulator.quantity}, "
                           f"volatility={simulator.volatility}, fee_tier={simulator.fee_tier}")
            except Exception as e:
                logger.error(f"Error updating parameters: {e}")
        
        await asyncio.sleep(0.01)


async def main():
    simulator = TradeSimulator()
    
    window = Window("Crypto Trade Simulator", create_layout(), finalize=True)
    
    tasks = []
    try:
        websocket_task = asyncio.create_task(simulator.connect_websocket())
        ui_task = asyncio.create_task(update_ui(window, simulator))
        events_task = asyncio.create_task(handle_events(window, simulator))
        tasks = [websocket_task, ui_task, events_task]
        
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        window.close()
        simulator.running = False
        logger.info("Application closed")


def signal_handler(sig, frame):
    logger.info("Received interrupt signal")
    raise KeyboardInterrupt


if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
    finally:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
        if not loop.is_closed():
            loop.close()
        logger.info("Event loop closed")