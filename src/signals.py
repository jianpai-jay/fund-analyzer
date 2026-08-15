"""
信号生成模块 - 增强版
基于多维度分析生成详细的买入/卖出/持有信号
"""
from typing import Dict, Any, List
from datetime import datetime


class SignalGenerator:
    """信号生成类"""

    def __init__(self):
        # 各维度权重
        self.weights = {
            "technical": 0.30,
            "capital": 0.25,
            "sentiment": 0.15,
            "news": 0.15,
            "valuation": 0.10,
            "manager": 0.05
        }

    def generate_comprehensive_signal(self, all_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合信号

        Args:
            all_analysis: 所有分析数据

        Returns:
            dict: 综合信号
        """
        # 计算各维度得分和分析
        dimensions = self._analyze_dimensions(all_analysis)

        # 计算综合得分
        total_score = self._calculate_total_score(dimensions)

        # 生成详细建议
        recommendation = self._generate_recommendation(total_score, dimensions, all_analysis)

        # 生成风险提示
        risk_warnings = self._generate_risk_warnings(all_analysis, dimensions)

        # 生成操作建议
        action_plan = self._generate_action_plan(total_score, dimensions, all_analysis)

        return {
            "signal_category": recommendation["category"],
            "signal_type": recommendation["type"],
            "description": recommendation["description"],
            "confidence": recommendation["confidence"],
            "total_score": total_score,
            "dimensions": dimensions,
            "recommendation": recommendation,
            "risk_warnings": risk_warnings,
            "action_plan": action_plan,
            "conditions": recommendation.get("conditions", []),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _analyze_dimensions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析各维度"""
        dimensions = {}

        # 技术面分析
        technical = analysis.get("technical", {})
        tech_score = self._score_technical(technical)
        dimensions["technical"] = {
            "score": tech_score,
            "weight": self.weights["technical"],
            "signal": technical.get("overall_signal", "neutral"),
            "details": self._get_technical_details(technical)
        }

        # 资金面分析
        capital = analysis.get("capital", {})
        cap_score = self._score_capital(capital)
        dimensions["capital"] = {
            "score": cap_score,
            "weight": self.weights["capital"],
            "signal": capital.get("overall_signal", "neutral"),
            "details": self._get_capital_details(capital)
        }

        # 情绪面分析
        sentiment = analysis.get("sentiment", {})
        sent_score = self._score_sentiment(sentiment)
        dimensions["sentiment"] = {
            "score": sent_score,
            "weight": self.weights["sentiment"],
            "signal": sentiment.get("overall_signal", "neutral"),
            "details": self._get_sentiment_details(sentiment)
        }

        # 新闻面分析
        news = analysis.get("news", {})
        news_score = self._score_news(news)
        dimensions["news"] = {
            "score": news_score,
            "weight": self.weights["news"],
            "signal": news.get("overall_signal", "neutral"),
            "details": self._get_news_details(news)
        }

        # 估值分析
        valuation = analysis.get("valuation", {})
        val_score = valuation.get("score", 0)
        dimensions["valuation"] = {
            "score": val_score,
            "weight": self.weights["valuation"],
            "signal": "undervalued" if val_score > 0.3 else ("overvalued" if val_score < -0.3 else "fair"),
            "details": valuation.get("description", "估值中性")
        }

        # 基金经理分析
        manager = analysis.get("manager", {})
        mgr_score = manager.get("signal", {}).get("score", 0.5) if isinstance(manager.get("signal"), dict) else 0.5
        dimensions["manager"] = {
            "score": (mgr_score - 0.5) * 2,  # 转换为 -1 到 1
            "weight": self.weights["manager"],
            "signal": manager.get("signal", {}).get("signal", "neutral") if isinstance(manager.get("signal"), dict) else "neutral",
            "details": manager.get("name", "暂无数据")
        }

        return dimensions

    def _score_technical(self, technical: Dict) -> float:
        """技术面评分"""
        signal = technical.get("overall_signal", "neutral")
        strength = technical.get("signal_strength", 0)

        if signal == "bullish":
            return min(0.5 + strength * 0.5, 1.0)
        elif signal == "bearish":
            return max(-0.5 - strength * 0.5, -1.0)
        return 0

    def _score_capital(self, capital: Dict) -> float:
        """资金面评分"""
        return capital.get("total_score", 0)

    def _score_sentiment(self, sentiment: Dict) -> float:
        """情绪面评分"""
        score = sentiment.get("score", 0)
        # 逆向思维：情绪过高时看跌，情绪过低时看涨
        return -score * 0.5

    def _score_news(self, news: Dict) -> float:
        """新闻面评分"""
        return news.get("total_score", 0)

    def _get_technical_details(self, technical: Dict) -> List[str]:
        """获取技术面详情"""
        details = []
        macd = technical.get("macd_signal", "")
        rsi = technical.get("rsi_signal", "")
        bollinger = technical.get("bollinger_signal", "")

        if macd == "golden_cross":
            details.append("MACD金叉，短期看涨")
        elif macd == "death_cross":
            details.append("MACD死叉，短期看跌")
        elif macd == "bullish_divergence":
            details.append("出现底背离，可能反弹")
        elif macd == "bearish_divergence":
            details.append("出现顶背离，注意风险")

        if rsi == "oversold":
            details.append("RSI超卖，可能反弹")
        elif rsi == "overbought":
            details.append("RSI超买，注意回调")

        if bollinger == "below_lower":
            details.append("跌破布林带下轨，超卖")
        elif bollinger == "above_upper":
            details.append("突破布林带上轨，超买")

        return details

    def _get_capital_details(self, capital: Dict) -> List[str]:
        """获取资金面详情"""
        details = []
        main_flow = capital.get("main_flow", {})
        north_flow = capital.get("north_flow", {})

        if isinstance(main_flow, dict):
            main_desc = main_flow.get("description", "")
            if main_desc:
                details.append(f"主力资金: {main_desc}")

        if isinstance(north_flow, dict):
            north_desc = north_flow.get("description", "")
            if north_desc:
                details.append(f"北向资金: {north_desc}")

        return details

    def _get_sentiment_details(self, sentiment: Dict) -> List[str]:
        """获取情绪面详情"""
        details = []
        fear_greed = sentiment.get("fear_greed_index", 50)
        advice = sentiment.get("advice", "")

        if fear_greed >= 80:
            details.append("市场极度贪婪，注意风险")
        elif fear_greed >= 60:
            details.append("市场偏贪婪")
        elif fear_greed <= 20:
            details.append("市场极度恐慌，可能是机会")
        elif fear_greed <= 40:
            details.append("市场偏恐慌")

        if advice:
            details.append(f"建议: {advice}")

        return details

    def _get_news_details(self, news: Dict) -> List[str]:
        """获取新闻面详情"""
        details = []
        sentiment = news.get("sentiment", "")
        policy = news.get("policy_impact", "")

        if sentiment and sentiment != "neutral":
            details.append(f"新闻情绪: {sentiment}")

        if policy and policy != "neutral":
            details.append(f"政策影响: {policy}")

        return details

    def _calculate_total_score(self, dimensions: Dict) -> float:
        """计算综合得分"""
        total = 0
        for dim, data in dimensions.items():
            total += data["score"] * data["weight"]
        return max(-1, min(1, total))

    def _generate_recommendation(self, total_score: float, dimensions: Dict, analysis: Dict) -> Dict[str, Any]:
        """生成详细建议"""
        # 统计各维度信号
        bullish_count = sum(1 for d in dimensions.values() if d["score"] > 0.2)
        bearish_count = sum(1 for d in dimensions.values() if d["score"] < -0.2)
        neutral_count = len(dimensions) - bullish_count - bearish_count

        # 收集触发条件
        conditions = []
        bullish_reasons = []
        bearish_reasons = []

        for dim, data in dimensions.items():
            if data["score"] > 0.3:
                conditions.append(f"{dim}看涨")
                bullish_reasons.append(dim)
            elif data["score"] < -0.3:
                conditions.append(f"{dim}看跌")
                bearish_reasons.append(dim)

        # 生成判断依据
        if bullish_reasons:
            reason_bull = f"看涨因素: {', '.join(bullish_reasons)}"
        else:
            reason_bull = ""

        if bearish_reasons:
            reason_bear = f"看跌因素: {', '.join(bearish_reasons)}"
        else:
            reason_bear = ""

        # 组合判断依据
        if reason_bull and reason_bear:
            reason = f"{reason_bull}; {reason_bear}"
        elif reason_bull:
            reason = reason_bull
        elif reason_bear:
            reason = reason_bear
        else:
            reason = "各维度信号中性，无明显方向"

        # 生成信号
        if total_score >= 0.5 and bullish_count >= 4:
            return {
                "category": "buy",
                "type": "strong_buy",
                "description": "强烈买入",
                "confidence": min(total_score, 1.0),
                "reason": f"多维度共振看涨，{bullish_count}/{len(dimensions)}个维度看涨。{reason}",
                "conditions": conditions
            }
        elif total_score >= 0.3 and bullish_count >= 3:
            return {
                "category": "buy",
                "type": "buy",
                "description": "建议买入",
                "confidence": total_score * 0.9,
                "reason": f"多数维度看涨，{bullish_count}/{len(dimensions)}个维度看涨。{reason}",
                "conditions": conditions
            }
        elif total_score >= 0.1:
            return {
                "category": "hold",
                "type": "weak_buy",
                "description": "可考虑少量买入",
                "confidence": total_score * 0.7,
                "reason": f"偏多但信号不够强。{reason}",
                "conditions": conditions
            }
        elif total_score <= -0.5 and bearish_count >= 4:
            return {
                "category": "sell",
                "type": "strong_sell",
                "description": "强烈卖出",
                "confidence": min(abs(total_score), 1.0),
                "reason": f"多维度共振看跌，{bearish_count}/{len(dimensions)}个维度看跌。{reason}",
                "conditions": conditions
            }
        elif total_score <= -0.3 and bearish_count >= 3:
            return {
                "category": "sell",
                "type": "sell",
                "description": "建议卖出",
                "confidence": abs(total_score) * 0.9,
                "reason": f"多数维度看跌，{bearish_count}/{len(dimensions)}个维度看跌。{reason}",
                "conditions": conditions
            }
        elif total_score <= -0.1:
            return {
                "category": "hold",
                "type": "weak_sell",
                "description": "可考虑减仓",
                "confidence": abs(total_score) * 0.7,
                "reason": f"偏空但信号不够强。{reason}",
                "conditions": conditions
            }
        else:
            return {
                "category": "hold",
                "type": "hold",
                "description": "建议持有观望",
                "confidence": 1 - abs(total_score),
                "reason": f"多空力量均衡，各维度信号中性。{reason}",
                "conditions": conditions
            }

    def _generate_risk_warnings(self, analysis: Dict, dimensions: Dict) -> List[str]:
        """生成风险提示"""
        warnings = []

        # 技术面风险
        technical = dimensions.get("technical", {})
        if technical["score"] < -0.5:
            warnings.append("技术面发出强烈看跌信号")

        # 资金面风险
        capital = dimensions.get("capital", {})
        if capital["score"] < -0.5:
            warnings.append("主力资金大幅流出")

        # 情绪面风险
        sentiment = analysis.get("sentiment", {})
        fear_greed = sentiment.get("fear_greed_index", 50)
        if fear_greed > 80:
            warnings.append("市场情绪极度贪婪，注意追高风险")
        elif fear_greed < 20:
            warnings.append("市场情绪极度恐慌，可能存在非理性下跌")

        # 波动率风险
        volatility = analysis.get("volatility", 0)
        if volatility > 25:
            warnings.append(f"年化波动率较高({volatility:.1f}%)，风险较大")

        # 回撤风险
        max_drawdown = analysis.get("max_drawdown", 0)
        if max_drawdown > 15:
            warnings.append(f"最大回撤较大({max_drawdown:.1f}%)，注意控制仓位")

        return warnings

    def _generate_action_plan(self, total_score: float, dimensions: Dict, analysis: Dict) -> Dict[str, Any]:
        """生成操作计划"""
        # 建议仓位
        if total_score >= 0.5:
            position = "60-80%"
            action = "逐步加仓"
        elif total_score >= 0.3:
            position = "40-60%"
            action = "适量建仓"
        elif total_score >= 0.1:
            position = "20-40%"
            action = "少量试探"
        elif total_score <= -0.5:
            position = "0-10%"
            action = "清仓或极低仓位"
        elif total_score <= -0.3:
            position = "10-20%"
            action = "大幅减仓"
        elif total_score <= -0.1:
            position = "20-30%"
            action = "适当减仓"
        else:
            position = "30-50%"
            action = "维持现有仓位"

        # 止损止盈建议
        stop_loss = "建议设置5-8%止损"
        take_profit = "建议设置10-15%止盈"

        return {
            "suggested_position": position,
            "action": action,
            "stop_loss": stop_loss,
            "take_profit": take_profit
        }


# 全局信号生成实例
signal_generator = SignalGenerator()
