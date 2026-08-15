"""
基金经理分析模块
分析基金经理的业绩和风格
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class FundManagerAnalyzer:
    """基金经理分析类"""

    def __init__(self):
        # 基金经理风格分类
        self.style_keywords = {
            "value": ["价值", "低估值", "高股息", "蓝筹", "稳健"],
            "growth": ["成长", "高增长", "创新", "科技", "新兴"],
            "blend": ["均衡", "混合", "灵活", "配置"],
            "index": ["指数", "被动", "跟踪", "ETF"]
        }

    def analyze_manager(self, manager_info: Dict[str, Any], fund_code: str) -> Dict[str, Any]:
        """
        分析基金经理

        Args:
            manager_info: 基金经理信息
            fund_code: 基金代码

        Returns:
            dict: 基金经理分析结果
        """
        if not manager_info:
            return {
                "fund_code": fund_code,
                "has_data": False,
                "analysis": "无基金经理数据"
            }

        # 分析经理经验
        experience = self._analyze_experience(manager_info)

        # 分析历史业绩
        performance = self._analyze_performance(manager_info)

        # 分析投资风格
        style = self._analyze_style(manager_info)

        # 生成经理信号
        signal = self._generate_manager_signal(experience, performance, style)

        return {
            "fund_code": fund_code,
            "has_data": True,
            "name": manager_info.get("name", "未知"),
            "experience": experience,
            "performance": performance,
            "style": style,
            "signal": signal
        }

    def _analyze_experience(self, manager_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析基金经理经验

        Args:
            manager_info: 基金经理信息

        Returns:
            dict: 经验分析
        """
        # 获取任职年限
        tenure = manager_info.get("tenure", "未知")
        fund_count = manager_info.get("fund_count", 0)

        # 判断经验水平
        if isinstance(tenure, (int, float)):
            if tenure >= 5:
                level = "experienced"
                description = f"资深基金经理，任职{tenure}年"
                score = 0.8
            elif tenure >= 3:
                level = "moderate"
                description = f"有一定经验，任职{tenure}年"
                score = 0.5
            else:
                level = "junior"
                description = f"经验较少，任职{tenure}年"
                score = 0.3
        else:
            level = "unknown"
            description = "经验信息未知"
            score = 0.5

        return {
            "tenure": tenure,
            "fund_count": fund_count,
            "level": level,
            "score": score,
            "description": description
        }

    def _analyze_performance(self, manager_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析基金经理业绩

        Args:
            manager_info: 基金经理信息

        Returns:
            dict: 业绩分析
        """
        total_return = manager_info.get("total_return", 0)
        annual_return = manager_info.get("annual_return", 0)

        # 判断业绩水平
        if annual_return > 20:
            level = "excellent"
            description = f"业绩优秀，年化收益{annual_return:.1f}%"
            score = 0.9
        elif annual_return > 10:
            level = "good"
            description = f"业绩良好，年化收益{annual_return:.1f}%"
            score = 0.7
        elif annual_return > 0:
            level = "average"
            description = f"业绩一般，年化收益{annual_return:.1f}%"
            score = 0.5
        elif annual_return > -10:
            level = "poor"
            description = f"业绩较差，年化收益{annual_return:.1f}%"
            score = 0.3
        else:
            level = "terrible"
            description = f"业绩很差，年化收益{annual_return:.1f}%"
            score = 0.1

        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "level": level,
            "score": score,
            "description": description
        }

    def _analyze_style(self, manager_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析基金经理投资风格

        Args:
            manager_info: 基金经理信息

        Returns:
            dict: 风格分析
        """
        # 这里可以基于经理的历史持仓、言论等分析风格
        # 目前简化处理
        style = manager_info.get("style", "blend")

        style_descriptions = {
            "value": "价值型投资，注重低估值和安全边际",
            "growth": "成长型投资，注重高增长潜力",
            "blend": "混合型投资，均衡配置价值和成长",
            "index": "被动指数投资，跟踪基准指数"
        }

        return {
            "style": style,
            "description": style_descriptions.get(style, "风格未知"),
            "score": 0.5
        }

    def _generate_manager_signal(self, experience: Dict, performance: Dict, style: Dict) -> Dict[str, Any]:
        """
        生成基金经理信号

        Args:
            experience: 经验分析
            performance: 业绩分析
            style: 风格分析

        Returns:
            dict: 经理信号
        """
        # 计算综合得分
        total_score = (
            experience.get("score", 0.5) * 0.3 +
            performance.get("score", 0.5) * 0.5 +
            style.get("score", 0.5) * 0.2
        )

        # 判断信号
        if total_score >= 0.7:
            signal = "positive"
            description = "基金经理能力较强"
        elif total_score >= 0.5:
            signal = "neutral"
            description = "基金经理能力一般"
        else:
            signal = "negative"
            description = "基金经理能力较弱"

        return {
            "signal": signal,
            "score": total_score,
            "description": description
        }


# 全局基金经理分析实例
fund_manager_analyzer = FundManagerAnalyzer()
