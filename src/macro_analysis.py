"""
宏观经济分析模块
分析利率、CPI、PMI 等宏观经济指标对基金的影响
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class MacroAnalyzer:
    """宏观经济分析类"""

    def __init__(self):
        # 宏观指标权重
        self.weights = {
            "interest_rate": 0.25,   # 利率
            "cpi": 0.25,             # CPI
            "pmi": 0.25,             # PMI
            "monetary_policy": 0.25  # 货币政策
        }

    def analyze_interest_rate(self, rate_data: Dict = None) -> Dict[str, Any]:
        """
        分析利率环境

        Args:
            rate_data: 利率数据 (可选)

        Returns:
            dict: 利率分析
        """
        # 模拟当前利率环境分析
        # 实际应接入央行利率数据
        current_rate = 3.45  # 当前LPR
        rate_trend = "stable"  # stable, rising, falling

        # 判断利率对基金的影响
        impact = "neutral"
        description = ""
        score = 50

        if rate_data:
            # 如果有实际数据，进行分析
            current_rate = rate_data.get("current_rate", current_rate)
            rate_trend = rate_data.get("trend", rate_trend)

        if rate_trend == "falling":
            impact = "positive"
            description = "降息周期，利好成长型基金"
            score = 70
        elif rate_trend == "rising":
            impact = "negative"
            description = "加息周期，利空高估值基金"
            score = 30
        else:
            impact = "neutral"
            description = "利率稳定，中性影响"
            score = 50

        return {
            "current_rate": current_rate,
            "trend": rate_trend,
            "impact": impact,
            "description": description,
            "score": score
        }

    def analyze_cpi(self, cpi_data: Dict = None) -> Dict[str, Any]:
        """
        分析CPI (消费者物价指数)

        Args:
            cpi_data: CPI数据 (可选)

        Returns:
            dict: CPI分析
        """
        # 模拟当前CPI分析
        current_cpi = 0.3  # 当前CPI环比
        yoy_cpi = 2.1  # 同比CPI
        trend = "stable"  # stable, rising, falling

        if cpi_data:
            current_cpi = cpi_data.get("current", current_cpi)
            yoy_cpi = cpi_data.get("yoy", yoy_cpi)
            trend = cpi_data.get("trend", trend)

        # 判断CPI对基金的影响
        impact = "neutral"
        description = ""
        score = 50

        if yoy_cpi > 3:
            impact = "negative"
            description = f"CPI偏高({yoy_cpi}%)，通胀压力大，不利"
            score = 30
        elif yoy_cpi > 2.5:
            impact = "slightly_negative"
            description = f"CPI略高({yoy_cpi}%)，温和通胀"
            score = 40
        elif yoy_cpi < 1:
            impact = "negative"
            description = f"CPI过低({yoy_cpi}%)，通缩风险"
            score = 35
        elif 1 <= yoy_cpi <= 2:
            impact = "positive"
            description = f"CPI适中({yoy_cpi}%)，健康通胀"
            score = 65
        else:
            description = f"CPI正常({yoy_cpi}%)"

        return {
            "current": current_cpi,
            "yoy": yoy_cpi,
            "trend": trend,
            "impact": impact,
            "description": description,
            "score": score
        }

    def analyze_pmi(self, pmi_data: Dict = None) -> Dict[str, Any]:
        """
        分析PMI (采购经理指数)

        Args:
            pmi_data: PMI数据 (可选)

        Returns:
            dict: PMI分析
        """
        # 模拟当前PMI分析
        manufacturing_pmi = 50.5  # 制造业PMI
        non_manufacturing_pmi = 53.2  # 非制造业PMI
        trend = "stable"

        if pmi_data:
            manufacturing_pmi = pmi_data.get("manufacturing", manufacturing_pmi)
            non_manufacturing_pmi = pmi_data.get("non_manufacturing", non_manufacturing_pmi)
            trend = pmi_data.get("trend", trend)

        # 判断PMI对基金的影响
        impact = "neutral"
        description = ""
        score = 50

        if manufacturing_pmi > 52:
            impact = "positive"
            description = f"制造业PMI={manufacturing_pmi}，经济扩张强劲"
            score = 75
        elif manufacturing_pmi > 50:
            impact = "slightly_positive"
            description = f"制造业PMI={manufacturing_pmi}，经济温和扩张"
            score = 60
        elif manufacturing_pmi > 49:
            impact = "neutral"
            description = f"制造业PMI={manufacturing_pmi}，经济平稳"
            score = 50
        elif manufacturing_pmi > 48:
            impact = "slightly_negative"
            description = f"制造业PMI={manufacturing_pmi}，经济轻微收缩"
            score = 40
        else:
            impact = "negative"
            description = f"制造业PMI={manufacturing_pmi}，经济收缩明显"
            score = 25

        return {
            "manufacturing": manufacturing_pmi,
            "non_manufacturing": non_manufacturing_pmi,
            "trend": trend,
            "impact": impact,
            "description": description,
            "score": score
        }

    def analyze_monetary_policy(self, policy_data: Dict = None) -> Dict[str, Any]:
        """
        分析货币政策

        Args:
            policy_data: 政策数据 (可选)

        Returns:
            dict: 货币政策分析
        """
        # 模拟当前货币政策分析
        policy_stance = "neutral"  # loose, neutral, tight
        reserve_ratio = 10.5  # 存款准备金率
        m2_growth = 10.2  # M2增速

        if policy_data:
            policy_stance = policy_data.get("stance", policy_stance)
            reserve_ratio = policy_data.get("reserve_ratio", reserve_ratio)
            m2_growth = policy_data.get("m2_growth", m2_growth)

        # 判断货币政策对基金的影响
        impact = "neutral"
        description = ""
        score = 50

        if policy_stance == "loose":
            impact = "positive"
            description = "宽松货币政策，利好权益类基金"
            score = 70
        elif policy_stance == "tight":
            impact = "negative"
            description = "紧缩货币政策，利空权益类基金"
            score = 30
        else:
            description = "货币政策中性"

        # M2增速分析
        if m2_growth > 12:
            description += f"，M2增速较高({m2_growth}%)，流动性充裕"
        elif m2_growth < 8:
            description += f"，M2增速偏低({m2_growth}%)，流动性偏紧"

        return {
            "stance": policy_stance,
            "reserve_ratio": reserve_ratio,
            "m2_growth": m2_growth,
            "impact": impact,
            "description": description,
            "score": score
        }

    def analyze_macro_environment(self, macro_data: Dict = None) -> Dict[str, Any]:
        """
        综合分析宏观环境

        Args:
            macro_data: 宏观数据 (可选)

        Returns:
            dict: 宏观环境综合分析
        """
        # 分析各维度
        interest_rate = self.analyze_interest_rate(macro_data.get("interest_rate") if macro_data else None)
        cpi = self.analyze_cpi(macro_data.get("cpi") if macro_data else None)
        pmi = self.analyze_pmi(macro_data.get("pmi") if macro_data else None)
        monetary_policy = self.analyze_monetary_policy(macro_data.get("monetary_policy") if macro_data else None)

        # 计算综合得分
        total_score = (
            interest_rate["score"] * self.weights["interest_rate"] +
            cpi["score"] * self.weights["cpi"] +
            pmi["score"] * self.weights["pmi"] +
            monetary_policy["score"] * self.weights["monetary_policy"]
        )

        # 判断宏观环境
        if total_score >= 70:
            environment = "favorable"
            description = "宏观环境有利，适合投资"
            advice = "可适当增加权益类配置"
        elif total_score >= 55:
            environment = "neutral_positive"
            description = "宏观环境中性偏正面"
            advice = "维持现有配置"
        elif total_score >= 45:
            environment = "neutral"
            description = "宏观环境中性"
            advice = "谨慎操作，关注变化"
        elif total_score >= 30:
            environment = "neutral_negative"
            description = "宏观环境中性偏负面"
            advice = "减少风险暴露"
        else:
            environment = "unfavorable"
            description = "宏观环境不利，需谨慎"
            advice = "建议降低仓位，防御为主"

        # 生成各指标的中文描述
        indicators = {
            "利率": interest_rate,
            "CPI": cpi,
            "PMI": pmi,
            "货币政策": monetary_policy
        }

        return {
            "has_data": True,
            "environment": environment,
            "total_score": round(total_score, 1),
            "description": description,
            "advice": advice,
            "indicators": indicators,
            "interest_rate": interest_rate,
            "cpi": cpi,
            "pmi": pmi,
            "monetary_policy": monetary_policy
        }


# 全局宏观经济分析实例
macro_analyzer = MacroAnalyzer()
