"""
基金分析模块
计算基础指标和风险指标
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional


class FundAnalyzer:
    """基金分析类"""

    def __init__(self):
        pass

    def analyze_fund(self, fund_code: str, fund_name: str,
                     nav_data: pd.DataFrame, fund_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        综合分析基金

        Args:
            fund_code: 基金代码
            fund_name: 基金名称
            nav_data: 净值数据
            fund_info: 基金信息

        Returns:
            dict: 分析结果
        """
        if nav_data is None or nav_data.empty:
            return {
                "code": fund_code,
                "name": fund_name,
                "error": "无法获取数据"
            }

        # 计算基础指标
        basic_metrics = self.calculate_basic_metrics(nav_data)

        # 计算风险指标
        risk_metrics = self.calculate_risk_metrics(nav_data)

        # 计算综合评分
        overall_score = self.calculate_overall_score(basic_metrics, risk_metrics)

        # 合并结果
        result = {
            "code": fund_code,
            "name": fund_name,
            **basic_metrics,
            **risk_metrics,
            "overall_score": overall_score
        }

        # 添加基金信息
        if fund_info:
            result["fund_info"] = fund_info

        return result

    def calculate_basic_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算基础指标

        Args:
            df: 净值数据

        Returns:
            dict: 基础指标
        """
        try:
            nav_series = df['nav']
            return_series = df['daily_return'].dropna()

            # 最新净值
            latest_nav = nav_series.iloc[-1]

            # 日涨跌幅
            if len(nav_series) >= 2:
                daily_return = (nav_series.iloc[-1] / nav_series.iloc[-2] - 1) * 100
            else:
                daily_return = 0.0

            # 区间收益率
            total_return = (nav_series.iloc[-1] / nav_series.iloc[0] - 1) * 100

            # 平均日收益率
            avg_daily_return = return_series.mean() if not return_series.empty else 0.0

            # 收益率标准差
            return_std = return_series.std() if not return_series.empty else 0.0

            return {
                "latest_nav": round(latest_nav, 4),
                "daily_return": round(daily_return, 2),
                "total_return": round(total_return, 2),
                "avg_daily_return": round(avg_daily_return, 4),
                "return_std": round(return_std, 4)
            }

        except Exception as e:
            print(f"计算基础指标时出错: {e}")
            return {
                "latest_nav": 0,
                "daily_return": 0,
                "total_return": 0,
                "avg_daily_return": 0,
                "return_std": 0
            }

    def calculate_risk_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算风险指标

        Args:
            df: 净值数据

        Returns:
            dict: 风险指标
        """
        try:
            nav_series = df['nav']
            return_series = df['daily_return'].dropna()

            # 波动率 (年化) - 将百分比转换为小数
            return_decimal = return_series / 100
            volatility = return_decimal.std() * np.sqrt(252) if not return_decimal.empty else 0.0

            # 最大回撤
            max_drawdown = self._calculate_max_drawdown(nav_series)

            # 夏普比率 (假设无风险利率3%)
            sharpe_ratio = self._calculate_sharpe(return_series)

            # 卡玛比率
            calmar_ratio = self._calculate_calmar(nav_series, return_series)

            # 索提诺比率
            sortino_ratio = self._calculate_sortino(return_series)

            return {
                "volatility": round(volatility * 100, 2),
                "max_drawdown": round(max_drawdown, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "calmar_ratio": round(calmar_ratio, 2),
                "sortino_ratio": round(sortino_ratio, 2)
            }

        except Exception as e:
            print(f"计算风险指标时出错: {e}")
            return {
                "volatility": 0,
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "calmar_ratio": 0,
                "sortino_ratio": 0
            }

    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """
        计算最大回撤

        Args:
            prices: 价格序列

        Returns:
            float: 最大回撤百分比
        """
        if prices.empty:
            return 0.0

        # 计算累计最大值
        peak = prices.expanding(min_periods=1).max()

        # 计算回撤
        drawdown = (prices - peak) / peak

        # 返回最大回撤（取绝对值）
        return abs(drawdown.min()) * 100

    def _calculate_sharpe(self, returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """
        计算夏普比率

        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率

        Returns:
            float: 夏普比率
        """
        if returns.empty or returns.std() == 0:
            return 0.0

        # 年化收益率
        annual_return = returns.mean() * 252

        # 年化波动率
        annual_volatility = returns.std() * np.sqrt(252)

        # 夏普比率
        sharpe = (annual_return - risk_free_rate) / annual_volatility

        return sharpe

    def _calculate_calmar(self, nav: pd.Series, returns: pd.Series) -> float:
        """
        计算卡玛比率

        Args:
            nav: 净值序列
            returns: 收益率序列

        Returns:
            float: 卡玛比率
        """
        if nav.empty or returns.empty:
            return 0.0

        # 年化收益率
        annual_return = returns.mean() * 252

        # 最大回撤
        max_drawdown = self._calculate_max_drawdown(nav)

        if max_drawdown == 0:
            return 0.0

        # 卡玛比率
        calmar = annual_return / (max_drawdown / 100)

        return calmar

    def _calculate_sortino(self, returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """
        计算索提诺比率

        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率

        Returns:
            float: 索提诺比率
        """
        if returns.empty:
            return 0.0

        # 年化收益率
        annual_return = returns.mean() * 252

        # 下行波动率
        downside_returns = returns[returns < 0]
        if downside_returns.empty:
            return 0.0

        downside_volatility = downside_returns.std() * np.sqrt(252)

        if downside_volatility == 0:
            return 0.0

        # 索提诺比率
        sortino = (annual_return - risk_free_rate) / downside_volatility

        return sortino

    def calculate_overall_score(self, basic_metrics: Dict, risk_metrics: Dict) -> str:
        """
        计算综合评分

        Args:
            basic_metrics: 基础指标
            risk_metrics: 风险指标

        Returns:
            str: 综合评级
        """
        try:
            # 计算评分
            score = 0

            # 收益率评分 (30%)
            total_return = basic_metrics.get('total_return', 0)
            if total_return > 10:
                score += 30
            elif total_return > 5:
                score += 25
            elif total_return > 0:
                score += 20
            elif total_return > -5:
                score += 15
            else:
                score += 10

            # 波动率评分 (25%)
            volatility = risk_metrics.get('volatility', 0)
            if volatility < 10:
                score += 25
            elif volatility < 15:
                score += 20
            elif volatility < 20:
                score += 15
            elif volatility < 25:
                score += 10
            else:
                score += 5

            # 最大回撤评分 (25%)
            max_drawdown = risk_metrics.get('max_drawdown', 0)
            if max_drawdown < 5:
                score += 25
            elif max_drawdown < 10:
                score += 20
            elif max_drawdown < 15:
                score += 15
            elif max_drawdown < 20:
                score += 10
            else:
                score += 5

            # 夏普比率评分 (20%)
            sharpe_ratio = risk_metrics.get('sharpe_ratio', 0)
            if sharpe_ratio > 2:
                score += 20
            elif sharpe_ratio > 1.5:
                score += 18
            elif sharpe_ratio > 1:
                score += 15
            elif sharpe_ratio > 0.5:
                score += 12
            else:
                score += 8

            # 根据分数返回评级
            if score >= 85:
                return "⭐⭐⭐⭐⭐ 优秀"
            elif score >= 70:
                return "⭐⭐⭐⭐ 良好"
            elif score >= 55:
                return "⭐⭐⭐ 中等"
            elif score >= 40:
                return "⭐⭐ 较差"
            else:
                return "⭐ 差"

        except Exception as e:
            print(f"计算综合评分时出错: {e}")
            return "⭐⭐ 中等"


# 全局分析实例
analyzer = FundAnalyzer()
