"""
回测模块
模拟历史投资策略的收益
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class BacktestAnalyzer:
    """回测分析类"""

    def __init__(self):
        pass

    def run_simple_backtest(self, nav_data: pd.DataFrame, strategy: str = "buy_and_hold",
                            initial_capital: float = 10000) -> Dict[str, Any]:
        """
        运行简单回测

        Args:
            nav_data: 净值数据
            strategy: 策略类型 (buy_and_hold, ma_cross, rsi)
            initial_capital: 初始资金

        Returns:
            dict: 回测结果
        """
        if nav_data is None or nav_data.empty or len(nav_data) < 10:
            return {
                "has_data": False,
                "message": "数据不足，无法回测"
            }

        nav_series = nav_data['nav'].values

        if strategy == "buy_and_hold":
            result = self._backtest_buy_and_hold(nav_series, initial_capital)
        elif strategy == "ma_cross":
            result = self._backtest_ma_cross(nav_series, initial_capital)
        elif strategy == "rsi":
            result = self._backtest_rsi(nav_series, initial_capital)
        else:
            result = self._backtest_buy_and_hold(nav_series, initial_capital)

        # 计算基准收益（买入持有）
        benchmark = self._backtest_buy_and_hold(nav_series, initial_capital)

        # 计算超额收益
        excess_return = result["total_return_rate"] - benchmark["total_return_rate"]

        return {
            "has_data": True,
            "strategy": strategy,
            "initial_capital": initial_capital,
            "final_capital": result["final_capital"],
            "total_return": result["total_return"],
            "total_return_rate": result["total_return_rate"],
            "annual_return": result["annual_return"],
            "max_drawdown": result["max_drawdown"],
            "sharpe_ratio": result["sharpe_ratio"],
            "trade_count": result["trade_count"],
            "benchmark_return": benchmark["total_return_rate"],
            "excess_return": excess_return,
            "description": self._generate_backtest_description(result, benchmark)
        }

    def _backtest_buy_and_hold(self, nav_series: np.ndarray, initial_capital: float) -> Dict[str, Any]:
        """买入持有策略"""
        # 买入
        shares = initial_capital / nav_series[0]
        final_capital = shares * nav_series[-1]

        # 计算收益
        total_return = final_capital - initial_capital
        total_return_rate = (final_capital / initial_capital - 1) * 100

        # 计算年化收益
        days = len(nav_series)
        years = days / 252
        annual_return = ((final_capital / initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0

        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown(nav_series)

        # 计算夏普比率
        returns = np.diff(nav_series) / nav_series[:-1]
        sharpe_ratio = self._calculate_sharpe(returns)

        return {
            "final_capital": round(final_capital, 2),
            "total_return": round(total_return, 2),
            "total_return_rate": round(total_return_rate, 2),
            "annual_return": round(annual_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "trade_count": 1
        }

    def _backtest_ma_cross(self, nav_series: np.ndarray, initial_capital: float,
                           short_period: int = 5, long_period: int = 20) -> Dict[str, Any]:
        """均线交叉策略"""
        capital = initial_capital
        shares = 0
        position = 0  # 0: 空仓, 1: 满仓
        trade_count = 0
        max_capital = initial_capital

        for i in range(long_period, len(nav_series)):
            # 计算均线
            short_ma = np.mean(nav_series[i-short_period:i])
            long_ma = np.mean(nav_series[i-long_period:i])

            # 金叉买入
            if short_ma > long_ma and position == 0:
                shares = capital / nav_series[i]
                capital = 0
                position = 1
                trade_count += 1

            # 死叉卖出
            elif short_ma < long_ma and position == 1:
                capital = shares * nav_series[i]
                shares = 0
                position = 0
                trade_count += 1

            # 更新最大资金
            current_value = capital + shares * nav_series[i]
            max_capital = max(max_capital, current_value)

        # 最终结算
        final_capital = capital + shares * nav_series[-1]

        # 计算收益
        total_return = final_capital - initial_capital
        total_return_rate = (final_capital / initial_capital - 1) * 100

        # 计算年化收益
        days = len(nav_series)
        years = days / 252
        annual_return = ((final_capital / initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0

        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown(nav_series)

        # 计算夏普比率
        returns = np.diff(nav_series) / nav_series[:-1]
        sharpe_ratio = self._calculate_sharpe(returns)

        return {
            "final_capital": round(final_capital, 2),
            "total_return": round(total_return, 2),
            "total_return_rate": round(total_return_rate, 2),
            "annual_return": round(annual_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "trade_count": trade_count
        }

    def _backtest_rsi(self, nav_series: np.ndarray, initial_capital: float,
                      period: int = 14, oversold: int = 30, overbought: int = 70) -> Dict[str, Any]:
        """RSI策略"""
        capital = initial_capital
        shares = 0
        position = 0
        trade_count = 0

        for i in range(period + 1, len(nav_series)):
            # 计算RSI
            deltas = np.diff(nav_series[i-period-1:i])
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            # RSI超卖买入
            if rsi < oversold and position == 0:
                shares = capital / nav_series[i]
                capital = 0
                position = 1
                trade_count += 1

            # RSI超买卖出
            elif rsi > overbought and position == 1:
                capital = shares * nav_series[i]
                shares = 0
                position = 0
                trade_count += 1

        # 最终结算
        final_capital = capital + shares * nav_series[-1]

        # 计算收益
        total_return = final_capital - initial_capital
        total_return_rate = (final_capital / initial_capital - 1) * 100

        # 计算年化收益
        days = len(nav_series)
        years = days / 252
        annual_return = ((final_capital / initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0

        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown(nav_series)

        # 计算夏普比率
        returns = np.diff(nav_series) / nav_series[:-1]
        sharpe_ratio = self._calculate_sharpe(returns)

        return {
            "final_capital": round(final_capital, 2),
            "total_return": round(total_return, 2),
            "total_return_rate": round(total_return_rate, 2),
            "annual_return": round(annual_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "trade_count": trade_count
        }

    def _calculate_max_drawdown(self, prices: np.ndarray) -> float:
        """计算最大回撤"""
        if len(prices) == 0:
            return 0
        peak = np.maximum.accumulate(prices)
        drawdown = (peak - prices) / peak
        return np.max(drawdown) * 100

    def _calculate_sharpe(self, returns: np.ndarray, risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        if len(returns) == 0 or np.std(returns) == 0:
            return 0
        annual_return = np.mean(returns) * 252
        annual_volatility = np.std(returns) * np.sqrt(252)
        return (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0

    def _generate_backtest_description(self, result: Dict, benchmark: Dict) -> str:
        """生成回测描述"""
        excess = result["total_return_rate"] - benchmark["total_return_rate"]

        if excess > 5:
            desc = f"策略大幅跑赢基准，超额收益{excess:.1f}%"
        elif excess > 0:
            desc = f"策略跑赢基准，超额收益{excess:.1f}%"
        elif excess > -5:
            desc = f"策略略逊于基准，落后{abs(excess):.1f}%"
        else:
            desc = f"策略大幅跑输基准，落后{abs(excess):.1f}%"

        return desc

    def compare_strategies(self, nav_data: pd.DataFrame, initial_capital: float = 10000) -> Dict[str, Any]:
        """
        比较不同策略

        Args:
            nav_data: 净值数据
            initial_capital: 初始资金

        Returns:
            dict: 策略比较结果
        """
        strategies = ["buy_and_hold", "ma_cross", "rsi"]
        results = {}

        for strategy in strategies:
            results[strategy] = self.run_simple_backtest(nav_data, strategy, initial_capital)

        # 找出最佳策略
        best_strategy = max(results.items(), key=lambda x: x[1].get("total_return_rate", 0))

        return {
            "has_data": True,
            "strategies": results,
            "best_strategy": best_strategy[0],
            "best_return": best_strategy[1].get("total_return_rate", 0)
        }


# 全局回测分析实例
backtest_analyzer = BacktestAnalyzer()
