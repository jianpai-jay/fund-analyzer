"""
信号生成模块
基于多维度分析生成买入/卖出/持有信号
"""
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime


class SignalGenerator:
    """信号生成类"""

    def __init__(self):
        # 信号强度阈值
        self.buy_threshold = 0.6
        self.sell_threshold = -0.4
        self.hold_threshold = 0.3

        # 各维度权重
        self.weights = {
            "technical": 0.30,    # 技术面
            "capital": 0.25,      # 资金面
            "sentiment": 0.20,    # 情绪面
            "news": 0.15,         # 新闻面
            "valuation": 0.10     # 估值面
        }

    def generate_buy_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成买入信号

        Args:
            analysis: 综合分析数据

        Returns:
            dict: 买入信号
        """
        # 计算各维度得分
        scores = self._calculate_dimension_scores(analysis)

        # 计算综合得分
        total_score = self._calculate_total_score(scores)

        # 判断是否满足买入条件
        buy_conditions = self._check_buy_conditions(analysis, scores)

        # 生成信号
        if total_score >= self.buy_threshold and len(buy_conditions) >= 3:
            signal_type = "strong_buy"
            description = "强烈买入信号"
            confidence = min(total_score, 1.0)
        elif total_score >= self.buy_threshold * 0.8 and len(buy_conditions) >= 2:
            signal_type = "buy"
            description = "买入信号"
            confidence = total_score * 0.8
        elif total_score >= self.hold_threshold and len(buy_conditions) >= 2:
            signal_type = "weak_buy"
            description = "弱买入信号"
            confidence = total_score * 0.6
        else:
            return None

        return {
            "signal_type": signal_type,
            "description": description,
            "confidence": confidence,
            "total_score": total_score,
            "dimension_scores": scores,
            "conditions": buy_conditions,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_sell_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成卖出信号

        Args:
            analysis: 综合分析数据

        Returns:
            dict: 卖出信号
        """
        # 计算各维度得分
        scores = self._calculate_dimension_scores(analysis)

        # 计算综合得分
        total_score = self._calculate_total_score(scores)

        # 判断是否满足卖出条件
        sell_conditions = self._check_sell_conditions(analysis, scores)

        # 生成信号
        if total_score <= self.sell_threshold and len(sell_conditions) >= 2:
            signal_type = "strong_sell"
            description = "强烈卖出信号"
            confidence = min(abs(total_score), 1.0)
        elif total_score <= self.sell_threshold * 0.8 and len(sell_conditions) >= 2:
            signal_type = "sell"
            description = "卖出信号"
            confidence = abs(total_score) * 0.8
        elif total_score <= 0 and len(sell_conditions) >= 1:
            signal_type = "weak_sell"
            description = "弱卖出信号"
            confidence = abs(total_score) * 0.6
        else:
            return None

        return {
            "signal_type": signal_type,
            "description": description,
            "confidence": confidence,
            "total_score": total_score,
            "dimension_scores": scores,
            "conditions": sell_conditions,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_hold_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成持有信号

        Args:
            analysis: 综合分析数据

        Returns:
            dict: 持有信号
        """
        # 计算各维度得分
        scores = self._calculate_dimension_scores(analysis)

        # 计算综合得分
        total_score = self._calculate_total_score(scores)

        # 判断是否满足持有条件
        hold_conditions = self._check_hold_conditions(analysis, scores)

        # 生成信号
        if abs(total_score) < self.hold_threshold:
            signal_type = "hold"
            description = "建议持有"
            confidence = 1 - abs(total_score)
        else:
            signal_type = "观望"
            description = "建议观望"
            confidence = 0.5

        return {
            "signal_type": signal_type,
            "description": description,
            "confidence": confidence,
            "total_score": total_score,
            "dimension_scores": scores,
            "conditions": hold_conditions,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _calculate_dimension_scores(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """
        计算各维度得分

        Args:
            analysis: 分析数据

        Returns:
            dict: 各维度得分
        """
        scores = {}

        # 技术面得分
        technical = analysis.get("technical", {})
        technical_signal = technical.get("overall_signal", "neutral")
        if technical_signal == "bullish":
            scores["technical"] = 0.8
        elif technical_signal == "bearish":
            scores["technical"] = -0.8
        else:
            scores["technical"] = 0

        # 资金面得分
        capital = analysis.get("capital", {})
        capital_score = capital.get("total_score", 0)
        scores["capital"] = max(-1, min(1, capital_score))

        # 情绪面得分
        sentiment = analysis.get("sentiment", {})
        sentiment_score = sentiment.get("score", 0)
        scores["sentiment"] = max(-1, min(1, sentiment_score))

        # 新闻面得分
        news = analysis.get("news", {})
        news_score = news.get("total_score", 0)
        scores["news"] = max(-1, min(1, news_score))

        # 估值面得分
        valuation = analysis.get("valuation", {})
        valuation_score = valuation.get("score", 0)
        scores["valuation"] = max(-1, min(1, valuation_score))

        return scores

    def _calculate_total_score(self, scores: Dict[str, float]) -> float:
        """
        计算综合得分

        Args:
            scores: 各维度得分

        Returns:
            float: 综合得分
        """
        total = 0
        for dimension, weight in self.weights.items():
            score = scores.get(dimension, 0)
            total += score * weight

        return total

    def _check_buy_conditions(self, analysis: Dict, scores: Dict) -> List[str]:
        """
        检查买入条件

        Args:
            analysis: 分析数据
            scores: 各维度得分

        Returns:
            list: 满足的条件列表
        """
        conditions = []

        # 技术面条件
        if scores.get("technical", 0) > 0.3:
            conditions.append("技术面看涨")

        # 资金面条件
        if scores.get("capital", 0) > 0.3:
            conditions.append("资金面流入")

        # 情绪面条件
        if scores.get("sentiment", 0) < -0.3:
            conditions.append("情绪面超卖")

        # 新闻面条件
        if scores.get("news", 0) > 0.3:
            conditions.append("新闻面利好")

        # 估值面条件
        if scores.get("valuation", 0) < -0.3:
            conditions.append("估值偏低")

        # MACD金叉
        technical = analysis.get("technical", {})
        macd = technical.get("macd", {})
        if macd.get("signal") == "golden_cross":
            conditions.append("MACD金叉")

        # RSI超卖
        rsi = technical.get("rsi", {})
        if rsi.get("signal") == "oversold":
            conditions.append("RSI超卖")

        # 价格跌破布林带下轨
        bollinger = technical.get("bollinger", {})
        if bollinger.get("signal") == "below_lower":
            conditions.append("价格跌破布林带下轨")

        return conditions

    def _check_sell_conditions(self, analysis: Dict, scores: Dict) -> List[str]:
        """
        检查卖出条件

        Args:
            analysis: 分析数据
            scores: 各维度得分

        Returns:
            list: 满足的条件列表
        """
        conditions = []

        # 技术面条件
        if scores.get("technical", 0) < -0.3:
            conditions.append("技术面看跌")

        # 资金面条件
        if scores.get("capital", 0) < -0.3:
            conditions.append("资金面流出")

        # 情绪面条件
        if scores.get("sentiment", 0) > 0.5:
            conditions.append("情绪面过热")

        # 新闻面条件
        if scores.get("news", 0) < -0.3:
            conditions.append("新闻面利空")

        # 估值面条件
        if scores.get("valuation", 0) > 0.5:
            conditions.append("估值偏高")

        # MACD死叉
        technical = analysis.get("technical", {})
        macd = technical.get("macd", {})
        if macd.get("signal") == "death_cross":
            conditions.append("MACD死叉")

        # RSI超买
        rsi = technical.get("rsi", {})
        if rsi.get("signal") == "overbought":
            conditions.append("RSI超买")

        # 价格突破布林带上轨
        bollinger = technical.get("bollinger", {})
        if bollinger.get("signal") == "above_upper":
            conditions.append("价格突破布林带上轨")

        return conditions

    def _check_hold_conditions(self, analysis: Dict, scores: Dict) -> List[str]:
        """
        检查持有条件

        Args:
            analysis: 分析数据
            scores: 各维度得分

        Returns:
            list: 满足的条件列表
        """
        conditions = []

        # 技术面中性
        if abs(scores.get("technical", 0)) < 0.3:
            conditions.append("技术面中性")

        # 资金面稳定
        if abs(scores.get("capital", 0)) < 0.3:
            conditions.append("资金面稳定")

        # 情绪面中性
        if abs(scores.get("sentiment", 0)) < 0.3:
            conditions.append("情绪面中性")

        # 趋势延续
        technical = analysis.get("technical", {})
        macd = technical.get("macd", {})
        if macd.get("signal") in ["bullish", "bearish"]:
            conditions.append("趋势延续")

        return conditions

    def calculate_signal_strength(self, signal: Dict[str, Any]) -> float:
        """
        计算信号强度

        Args:
            signal: 信号数据

        Returns:
            float: 信号强度 (0-1)
        """
        confidence = signal.get("confidence", 0)
        condition_count = len(signal.get("conditions", []))

        # 基础强度
        strength = confidence

        # 条件数量加成
        if condition_count >= 4:
            strength = min(strength * 1.2, 1.0)
        elif condition_count >= 3:
            strength = min(strength * 1.1, 1.0)

        return strength

    def generate_comprehensive_signal(self, all_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合信号

        Args:
            all_analysis: 所有分析数据

        Returns:
            dict: 综合信号
        """
        # 尝试生成买入信号
        buy_signal = self.generate_buy_signal(all_analysis)
        if buy_signal:
            buy_signal["signal_category"] = "buy"
            return buy_signal

        # 尝试生成卖出信号
        sell_signal = self.generate_sell_signal(all_analysis)
        if sell_signal:
            sell_signal["signal_category"] = "sell"
            return sell_signal

        # 生成持有信号
        hold_signal = self.generate_hold_signal(all_analysis)
        hold_signal["signal_category"] = "hold"
        return hold_signal


# 全局信号生成实例
signal_generator = SignalGenerator()
