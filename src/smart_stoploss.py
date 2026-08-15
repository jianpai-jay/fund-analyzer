"""
智能止损模块
根据波动率动态计算止盈止损位
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional


class SmartStoplossAnalyzer:
    """智能止损分析类"""

    def __init__(self):
        # 默认参数
        self.default_stoploss_pct = 5.0  # 默认止损5%
        self.default_takeprofit_pct = 15.0  # 默认止盈15%
        self.volatility_factor = 1.5  # 波动率调整因子
        self.min_stoploss = 3.0  # 最小止损3%
        self.max_stoploss = 15.0  # 最大止损15%
        self.min_takeprofit = 8.0  # 最小止盈8%
        self.max_takeprofit = 30.0  # 最大止盈30%

    def calculate_dynamic_stoploss(self, nav_data: pd.DataFrame, risk_tolerance: str = "medium") -> Dict[str, Any]:
        """
        动态计算止损止盈位

        Args:
            nav_data: 净值数据
            risk_tolerance: 风险偏好 (low, medium, high)

        Returns:
            dict: 止损止盈建议
        """
        if nav_data is None or nav_data.empty or len(nav_data) < 20:
            return {
                "has_data": False,
                "message": "数据不足，使用默认止损止盈"
            }

        # 计算波动率
        returns = nav_data['nav'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252) * 100  # 年化波动率百分比

        # 计算最大回撤
        nav_series = nav_data['nav'].values
        peak = np.maximum.accumulate(nav_series)
        drawdown = (peak - nav_series) / peak
        max_drawdown = np.max(drawdown) * 100

        # 根据波动率计算动态止损
        if volatility < 10:
            # 低波动
            volatility_multiplier = 1.0
            volatility_level = "low"
        elif volatility < 20:
            # 中等波动
            volatility_multiplier = 1.2
            volatility_level = "medium"
        elif volatility < 30:
            # 高波动
            volatility_multiplier = 1.5
            volatility_level = "high"
        else:
            # 极高波动
            volatility_multiplier = 2.0
            volatility_level = "extreme"

        # 根据风险偏好调整
        risk_multiplier = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.2
        }.get(risk_tolerance, 1.0)

        # 计算止损位
        stoploss_pct = self.default_stoploss_pct * volatility_multiplier * risk_multiplier
        stoploss_pct = max(self.min_stoploss, min(self.max_stoploss, stoploss_pct))

        # 计算止盈位 (止损位的2-3倍)
        takeprofit_multiplier = 2.5 if risk_tolerance == "medium" else 2.0 if risk_tolerance == "low" else 3.0
        takeprofit_pct = stoploss_pct * takeprofit_multiplier
        takeprofit_pct = max(self.min_takeprofit, min(self.max_takeprofit, takeprofit_pct))

        # 计算移动止损 (trailing stop)
        trailing_stop_pct = stoploss_pct * 0.8  # 移动止损比固定止损更紧

        # 当前净值
        current_nav = nav_data['nav'].iloc[-1]

        # 计算具体价位
        stoploss_price = current_nav * (1 - stoploss_pct / 100)
        takeprofit_price = current_nav * (1 + takeprofit_pct / 100)
        trailing_stop_price = current_nav * (1 - trailing_stop_pct / 100)

        # 生成建议
        if volatility_level in ["high", "extreme"]:
            advice = "波动率较高，建议收紧止损"
        elif max_drawdown > 15:
            advice = "历史回撤较大，建议设置较紧止损"
        else:
            advice = "波动率适中，可设置标准止损"

        return {
            "has_data": True,
            "current_nav": round(current_nav, 4),
            "volatility": round(volatility, 2),
            "volatility_level": volatility_level,
            "max_drawdown": round(max_drawdown, 2),
            "stoploss": {
                "fixed": {
                    "percentage": round(stoploss_pct, 2),
                    "price": round(stoploss_price, 4)
                },
                "trailing": {
                    "percentage": round(trailing_stop_pct, 2),
                    "price": round(trailing_stop_price, 4)
                }
            },
            "takeprofit": {
                "percentage": round(takeprofit_pct, 2),
                "price": round(takeprofit_price, 4)
            },
            "risk_tolerance": risk_tolerance,
            "advice": advice
        }

    def calculate_position_size(self, nav_data: pd.DataFrame, capital: float = 100000,
                                risk_per_trade: float = 2.0) -> Dict[str, Any]:
        """
        计算仓位大小 (Kelly公式简化版)

        Args:
            nav_data: 净值数据
            capital: 总资金
            risk_per_trade: 每笔交易风险比例(%)

        Returns:
            dict: 仓位建议
        """
        if nav_data is None or nav_data.empty or len(nav_data) < 20:
            return {
                "has_data": False,
                "message": "数据不足"
            }

        # 计算波动率
        returns = nav_data['nav'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)

        # 计算胜率 (简化: 假设上涨天数占比)
        win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0.5

        # 计算盈亏比 (简化: 平均上涨幅度/平均下跌幅度)
        avg_gain = returns[returns > 0].mean() if (returns > 0).any() else 0.01
        avg_loss = abs(returns[returns < 0].mean()) if (returns < 0).any() else 0.01
        profit_loss_ratio = avg_gain / avg_loss

        # Kelly公式 (简化版)
        kelly_fraction = win_rate - (1 - win_rate) / profit_loss_ratio
        kelly_fraction = max(0, min(0.5, kelly_fraction))  # 限制在0-50%

        # 根据波动率调整仓位
        if volatility > 0.3:
            volatility_adjustment = 0.6
        elif volatility > 0.2:
            volatility_adjustment = 0.8
        else:
            volatility_adjustment = 1.0

        # 计算建议仓位
        suggested_fraction = kelly_fraction * volatility_adjustment
        suggested_position = capital * suggested_fraction

        # 计算止损金额
        stoploss_pct = self.default_stoploss_pct / 100
        max_loss = suggested_position * stoploss_pct

        return {
            "has_data": True,
            "capital": capital,
            "volatility": round(volatility * 100, 2),
            "win_rate": round(win_rate * 100, 2),
            "profit_loss_ratio": round(profit_loss_ratio, 2),
            "kelly_fraction": round(kelly_fraction * 100, 2),
            "suggested_fraction": round(suggested_fraction * 100, 2),
            "suggested_position": round(suggested_position, 2),
            "max_loss": round(max_loss, 2),
            "advice": f"建议仓位{suggested_fraction*100:.0f}%，最大亏损控制在{max_loss:.0f}元"
        }

    def generate_stoploss_advice(self, nav_data: pd.DataFrame, signal_type: str = "hold") -> Dict[str, Any]:
        """
        生成止损止盈综合建议

        Args:
            nav_data: 净值数据
            signal_type: 信号类型 (buy, sell, hold)

        Returns:
            dict: 综合建议
        """
        # 计算动态止损
        stoploss_result = self.calculate_dynamic_stoploss(nav_data)

        # 计算仓位
        position_result = self.calculate_position_size(nav_data)

        # 根据信号类型调整建议
        if signal_type == "buy":
            action = "建仓"
            advice = "建议分批买入，设置好止损位"
        elif signal_type == "sell":
            action = "减仓"
            advice = "建议逐步减仓，锁定利润"
        elif signal_type == "hold":
            action = "持有"
            advice = "建议继续持有，关注止损位"
        else:
            action = "观望"
            advice = "建议观望，等待更好时机"

        # 综合建议
        if stoploss_result.get("has_data") and position_result.get("has_data"):
            summary = (
                f"当前波动率{stoploss_result['volatility']}%，"
                f"建议止损{stoploss_result['stoploss']['fixed']['percentage']}%，"
                f"止盈{stoploss_result['takeprofit']['percentage']}%，"
                f"仓位{position_result['suggested_fraction']}%"
            )
        else:
            summary = "数据不足，使用默认建议"

        return {
            "has_data": True,
            "action": action,
            "advice": advice,
            "stoploss": stoploss_result,
            "position": position_result,
            "summary": summary
        }


# 全局智能止损分析实例
smart_stoploss_analyzer = SmartStoplossAnalyzer()
