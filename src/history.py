"""
历史记录模块
保存和查询历史分析结果
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path


class HistoryManager:
    """历史记录管理类"""

    def __init__(self, history_dir: str = None):
        """
        初始化

        Args:
            history_dir: 历史记录存储目录
        """
        if history_dir is None:
            history_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "history"
            )
        self.history_dir = history_dir
        self._ensure_dir()

    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.history_dir, exist_ok=True)

    def save_analysis(self, fund_code: str, result: Dict[str, Any]) -> bool:
        """
        保存分析结果

        Args:
            fund_code: 基金代码
            result: 分析结果

        Returns:
            bool: 是否保存成功
        """
        try:
            # 按日期组织目录
            date_str = datetime.now().strftime("%Y-%m-%d")
            date_dir = os.path.join(self.history_dir, date_str)
            os.makedirs(date_dir, exist_ok=True)

            # 保存文件
            file_path = os.path.join(date_dir, f"{fund_code}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # 更新索引
            self._update_index(fund_code, date_str, result)

            return True
        except Exception as e:
            print(f"保存分析结果失败: {e}")
            return False

    def _update_index(self, fund_code: str, date_str: str, result: Dict):
        """更新索引文件"""
        index_path = os.path.join(self.history_dir, "index.json")

        # 读取现有索引
        index = {}
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            except:
                index = {}

        # 更新索引
        if fund_code not in index:
            index[fund_code] = {"name": result.get("name", ""), "records": []}

        # 检查是否已存在该日期的记录
        records = index[fund_code]["records"]
        records = [r for r in records if r["date"] != date_str]

        # 添加新记录
        records.append({
            "date": date_str,
            "daily_return": result.get("daily_return", 0),
            "total_return": result.get("total_return", 0),
            "signal": result.get("signal", {}).get("type", "hold"),
            "score": result.get("overall_score", {}).get("score", 0) if isinstance(result.get("overall_score"), dict) else 0
        })

        # 按日期排序
        records.sort(key=lambda x: x["date"], reverse=True)

        # 只保留最近90天
        index[fund_code]["records"] = records[:90]

        # 保存索引
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def get_history(self, fund_code: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取历史分析记录

        Args:
            fund_code: 基金代码
            days: 获取天数

        Returns:
            list: 历史记录列表
        """
        index_path = os.path.join(self.history_dir, "index.json")

        if not os.path.exists(index_path):
            return []

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index = json.load(f)

            if fund_code not in index:
                return []

            records = index[fund_code]["records"][:days]
            return records

        except Exception as e:
            print(f"获取历史记录失败: {e}")
            return []

    def get_trend(self, fund_code: str, days: int = 30) -> Dict[str, Any]:
        """
        获取基金趋势分析

        Args:
            fund_code: 基金代码
            days: 分析天数

        Returns:
            dict: 趋势分析结果
        """
        records = self.get_history(fund_code, days)

        if not records:
            return {
                "has_data": False,
                "message": "无历史数据"
            }

        # 计算趋势
        returns = [r.get("daily_return", 0) for r in records]
        scores = [r.get("score", 50) for r in records]
        signals = [r.get("signal", "hold") for r in records]

        # 平均收益
        avg_return = sum(returns) / len(returns) if returns else 0

        # 趋势方向
        if len(returns) >= 2:
            recent_avg = sum(returns[:5]) / min(5, len(returns))
            earlier_avg = sum(returns[5:]) / max(1, len(returns) - 5) if len(returns) > 5 else returns[-1]

            if recent_avg > earlier_avg * 1.1:
                trend = "improving"
                trend_desc = "近期表现改善"
            elif recent_avg < earlier_avg * 0.9:
                trend = "worsening"
                trend_desc = "近期表现走弱"
            else:
                trend = "stable"
                trend_desc = "近期表现稳定"
        else:
            trend = "unknown"
            trend_desc = "数据不足"

        # 信号统计
        signal_counts = {}
        for s in signals:
            signal_counts[s] = signal_counts.get(s, 0) + 1

        # 最近信号
        latest_signal = signals[0] if signals else "hold"

        return {
            "has_data": True,
            "record_count": len(records),
            "avg_return": avg_return,
            "trend": trend,
            "trend_desc": trend_desc,
            "signal_counts": signal_counts,
            "latest_signal": latest_signal,
            "latest_score": scores[0] if scores else 50
        }

    def save_batch(self, results: List[Dict[str, Any]]) -> bool:
        """
        批量保存分析结果

        Args:
            results: 分析结果列表

        Returns:
            bool: 是否全部保存成功
        """
        success_count = 0
        for result in results:
            fund_code = result.get("code", "")
            if fund_code and self.save_analysis(fund_code, result):
                success_count += 1

        return success_count == len(results)


# 全局历史记录管理实例
history_manager = HistoryManager()
