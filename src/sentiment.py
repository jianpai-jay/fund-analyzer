"""
情绪分析模块
分析市场情绪和投资者情绪
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class SentimentAnalyzer:
    """情绪分析类"""

    def __init__(self):
        pass

    def calculate_fear_greed_index(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算恐慌贪婪指数

        Args:
            market_data: 市场数据

        Returns:
            dict: 恐慌贪婪指数
        """
        # 指标权重
        weights = {
            "market_momentum": 0.25,  # 市场动量
            "stock_strength": 0.25,    # 股票强度
            "market_breadth": 0.20,    # 市场广度
            "put_call_ratio": 0.15,    # 看跌看涨比率
            "volatility": 0.15         # 波动率
        }

        scores = {}

        # 市场动量（使用大盘涨跌幅）
        market_change = market_data.get("market_change", 0)
        if market_change > 2:
            scores["market_momentum"] = 80
        elif market_change > 1:
            scores["market_momentum"] = 70
        elif market_change > 0:
            scores["market_momentum"] = 60
        elif market_change > -1:
            scores["market_momentum"] = 40
        elif market_change > -2:
            scores["market_momentum"] = 30
        else:
            scores["market_momentum"] = 20

        # 股票强度（上涨股票比例）
        up_ratio = market_data.get("up_ratio", 0.5)
        scores["stock_strength"] = up_ratio * 100

        # 市场广度（涨跌家数比）
        advance_decline = market_data.get("advance_decline_ratio", 1)
        if advance_decline > 2:
            scores["market_breadth"] = 80
        elif advance_decline > 1.5:
            scores["market_breadth"] = 70
        elif advance_decline > 1:
            scores["market_breadth"] = 60
        elif advance_decline > 0.67:
            scores["market_breadth"] = 40
        elif advance_decline > 0.5:
            scores["market_breadth"] = 30
        else:
            scores["market_breadth"] = 20

        # 看跌看涨比率（简化处理）
        put_call_ratio = market_data.get("put_call_ratio", 1)
        if put_call_ratio < 0.7:
            scores["put_call_ratio"] = 80  # 看涨情绪高
        elif put_call_ratio < 0.9:
            scores["put_call_ratio"] = 65
        elif put_call_ratio < 1.1:
            scores["put_call_ratio"] = 50
        elif put_call_ratio < 1.3:
            scores["put_call_ratio"] = 35
        else:
            scores["put_call_ratio"] = 20  # 看跌情绪高

        # 波动率（波动率高表示恐慌）
        volatility = market_data.get("volatility", 20)
        if volatility < 15:
            scores["volatility"] = 80  # 低波动，贪婪
        elif volatility < 20:
            scores["volatility"] = 65
        elif volatility < 25:
            scores["volatility"] = 50
        elif volatility < 30:
            scores["volatility"] = 35
        else:
            scores["volatility"] = 20  # 高波动，恐慌

        # 计算加权平均
        total_score = 0
        for key, weight in weights.items():
            total_score += scores.get(key, 50) * weight

        # 判断情绪状态
        if total_score >= 80:
            sentiment = "extreme_greed"
            description = "极度贪婪，市场可能过热"
            advice = "考虑减仓或止盈"
        elif total_score >= 60:
            sentiment = "greed"
            description = "贪婪情绪，市场偏强"
            advice = "谨慎追高"
        elif total_score >= 40:
            sentiment = "neutral"
            description = "情绪中性"
            advice = "保持观望"
        elif total_score >= 20:
            sentiment = "fear"
            description = "恐慌情绪，市场偏弱"
            advice = "可考虑逢低买入"
        else:
            sentiment = "extreme_fear"
            description = "极度恐慌，市场可能超卖"
            advice = "可能是较好的买入时机"

        return {
            "index": total_score,
            "sentiment": sentiment,
            "description": description,
            "advice": advice,
            "components": scores
        }

    def calculate_market_sentiment_score(self, market_data: Dict[str, Any]) -> float:
        """
        计算市场情绪得分

        Args:
            market_data: 市场数据

        Returns:
            float: 情绪得分 (-1 到 1)
        """
        fear_greed = self.calculate_fear_greed_index(market_data)
        # 转换为 -1 到 1 的范围
        return (fear_greed["index"] - 50) / 50

    def analyze_investor_sentiment(self, fund_flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析投资者情绪

        Args:
            fund_flow_data: 基金资金流向数据

        Returns:
            dict: 投资者情绪分析
        """
        # 基金申赎情况
        subscription = fund_flow_data.get("subscription", 0)
        redemption = fund_flow_data.get("redemption", 0)

        # 计算净申购率
        if subscription + redemption > 0:
            net_subscription_rate = (subscription - redemption) / (subscription + redemption)
        else:
            net_subscription_rate = 0

        # 散户情绪
        retail_sentiment = fund_flow_data.get("retail_sentiment", 0)

        # 机构情绪
        institutional_sentiment = fund_flow_data.get("institutional_sentiment", 0)

        # 计算综合情绪
        if net_subscription_rate > 0.2:
            sentiment = "very_optimistic"
            description = "投资者非常乐观，大量申购"
        elif net_subscription_rate > 0.05:
            sentiment = "optimistic"
            description = "投资者偏乐观"
        elif net_subscription_rate < -0.2:
            sentiment = "very_pessimistic"
            description = "投资者非常悲观，大量赎回"
        elif net_subscription_rate < -0.05:
            sentiment = "pessimistic"
            description = "投资者偏悲观"
        else:
            sentiment = "neutral"
            description = "投资者情绪中性"

        return {
            "sentiment": sentiment,
            "description": description,
            "net_subscription_rate": net_subscription_rate,
            "retail_sentiment": retail_sentiment,
            "institutional_sentiment": institutional_sentiment
        }

    def calculate_sentiment_score(self, fear_greed_index: Dict, investor_sentiment: Dict) -> float:
        """
        计算综合情绪分数

        Args:
            fear_greed_index: 恐慌贪婪指数
            investor_sentiment: 投资者情绪

        Returns:
            float: 综合情绪分数 (-1 到 1)
        """
        # 恐慌贪婪指数分数 (0-100 -> -1 到 1)
        fear_greed_score = (fear_greed_index.get("index", 50) - 50) / 50

        # 投资者情绪分数
        investor_score = investor_sentiment.get("net_subscription_rate", 0)

        # 综合分数（加权平均）
        total_score = fear_greed_score * 0.6 + investor_score * 0.4

        return max(-1, min(1, total_score))

    def generate_sentiment_signal(self, sentiment_score: float) -> Dict[str, Any]:
        """
        生成情绪信号

        Args:
            sentiment_score: 情绪分数

        Returns:
            dict: 情绪信号
        """
        if sentiment_score > 0.5:
            signal = "strong_bullish"
            description = "情绪极度乐观，可能过热"
            advice = "警惕回调风险"
        elif sentiment_score > 0.2:
            signal = "bullish"
            description = "情绪偏乐观"
            advice = "可适当参与"
        elif sentiment_score > -0.2:
            signal = "neutral"
            description = "情绪中性"
            advice = "保持观望"
        elif sentiment_score > -0.5:
            signal = "bearish"
            description = "情绪偏悲观"
            advice = "谨慎操作"
        else:
            signal = "strong_bearish"
            description = "情绪极度悲观，可能超卖"
            advice = "可能是布局机会"

        return {
            "signal": signal,
            "score": sentiment_score,
            "description": description,
            "advice": advice
        }


# 全局情绪分析实例
sentiment_analyzer = SentimentAnalyzer()
