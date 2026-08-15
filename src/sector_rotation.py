"""
行业轮动分析模块
分析行业热度和轮动趋势
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class SectorRotationAnalyzer:
    """行业轮动分析类"""

    def __init__(self):
        # 主要行业板块
        self.sectors = {
            "消费": ["食品饮料", "家用电器", "纺织服饰", "商贸零售", "社会服务", "美容护理"],
            "科技": ["电子", "计算机", "通信", "传媒"],
            "医药": ["医药生物"],
            "金融": ["银行", "非银金融", "房地产"],
            "制造": ["机械设备", "汽车", "电力设备", "国防军工"],
            "周期": ["有色金属", "钢铁", "煤炭", "基础化工", "建筑材料"],
            "基建": ["建筑装饰", "公用事业", "交通运输"]
        }

        # 行业估值区间
        self.valuation_ranges = {
            "low": (0, 30),      # 低估
            "medium": (30, 70),   # 适中
            "high": (70, 100)     # 高估
        }

    def analyze_sector_momentum(self, sector_data: Dict = None) -> Dict[str, Any]:
        """
        分析行业动量

        Args:
            sector_data: 行业数据 (可选)

        Returns:
            dict: 行业动量分析
        """
        # 模拟行业数据
        # 实际应接入东方财富或同花顺行业数据
        sectors_performance = {
            "消费": {"return_5d": 1.2, "return_20d": 3.5, "momentum": "strong"},
            "科技": {"return_5d": 2.1, "return_20d": 5.2, "momentum": "strong"},
            "医药": {"return_5d": -0.5, "return_20d": 1.2, "momentum": "weak"},
            "金融": {"return_5d": 0.3, "return_20d": -1.5, "momentum": "neutral"},
            "制造": {"return_5d": 1.8, "return_20d": 4.1, "momentum": "strong"},
            "周期": {"return_5d": -1.2, "return_20d": -3.2, "momentum": "weak"},
            "基建": {"return_5d": 0.5, "return_20d": 2.1, "momentum": "neutral"}
        }

        if sector_data:
            sectors_performance = sector_data

        # 计算动量排名
        momentum_ranking = sorted(
            sectors_performance.items(),
            key=lambda x: x[1].get("return_20d", 0),
            reverse=True
        )

        # 热门行业
        hot_sectors = [s[0] for s in momentum_ranking[:3]]
        # 冷门行业
        cold_sectors = [s[0] for s in momentum_ranking[-3:]]

        return {
            "sectors": sectors_performance,
            "ranking": momentum_ranking,
            "hot_sectors": hot_sectors,
            "cold_sectors": cold_sectors,
            "description": f"热门行业: {', '.join(hot_sectors)}"
        }

    def analyze_sector_valuation(self, valuation_data: Dict = None) -> Dict[str, Any]:
        """
        分析行业估值

        Args:
            valuation_data: 估值数据 (可选)

        Returns:
            dict: 行业估值分析
        """
        # 模拟行业估值数据
        sector_valuations = {
            "消费": {"pe_percentile": 65, "pb_percentile": 55, "status": "medium"},
            "科技": {"pe_percentile": 80, "pb_percentile": 75, "status": "high"},
            "医药": {"pe_percentile": 45, "pb_percentile": 40, "status": "medium"},
            "金融": {"pe_percentile": 25, "pb_percentile": 20, "status": "low"},
            "制造": {"pe_percentile": 55, "pb_percentile": 50, "status": "medium"},
            "周期": {"pe_percentile": 35, "pb_percentile": 30, "status": "low"},
            "基建": {"pe_percentile": 40, "pb_percentile": 35, "status": "medium"}
        }

        if valuation_data:
            sector_valuations = valuation_data

        # 分类
        undervalued = []
        overvalued = []
        fair_valued = []

        for sector, val in sector_valuations.items():
            pe = val.get("pe_percentile", 50)
            if pe < 30:
                undervalued.append(sector)
                val["status"] = "low"
            elif pe > 70:
                overvalued.append(sector)
                val["status"] = "high"
            else:
                fair_valued.append(sector)
                val["status"] = "medium"

        return {
            "valuations": sector_valuations,
            "undervalued": undervalued,
            "overvalued": overvalued,
            "fair_valued": fair_valued,
            "description": f"低估行业: {', '.join(undervalued) if undervalued else '无'}"
        }

    def analyze_sector_correlation(self, fund_sectors: List[str] = None) -> Dict[str, Any]:
        """
        分析基金持仓行业与市场热点的相关性

        Args:
            fund_sectors: 基金持仓的行业列表

        Returns:
            dict: 行业相关性分析
        """
        if not fund_sectors:
            fund_sectors = ["消费", "科技"]  # 默认

        # 获取热门行业
        momentum = self.analyze_sector_momentum()
        hot_sectors = momentum.get("hot_sectors", [])

        # 计算相关性
        overlap = set(fund_sectors) & set(hot_sectors)
        correlation_score = len(overlap) / len(hot_sectors) if hot_sectors else 0

        if correlation_score > 0.6:
            correlation_level = "high"
            description = "基金持仓与市场热点高度契合"
        elif correlation_score > 0.3:
            correlation_level = "medium"
            description = "基金持仓与市场热点有一定契合"
        else:
            correlation_level = "low"
            description = "基金持仓与市场热点契合度较低"

        return {
            "fund_sectors": fund_sectors,
            "hot_sectors": hot_sectors,
            "overlap": list(overlap),
            "correlation_score": round(correlation_score, 2),
            "correlation_level": correlation_level,
            "description": description
        }

    def generate_rotation_signal(self, fund_code: str = None, fund_sectors: List[str] = None) -> Dict[str, Any]:
        """
        生成行业轮动信号

        Args:
            fund_code: 基金代码
            fund_sectors: 基金持仓行业

        Returns:
            dict: 行业轮动信号
        """
        # 分析行业动量
        momentum = self.analyze_sector_momentum()

        # 分析行业估值
        valuation = self.analyze_sector_valuation()

        # 分析相关性
        correlation = self.analyze_sector_correlation(fund_sectors)

        # 综合评分
        score = 50

        # 动量加分
        hot_count = len(momentum.get("hot_sectors", []))
        score += hot_count * 5

        # 估值加分
        undervalued_count = len(valuation.get("undervalued", []))
        score += undervalued_count * 3

        # 相关性加分
        correlation_score = correlation.get("correlation_score", 0)
        score += correlation_score * 20

        # 限制分数范围
        score = max(0, min(100, score))

        # 生成信号
        if score >= 70:
            signal = "favorable"
            description = "行业轮动有利，当前持仓行业表现强劲"
            advice = "可继续持有或加仓"
        elif score >= 55:
            signal = "neutral_positive"
            description = "行业轮动中性偏正面"
            advice = "维持现有配置"
        elif score >= 45:
            signal = "neutral"
            description = "行业轮动中性"
            advice = "关注行业变化，适时调整"
        else:
            signal = "unfavorable"
            description = "行业轮动不利，当前持仓行业表现疲软"
            advice = "考虑调整行业配置"

        return {
            "has_data": True,
            "signal": signal,
            "score": score,
            "description": description,
            "advice": advice,
            "momentum": momentum,
            "valuation": valuation,
            "correlation": correlation
        }


# 全局行业轮动分析实例
sector_rotation_analyzer = SectorRotationAnalyzer()
