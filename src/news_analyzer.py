"""
新闻分析模块
分析财经新闻和政策信息的情绪影响
"""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class NewsAnalyzer:
    """新闻分析类"""

    def __init__(self):
        # 正面关键词
        self.positive_keywords = [
            "利好", "上涨", "增长", "突破", "创新高", "反弹", "回升", "强势",
            "看好", "推荐", "买入", "增持", "超预期", "业绩好", "利润增长",
            "政策支持", "扶持", "补贴", "减税", "降息", "降准", "宽松",
            "牛市", "上涨趋势", "资金流入", "北向资金买入", "机构加仓"
        ]

        # 负面关键词
        self.negative_keywords = [
            "利空", "下跌", "下滑", "破位", "创新低", "回调", "回落", "弱势",
            "看空", "减持", "卖出", "回避", "低于预期", "业绩差", "利润下降",
            "政策收紧", "监管", "限制", "加税", "加息", "提准", "紧缩",
            "熊市", "下跌趋势", "资金流出", "北向资金卖出", "机构减仓"
        ]

        # 政策关键词
        self.policy_keywords = {
            "monetary": ["央行", "货币政策", "利率", "存款准备金", "公开市场操作"],
            "fiscal": ["财政政策", "税收", "政府支出", "基建投资"],
            "industry": ["产业政策", "行业监管", "补贴政策", "准入门槛"],
            "regulation": ["监管政策", "合规要求", "风险控制", "整顿"]
        }

    def analyze_sentiment(self, news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析新闻整体情绪

        Args:
            news: 新闻列表

        Returns:
            dict: 情绪分析结果
        """
        if not news:
            return {
                "sentiment_score": 0,
                "sentiment_label": "neutral",
                "description": "无新闻数据",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0
            }

        positive_count = 0
        negative_count = 0
        neutral_count = 0

        for article in news:
            text = article.get("title", "") + " " + article.get("content", "")
            sentiment = self._analyze_single_text(text)

            if sentiment > 0.1:
                positive_count += 1
            elif sentiment < -0.1:
                negative_count += 1
            else:
                neutral_count += 1

        total = len(news)
        sentiment_score = (positive_count - negative_count) / total if total > 0 else 0

        # 判断情绪标签
        if sentiment_score > 0.3:
            sentiment_label = "very_positive"
            description = "新闻情绪非常积极"
        elif sentiment_score > 0.1:
            sentiment_label = "positive"
            description = "新闻情绪偏积极"
        elif sentiment_score < -0.3:
            sentiment_label = "very_negative"
            description = "新闻情绪非常消极"
        elif sentiment_score < -0.1:
            sentiment_label = "negative"
            description = "新闻情绪偏消极"
        else:
            sentiment_label = "neutral"
            description = "新闻情绪中性"

        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "description": description,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "total_count": total
        }

    def _analyze_single_text(self, text: str) -> float:
        """
        分析单条文本的情绪

        Args:
            text: 文本内容

        Returns:
            float: 情绪分数 (-1 到 1)
        """
        if not text:
            return 0

        positive_count = 0
        negative_count = 0

        for keyword in self.positive_keywords:
            if keyword in text:
                positive_count += 1

        for keyword in self.negative_keywords:
            if keyword in text:
                negative_count += 1

        total = positive_count + negative_count
        if total == 0:
            return 0

        return (positive_count - negative_count) / total

    def extract_keywords(self, news: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
        """
        提取新闻关键词

        Args:
            news: 新闻列表
            top_n: 返回前N个关键词

        Returns:
            list: 关键词列表
        """
        # 合并所有文本
        all_text = ""
        for article in news:
            all_text += article.get("title", "") + " " + article.get("content", "") + " "

        # 简单的关键词提取（实际可以使用jieba等分词工具）
        word_count = {}

        # 检查正面关键词
        for keyword in self.positive_keywords:
            if keyword in all_text:
                word_count[keyword] = word_count.get(keyword, 0) + all_text.count(keyword)

        # 检查负面关键词
        for keyword in self.negative_keywords:
            if keyword in all_text:
                word_count[keyword] = word_count.get(keyword, 0) + all_text.count(keyword)

        # 按频率排序
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

        return [{"keyword": word, "count": count} for word, count in sorted_words[:top_n]]

    def analyze_policy_impact(self, news: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析政策影响

        Args:
            news: 新闻列表

        Returns:
            dict: 政策影响分析
        """
        policy_mentions = {
            "monetary": 0,
            "fiscal": 0,
            "industry": 0,
            "regulation": 0
        }

        for article in news:
            text = article.get("title", "") + " " + article.get("content", "")

            for policy_type, keywords in self.policy_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        policy_mentions[policy_type] += 1

        # 分析政策影响
        impact_analysis = {}

        # 货币政策
        if policy_mentions["monetary"] > 0:
            # 检查是宽松还是紧缩
            text = " ".join([a.get("title", "") + a.get("content", "") for a in news])
            if any(kw in text for kw in ["降息", "降准", "宽松", "流动性"]):
                impact_analysis["monetary"] = {
                    "direction": "easing",
                    "impact": "positive",
                    "description": "货币政策宽松，利好市场"
                }
            elif any(kw in text for kw in ["加息", "提准", "紧缩", "收紧"]):
                impact_analysis["monetary"] = {
                    "direction": "tightening",
                    "impact": "negative",
                    "description": "货币政策收紧，利空市场"
                }
            else:
                impact_analysis["monetary"] = {
                    "direction": "neutral",
                    "impact": "neutral",
                    "description": "货币政策中性"
                }

        # 财政政策
        if policy_mentions["fiscal"] > 0:
            text = " ".join([a.get("title", "") + a.get("content", "") for a in news])
            if any(kw in text for kw in ["减税", "降费", "基建投资", "政府支出"]):
                impact_analysis["fiscal"] = {
                    "direction": "expansionary",
                    "impact": "positive",
                    "description": "财政政策积极，利好经济"
                }
            else:
                impact_analysis["fiscal"] = {
                    "direction": "neutral",
                    "impact": "neutral",
                    "description": "财政政策中性"
                }

        # 行业政策
        if policy_mentions["industry"] > 0:
            text = " ".join([a.get("title", "") + a.get("content", "") for a in news])
            if any(kw in text for kw in ["扶持", "补贴", "支持", "鼓励"]):
                impact_analysis["industry"] = {
                    "direction": "supportive",
                    "impact": "positive",
                    "description": "行业政策支持，利好相关行业"
                }
            elif any(kw in text for kw in ["限制", "整顿", "规范", "收紧"]):
                impact_analysis["industry"] = {
                    "direction": "restrictive",
                    "impact": "negative",
                    "description": "行业政策收紧，利空相关行业"
                }
            else:
                impact_analysis["industry"] = {
                    "direction": "neutral",
                    "impact": "neutral",
                    "description": "行业政策中性"
                }

        # 监管政策
        if policy_mentions["regulation"] > 0:
            text = " ".join([a.get("title", "") + a.get("content", "") for a in news])
            if any(kw in text for kw in ["加强监管", "风险控制", "合规要求"]):
                impact_analysis["regulation"] = {
                    "direction": "strict",
                    "impact": "mixed",
                    "description": "监管加强，短期可能利空，长期利好市场规范"
                }
            else:
                impact_analysis["regulation"] = {
                    "direction": "neutral",
                    "impact": "neutral",
                    "description": "监管政策中性"
                }

        # 计算总体影响
        positive_impacts = sum(1 for v in impact_analysis.values() if v.get("impact") == "positive")
        negative_impacts = sum(1 for v in impact_analysis.values() if v.get("impact") == "negative")

        if positive_impacts > negative_impacts:
            overall_impact = "positive"
            overall_description = "政策面整体利好"
        elif negative_impacts > positive_impacts:
            overall_impact = "negative"
            overall_description = "政策面整体利空"
        else:
            overall_impact = "neutral"
            overall_description = "政策面整体中性"

        return {
            "policy_mentions": policy_mentions,
            "impact_analysis": impact_analysis,
            "overall_impact": overall_impact,
            "overall_description": overall_description
        }

    def generate_news_signal(self, news_sentiment: Dict, policy_impact: Dict) -> Dict[str, Any]:
        """
        生成新闻信号

        Args:
            news_sentiment: 新闻情绪分析
            policy_impact: 政策影响分析

        Returns:
            dict: 综合信号
        """
        # 计算情绪分数
        sentiment_score = news_sentiment.get("sentiment_score", 0)

        # 计算政策影响分数
        policy_score = 0
        if policy_impact.get("overall_impact") == "positive":
            policy_score = 0.5
        elif policy_impact.get("overall_impact") == "negative":
            policy_score = -0.5

        # 综合分数
        total_score = sentiment_score * 0.6 + policy_score * 0.4

        # 判断信号
        if total_score > 0.3:
            overall_signal = "strong_bullish"
            description = "新闻面强烈看涨"
        elif total_score > 0.1:
            overall_signal = "bullish"
            description = "新闻面看涨"
        elif total_score < -0.3:
            overall_signal = "strong_bearish"
            description = "新闻面强烈看跌"
        elif total_score < -0.1:
            overall_signal = "bearish"
            description = "新闻面看跌"
        else:
            overall_signal = "neutral"
            description = "新闻面中性"

        return {
            "overall_signal": overall_signal,
            "total_score": total_score,
            "description": description,
            "news_sentiment": news_sentiment,
            "policy_impact": policy_impact
        }


# 全局新闻分析实例
news_analyzer = NewsAnalyzer()
