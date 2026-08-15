"""
定投策略分析模块
分析定投策略和回测
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class DCAStrategyAnalyzer:
    """定投策略分析类"""

    def __init__(self):
        pass

    def analyze_dca_strategy(self, nav_data: pd.DataFrame, fund_code: str, monthly_amount: float = 1000) -> Dict[str, Any]:
        """
        分析定投策略

        Args:
            nav_data: 净值数据
            fund_code: 基金代码
            monthly_amount: 每月定投金额

        Returns:
            dict: 定投分析结果
        """
        if nav_data is None or nav_data.empty:
            return {
                "fund_code": fund_code,
                "has_data": False,
                "analysis": "无净值数据"
            }

        # 计算定投收益
        dca_result = self._calculate_dca_returns(nav_data, monthly_amount)

        # 计算一次性投资收益
        lump_sum_result = self._calculate_lump_sum_returns(nav_data, monthly_amount)

        # 计算定投效率
        efficiency = self._calculate_dca_efficiency(dca_result, lump_sum_result)

        # 生成定投信号
        signal = self._generate_dca_signal(dca_result, efficiency)

        return {
            "fund_code": fund_code,
            "has_data": True,
            "monthly_amount": monthly_amount,
            "dca_result": dca_result,
            "lump_sum_result": lump_sum_result,
            "efficiency": efficiency,
            "signal": signal
        }

    def _calculate_dca_returns(self, nav_data: pd.DataFrame, monthly_amount: float) -> Dict[str, Any]:
        """
        计算定投收益

        Args:
            nav_data: 净值数据
            monthly_amount: 每月定投金额

        Returns:
            dict: 定投收益
        """
        nav_series = nav_data['nav']
        dates = nav_data['date']

        # 模拟定投（每月第一个交易日）
        total_shares = 0
        total_invested = 0
        investment_records = []

        # 按月分组
        monthly_groups = {}
        for i, (date, nav) in enumerate(zip(dates, nav_series)):
            month_key = date.strftime('%Y-%m')
            if month_key not in monthly_groups:
                monthly_groups[month_key] = []
            monthly_groups[month_key].append((date, nav))

        # 每月定投
        for month_key, group in sorted(monthly_groups.items()):
            # 取该月第一个交易日
            first_date, first_nav = group[0]

            if first_nav > 0:
                shares = monthly_amount / first_nav
                total_shares += shares
                total_invested += monthly_amount

                investment_records.append({
                    "date": first_date.strftime('%Y-%m-%d'),
                    "nav": first_nav,
                    "amount": monthly_amount,
                    "shares": shares,
                    "total_shares": total_shares,
                    "total_invested": total_invested
                })

        # 计算当前价值
        final_nav = nav_series.iloc[-1]
        current_value = total_shares * final_nav

        # 计算收益
        total_return = current_value - total_invested
        return_rate = (total_return / total_invested * 100) if total_invested > 0 else 0

        # 计算年化收益
        if len(nav_data) > 0:
            days = (nav_data['date'].iloc[-1] - nav_data['date'].iloc[0]).days
            years = days / 365.25
            if years > 0 and total_invested > 0:
                annual_return = ((current_value / total_invested) ** (1 / years) - 1) * 100
            else:
                annual_return = 0
        else:
            annual_return = 0

        return {
            "total_invested": total_invested,
            "current_value": current_value,
            "total_return": total_return,
            "return_rate": return_rate,
            "annual_return": annual_return,
            "total_shares": total_shares,
            "final_nav": final_nav,
            "investment_count": len(investment_records),
            "records": investment_records
        }

    def _calculate_lump_sum_returns(self, nav_data: pd.DataFrame, total_amount: float) -> Dict[str, Any]:
        """
        计算一次性投资收益

        Args:
            nav_data: 净值数据
            total_amount: 总投资金额

        Returns:
            dict: 一次性投资收益
        """
        nav_series = nav_data['nav']

        # 第一天买入
        first_nav = nav_series.iloc[0]
        shares = total_amount / first_nav

        # 计算当前价值
        final_nav = nav_series.iloc[-1]
        current_value = shares * final_nav

        # 计算收益
        total_return = current_value - total_amount
        return_rate = (total_return / total_amount * 100) if total_amount > 0 else 0

        # 计算年化收益
        days = (nav_data['date'].iloc[-1] - nav_data['date'].iloc[0]).days
        years = days / 365.25
        if years > 0:
            annual_return = ((current_value / total_amount) ** (1 / years) - 1) * 100
        else:
            annual_return = 0

        return {
            "total_invested": total_amount,
            "current_value": current_value,
            "total_return": total_return,
            "return_rate": return_rate,
            "annual_return": annual_return,
            "first_nav": first_nav,
            "final_nav": final_nav
        }

    def _calculate_dca_efficiency(self, dca_result: Dict, lump_sum_result: Dict) -> Dict[str, Any]:
        """
        计算定投效率

        Args:
            dca_result: 定投收益
            lump_sum_result: 一次性投资收益

        Returns:
            dict: 定投效率
        """
        dca_return = dca_result.get("return_rate", 0)
        lump_sum_return = lump_sum_result.get("return_rate", 0)

        # 计算效率比率
        if lump_sum_return != 0:
            efficiency_ratio = dca_return / lump_sum_return
        else:
            efficiency_ratio = 1.0

        # 判断定投是否更优
        if efficiency_ratio > 1:
            is_dca_better = True
            description = "定投策略优于一次性投资"
        elif efficiency_ratio > 0.8:
            is_dca_better = False
            description = "定投策略接近一次性投资"
        else:
            is_dca_better = False
            description = "定投策略不如一次性投资"

        return {
            "efficiency_ratio": efficiency_ratio,
            "is_dca_better": is_dca_better,
            "description": description
        }

    def _generate_dca_signal(self, dca_result: Dict, efficiency: Dict) -> Dict[str, Any]:
        """
        生成定投信号

        Args:
            dca_result: 定投收益
            efficiency: 定投效率

        Returns:
            dict: 定投信号
        """
        return_rate = dca_result.get("return_rate", 0)
        is_better = efficiency.get("is_dca_better", False)

        # 判断信号
        if return_rate > 10 and is_better:
            signal = "strong_buy"
            description = "定投收益良好，建议继续定投"
        elif return_rate > 0:
            signal = "hold"
            description = "定投收益为正，建议继续"
        elif return_rate > -10:
            signal = "cautious"
            description = "定投出现亏损，建议观望"
        else:
            signal = "stop"
            description = "定投亏损较大，建议暂停"

        return {
            "signal": signal,
            "description": description,
            "return_rate": return_rate
        }

    def calculate_moving_average_dca(self, nav_data: pd.DataFrame, short_period: int = 5, long_period: int = 20) -> Dict[str, Any]:
        """
        计算均线定投策略

        Args:
            nav_data: 净值数据
            short_period: 短期均线周期
            long_period: 长期均线周期

        Returns:
            dict: 均线定投分析
        """
        if nav_data is None or nav_data.empty or len(nav_data) < long_period:
            return {"has_data": False}

        nav_series = nav_data['nav']

        # 计算均线
        short_ma = nav_series.rolling(window=short_period).mean()
        long_ma = nav_series.rolling(window=long_period).mean()

        # 判断金叉/死叉
        current_short = short_ma.iloc[-1]
        current_long = long_ma.iloc[-1]
        prev_short = short_ma.iloc[-2]
        prev_long = long_ma.iloc[-2]

        signal = "hold"
        if prev_short <= prev_long and current_short > current_long:
            signal = "buy"
        elif prev_short >= prev_long and current_short < current_long:
            signal = "sell"

        return {
            "has_data": True,
            "current_short_ma": current_short,
            "current_long_ma": current_long,
            "signal": signal,
            "description": "金叉买入" if signal == "buy" else ("死叉卖出" if signal == "sell" else "持有")
        }

    def calculate_value_averaging(self, nav_data: pd.DataFrame, target_growth: float = 0.01) -> Dict[str, Any]:
        """
        计算价值平均策略

        Args:
            nav_data: 净值数据
            target_growth: 目标增长率

        Returns:
            dict: 价值平均分析
        """
        if nav_data is None or nav_data.empty:
            return {"has_data": False}

        nav_series = nav_data['nav']

        # 价值平均策略
        portfolio_value = 0
        target_value = 0
        total_invested = 0
        investment_records = []

        for i, nav in enumerate(nav_series):
            # 目标价值每月增长
            target_value = 1000 * (1 + target_growth) ** i

            # 需要投资的金额
            investment_needed = target_value - portfolio_value

            if investment_needed > 0:
                shares = investment_needed / nav
                portfolio_value += investment_needed
                total_invested += investment_needed

                investment_records.append({
                    "date": nav_data['date'].iloc[i].strftime('%Y-%m-%d'),
                    "nav": nav,
                    "investment": investment_needed,
                    "portfolio_value": portfolio_value,
                    "total_invested": total_invested
                })
            else:
                # 赎回多余资金
                redemption = -investment_needed
                portfolio_value -= redemption
                total_invested -= redemption

        # 计算最终收益
        final_value = portfolio_value
        total_return = final_value - total_invested
        return_rate = (total_return / total_invested * 100) if total_invested > 0 else 0

        return {
            "has_data": True,
            "total_invested": total_invested,
            "final_value": final_value,
            "total_return": total_return,
            "return_rate": return_rate,
            "investment_count": len(investment_records)
        }


# 全局定投策略分析实例
dca_strategy_analyzer = DCAStrategyAnalyzer()
