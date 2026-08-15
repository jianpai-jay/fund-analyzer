"""
基金持仓分析模块
分析基金持仓股票和行业分布
"""
import pandas as pd
from typing import Dict, Any, List, Optional


class FundHoldingsAnalyzer:
    """基金持仓分析类"""

    def __init__(self):
        # 行业分类映射
        self.industry_map = {
            "60": "金融",
            "00": "工业",
            "30": "信息技术",
            "68": "信息技术",
            "002": "可选消费",
            "600": "主要消费",
            "601": "金融",
            "603": "工业",
            "605": "主要消费",
            "688": "信息技术"
        }

    def analyze_holdings(self, holdings: List[Dict[str, Any]], fund_code: str) -> Dict[str, Any]:
        """
        分析基金持仓

        Args:
            holdings: 持仓数据列表
            fund_code: 基金代码

        Returns:
            dict: 持仓分析结果
        """
        if not holdings:
            return {
                "fund_code": fund_code,
                "total_holdings": 0,
                "analysis": "无持仓数据"
            }

        # 计算持仓集中度
        concentration = self._calculate_concentration(holdings)

        # 分析行业分布
        industry_dist = self._analyze_industry_distribution(holdings)

        # 计算前十大持仓占比
        top10_ratio = self._calculate_top10_ratio(holdings)

        # 生成持仓信号
        signal = self._generate_holdings_signal(concentration, industry_dist, top10_ratio)

        return {
            "fund_code": fund_code,
            "total_holdings": len(holdings),
            "concentration": concentration,
            "industry_distribution": industry_dist,
            "top10_ratio": top10_ratio,
            "signal": signal,
            "top_holdings": holdings[:10]
        }

    def _calculate_concentration(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算持仓集中度

        Args:
            holdings: 持仓数据列表

        Returns:
            dict: 集中度分析
        """
        if not holdings:
            return {"score": 0, "level": "unknown", "description": "无数据"}

        # 计算前5大持仓占比
        sorted_holdings = sorted(holdings, key=lambda x: x.get("percentage", 0), reverse=True)
        top5_sum = sum(h.get("percentage", 0) for h in sorted_holdings[:5])
        top10_sum = sum(h.get("percentage", 0) for h in sorted_holdings[:10])

        # 判断集中度水平
        if top5_sum > 60:
            level = "very_high"
            description = "持仓高度集中，风险较高"
            score = -0.5
        elif top5_sum > 40:
            level = "high"
            description = "持仓较集中"
            score = -0.2
        elif top5_sum > 20:
            level = "moderate"
            description = "持仓适中"
            score = 0.2
        else:
            level = "low"
            description = "持仓分散，风险较低"
            score = 0.5

        return {
            "top5_ratio": top5_sum,
            "top10_ratio": top10_sum,
            "level": level,
            "score": score,
            "description": description
        }

    def _analyze_industry_distribution(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析行业分布

        Args:
            holdings: 持仓数据列表

        Returns:
            dict: 行业分布分析
        """
        if not holdings:
            return {"distribution": {}, "diversification_score": 0}

        # 统计行业分布
        industry_count = {}
        industry_value = {}

        for holding in holdings:
            stock_code = holding.get("stock_code", "")
            percentage = holding.get("percentage", 0)

            # 根据股票代码判断行业
            industry = self._get_industry_by_code(stock_code)

            industry_count[industry] = industry_count.get(industry, 0) + 1
            industry_value[industry] = industry_value.get(industry, 0) + percentage

        # 计算行业数量
        industry_count_len = len(industry_count)

        # 计算分散度得分
        if industry_count_len >= 5:
            diversification_score = 0.8
        elif industry_count_len >= 3:
            diversification_score = 0.5
        else:
            diversification_score = 0.2

        # 找出最大行业占比
        max_industry = max(industry_value.items(), key=lambda x: x[1]) if industry_value else ("未知", 0)
        max_ratio = max_industry[1]

        return {
            "distribution": industry_value,
            "count": industry_count,
            "industry_count": industry_count_len,
            "max_industry": max_industry[0],
            "max_ratio": max_ratio,
            "diversification_score": diversification_score
        }

    def _get_industry_by_code(self, stock_code: str) -> str:
        """
        根据股票代码判断行业

        Args:
            stock_code: 股票代码

        Returns:
            str: 行业名称
        """
        if not stock_code:
            return "未知"

        # 简单的行业判断逻辑
        prefix = stock_code[:2]
        return self.industry_map.get(prefix, "其他")

    def _calculate_top10_ratio(self, holdings: List[Dict[str, Any]]) -> float:
        """
        计算前十大持仓占比

        Args:
            holdings: 持仓数据列表

        Returns:
            float: 前十大持仓占比
        """
        if not holdings:
            return 0

        sorted_holdings = sorted(holdings, key=lambda x: x.get("percentage", 0), reverse=True)
        return sum(h.get("percentage", 0) for h in sorted_holdings[:10])

    def _generate_holdings_signal(self, concentration: Dict, industry_dist: Dict, top10_ratio: float) -> Dict[str, Any]:
        """
        生成持仓信号

        Args:
            concentration: 集中度分析
            industry_dist: 行业分布分析
            top10_ratio: 前十大持仓占比

        Returns:
            dict: 持仓信号
        """
        signals = []

        # 集中度信号
        if concentration.get("level") == "very_high":
            signals.append({"type": "risk", "description": "持仓高度集中，风险较高"})
        elif concentration.get("level") == "low":
            signals.append({"type": "opportunity", "description": "持仓分散，风险较低"})

        # 行业分散度信号
        if industry_dist.get("diversification_score", 0) >= 0.8:
            signals.append({"type": "positive", "description": "行业配置分散"})
        elif industry_dist.get("diversification_score", 0) <= 0.2:
            signals.append({"type": "warning", "description": "行业配置集中"})

        # 前十大持仓信号
        if top10_ratio > 70:
            signals.append({"type": "risk", "description": f"前十大持仓占比{top10_ratio:.1f}%，集中度高"})
        elif top10_ratio < 40:
            signals.append({"type": "positive", "description": f"前十大持仓占比{top10_ratio:.1f}%，分散度好"})

        # 综合信号
        risk_count = sum(1 for s in signals if s["type"] == "risk")
        positive_count = sum(1 for s in signals if s["type"] in ["positive", "opportunity"])

        if risk_count > positive_count:
            overall = "cautious"
            description = "持仓结构需谨慎"
        elif positive_count > risk_count:
            overall = "positive"
            description = "持仓结构良好"
        else:
            overall = "neutral"
            description = "持仓结构一般"

        return {
            "overall": overall,
            "description": description,
            "signals": signals
        }


# 全局持仓分析实例
fund_holdings_analyzer = FundHoldingsAnalyzer()
