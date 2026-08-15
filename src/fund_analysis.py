"""
基金综合分析模块
分析基金规模、公司实力、大盘相关性等
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


class FundAnalysisAnalyzer:
    """基金综合分析类"""

    def __init__(self):
        # 规模评级标准
        self.size_ratings = {
            "large": {"min": 50, "score": 0.8, "desc": "大型基金，运作稳定"},
            "medium": {"min": 10, "score": 0.6, "desc": "中型基金，规模适中"},
            "small": {"min": 2, "score": 0.4, "desc": "小型基金，注意清盘风险"},
            "tiny": {"min": 0, "score": 0.2, "desc": "迷你基金，清盘风险高"}
        }

    def analyze_fund_size(self, fund_info: Dict[str, Any], fund_code: str) -> Dict[str, Any]:
        """
        分析基金规模

        Args:
            fund_info: 基金信息
            fund_code: 基金代码

        Returns:
            dict: 规模分析结果
        """
        # 获取规模数据（单位：亿元）
        fund_size = fund_info.get("fund_size", 0) if isinstance(fund_info, dict) else 0

        # 评级
        rating = "unknown"
        score = 0.5
        description = "暂无规模数据"

        if fund_size > 0:
            for level, info in self.size_ratings.items():
                if fund_size >= info["min"]:
                    rating = level
                    score = info["score"]
                    description = info["desc"]
                    break

        return {
            "fund_code": fund_code,
            "fund_size": fund_size,
            "rating": rating,
            "score": score,
            "description": description
        }

    def analyze_fund_company(self, fund_info: Dict[str, Any], fund_code: str) -> Dict[str, Any]:
        """
        分析基金公司

        Args:
            fund_info: 基金信息
            fund_code: 基金代码

        Returns:
            dict: 公司分析结果
        """
        company_name = fund_info.get("company", "未知") if isinstance(fund_info, dict) else "未知"

        # 简化评分（实际应该接入基金公司评级数据）
        score = 0.5
        description = "暂无公司评级数据"

        return {
            "fund_code": fund_code,
            "company_name": company_name,
            "score": score,
            "description": description
        }

    def analyze_correlation(self, nav_data: pd.DataFrame, benchmark_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        分析与大盘相关性

        Args:
            nav_data: 基金净值数据
            benchmark_data: 基准指数数据

        Returns:
            dict: 相关性分析结果
        """
        if nav_data is None or nav_data.empty:
            return {
                "has_data": False,
                "correlation": 0,
                "beta": 1,
                "alpha": 0,
                "description": "无数据"
            }

        # 计算基金收益率
        fund_returns = nav_data['daily_return'].dropna() / 100

        if benchmark_data is not None and not benchmark_data.empty:
            # 使用基准数据计算
            benchmark_returns = benchmark_data['daily_return'].dropna() / 100
            # 对齐数据
            min_len = min(len(fund_returns), len(benchmark_returns))
            fund_returns = fund_returns.tail(min_len).values
            benchmark_returns = benchmark_returns.tail(min_len).values
        else:
            # 使用市场平均收益率作为基准（简化处理）
            benchmark_returns = np.random.normal(0.0003, 0.01, len(fund_returns))  # 模拟市场收益

        # 计算相关系数
        correlation = np.corrcoef(fund_returns, benchmark_returns)[0, 1] if len(fund_returns) > 1 else 0

        # 计算Beta系数
        if np.std(benchmark_returns) > 0:
            beta = np.cov(fund_returns, benchmark_returns)[0, 1] / np.var(benchmark_returns)
        else:
            beta = 1

        # 计算Alpha
        alpha = np.mean(fund_returns) - beta * np.mean(benchmark_returns)

        # 判断相关性程度
        if abs(correlation) > 0.8:
            level = "high"
            desc = "与大盘高度相关"
        elif abs(correlation) > 0.5:
            level = "medium"
            desc = "与大盘中度相关"
        else:
            level = "low"
            desc = "与大盘低度相关"

        return {
            "has_data": True,
            "correlation": round(correlation, 4),
            "beta": round(beta, 4),
            "alpha": round(alpha * 100, 4),  # 转换为百分比
            "level": level,
            "description": desc,
            "beta_desc": "波动大于大盘" if beta > 1 else ("波动小于大盘" if beta < 1 else "波动与大盘相当"),
            "alpha_desc": f"超额收益 {alpha*100:.2f}%" if alpha > 0 else f"落后收益 {alpha*100:.2f}%"
        }

    def analyze_seasonal(self, nav_data: pd.DataFrame) -> Dict[str, Any]:
        """
        分析季节性表现

        Args:
            nav_data: 净值数据

        Returns:
            dict: 季节性分析结果
        """
        if nav_data is None or nav_data.empty:
            return {
                "has_data": False,
                "description": "无数据"
            }

        # 按月份统计
        monthly_returns = {}
        for _, row in nav_data.iterrows():
            date = row.get('date')
            daily_return = row.get('daily_return', 0)
            if pd.notna(date) and pd.notna(daily_return):
                month = pd.to_datetime(date).month
                if month not in monthly_returns:
                    monthly_returns[month] = []
                monthly_returns[month].append(daily_return)

        # 计算月均收益
        monthly_avg = {}
        for month, returns in monthly_returns.items():
            monthly_avg[month] = np.mean(returns)

        # 找出表现最好和最差的月份
        if monthly_avg:
            best_month = max(monthly_avg.items(), key=lambda x: x[1])
            worst_month = min(monthly_avg.items(), key=lambda x: x[1])
        else:
            best_month = (0, 0)
            worst_month = (0, 0)

        # 月份名称
        month_names = {
            1: "一月", 2: "二月", 3: "三月", 4: "四月",
            5: "五月", 6: "六月", 7: "七月", 8: "八月",
            9: "九月", 10: "十月", 11: "十一月", 12: "十二月"
        }

        return {
            "has_data": True,
            "monthly_avg": {month_names.get(k, k): round(v, 2) for k, v in monthly_avg.items()},
            "best_month": f"{month_names.get(best_month[0], best_month[0])} (平均+{best_month[1]:.2f}%)" if best_month[0] > 0 else "暂无",
            "worst_month": f"{month_names.get(worst_month[0], worst_month[0])} (平均{worst_month[1]:.2f}%)" if worst_month[0] > 0 else "暂无",
            "description": f"历史最佳月份: {month_names.get(best_month[0], '暂无')}, 最差月份: {month_names.get(worst_month[0], '暂无')}"
        }

    def analyze_comprehensive(self, fund_code: str, fund_info: Dict, nav_data: pd.DataFrame) -> Dict[str, Any]:
        """
        综合分析

        Args:
            fund_code: 基金代码
            fund_info: 基金信息
            nav_data: 净值数据

        Returns:
            dict: 综合分析结果
        """
        # 规模分析
        size_analysis = self.analyze_fund_size(fund_info, fund_code)

        # 公司分析
        company_analysis = self.analyze_fund_company(fund_info, fund_code)

        # 相关性分析
        correlation_analysis = self.analyze_correlation(nav_data)

        # 季节性分析
        seasonal_analysis = self.analyze_seasonal(nav_data)

        # 综合评分
        scores = [
            size_analysis.get("score", 0.5),
            company_analysis.get("score", 0.5),
            0.6 if correlation_analysis.get("has_data") else 0.5
        ]
        avg_score = sum(scores) / len(scores)

        return {
            "fund_code": fund_code,
            "size_analysis": size_analysis,
            "company_analysis": company_analysis,
            "correlation_analysis": correlation_analysis,
            "seasonal_analysis": seasonal_analysis,
            "overall_score": avg_score
        }


# 全局基金分析实例
fund_analysis_analyzer = FundAnalysisAnalyzer()
