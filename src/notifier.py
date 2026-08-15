# -*- coding: utf-8 -*-
"""
PushPlus 推送模块 - 精简版
"""
import requests
from typing import List, Dict, Any
from datetime import datetime


class PushPlusNotifier:
    """PushPlus 通知类"""

    SIGNAL_MAP = {
        "bullish": "看涨", "bearish": "看跌", "neutral": "中性",
        "golden_cross": "金叉(涨)", "death_cross": "死叉(跌)",
        "bullish_divergence": "底背离(涨)", "bearish_divergence": "顶背离(跌)",
        "oversold": "超卖", "overbought": "超买",
        "above_upper": "突破上轨", "below_lower": "跌破下轨",
        "above_middle": "中轨上方", "below_middle": "中轨下方",
        "strong_bullish": "强看涨", "strong_bearish": "强看跌",
        "weak_bullish": "偏多", "weak_bearish": "偏空",
        "strong_inflow": "大幅流入", "inflow": "流入",
        "weak_inflow": "小幅流入", "strong_outflow": "大幅流出",
        "outflow": "流出", "weak_outflow": "小幅流出",
        "very_positive": "非常积极", "positive": "积极",
        "very_negative": "非常消极", "negative": "消极",
        "extreme_greed": "极度贪婪", "greed": "贪婪",
        "fear": "恐慌", "extreme_fear": "极度恐慌",
        "strong_buy": "强烈买入", "buy": "买入",
        "weak_buy": "弱买入", "strong_sell": "强烈卖出",
        "sell": "卖出", "weak_sell": "弱卖出",
        "hold": "持有", "unknown": "暂无", "N/A": "暂无"
    }

    def __init__(self, token: str):
        self.token = token
        self.api_url = "http://www.pushplus.plus/send"

    def _t(self, v: str) -> str:
        if not v:
            return "暂无"
        return self.SIGNAL_MAP.get(v, v)

    def send_analysis_report(self, fund_data: List[Dict[str, Any]]) -> bool:
        if not self.token:
            print("未配置 PushPlus Token")
            return False
        content = self._format(fund_data)
        return self._send("基金分析报告", content, "html")

    def _format(self, funds: List[Dict]) -> str:
        parts = [f'<div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:10px;font-size:14px;">']
        parts.append(f'<h2 style="text-align:center;margin:5px 0;">📊 基金分析</h2>')
        parts.append(f'<p style="text-align:center;color:#999;font-size:12px;">{datetime.now().strftime("%m-%d %H:%M")}</p>')

        for f in funds:
            if "error" in f:
                parts.append(f'<div style="background:#fff5f5;padding:10px;border-radius:8px;margin:8px 0;border-left:3px solid #e74c3c;"><b>{f["name"]}</b> 获取失败</div>')
                continue
            parts.append(self._card(f))

        parts.append('<p style="text-align:center;color:#999;font-size:11px;margin-top:10px;">仅供参考，不构成投资建议</p>')
        parts.append('</div>')
        return "\n".join(parts)

    def _card(self, f: Dict) -> str:
        name = f.get('name', '')
        code = f.get('code', '')
        dr = f.get('daily_return', 0)
        tr = f.get('total_return', 0)
        nav = f.get('latest_nav', 0)
        color = "#e74c3c" if dr < 0 else "#27ae60"
        score = f.get('overall_score', {})
        rating = score.get('rating', '暂无') if isinstance(score, dict) else '暂无'

        h = [f'<div style="background:#f5f5f5;padding:12px;border-radius:8px;margin:8px 0;">']
        h.append(f'<div style="display:flex;justify-content:space-between;"><b>{name}</b><span style="color:#999;">{code}</span></div>')
        h.append(f'<div style="text-align:center;margin:8px 0;"><span style="font-size:22px;font-weight:bold;color:{color};">{dr:+.2f}%</span></div>')

        # 基础指标
        h.append(f'<table style="width:100%;font-size:13px;">')
        h.append(f'<tr><td>净值</td><td style="text-align:right;">{nav:.4f}</td>')
        h.append(f'<td>收益</td><td style="text-align:right;color:{"#27ae60" if tr >= 0 else "#e74c3c"};">{tr:+.2f}%</td></tr>')
        h.append(f'<tr><td>波动率</td><td style="text-align:right;">{f.get("volatility", 0):.1f}%</td>')
        h.append(f'<td>回撤</td><td style="text-align:right;">{f.get("max_drawdown", 0):.1f}%</td></tr>')
        h.append(f'<tr><td>夏普</td><td style="text-align:right;">{f.get("sharpe_ratio", 0):.2f}</td>')
        h.append(f'<td>评级</td><td style="text-align:right;font-weight:bold;">{rating}</td></tr>')
        h.append('</table>')

        # 技术分析
        tech = f.get('technical', {})
        if tech:
            h.append(f'<div style="border-top:1px solid #eee;margin-top:8px;padding-top:8px;"><b>技术:</b> {self._t(tech.get("overall_signal", ""))} | MACD:{self._t(tech.get("macd_signal", ""))} RSI:{self._t(tech.get("rsi_signal", ""))}</div>')

        # 资金流向
        cap = f.get('capital', {})
        if cap:
            h.append(f'<div><b>资金:</b> 主力{cap.get("main_flow", "暂无")} 北向{cap.get("north_flow", "暂无")}</div>')

        # 信号
        sig = f.get('signal', {})
        if sig:
            sc = sig.get('category', '')
            scolor = "#27ae60" if sc == 'buy' else "#e74c3c" if sc == 'sell' else "#f39c12"
            h.append(f'<div style="background:{scolor}15;padding:8px;border-radius:6px;margin-top:8px;text-align:center;">')
            h.append(f'<div style="color:{scolor};font-weight:bold;font-size:16px;">{self._t(sig.get("type", ""))}</div>')
            h.append(f'<div style="font-size:12px;color:#666;">置信度 {sig.get("confidence", 0):.0%} | {sig.get("reason", "综合分析")}</div>')

            warnings = sig.get('risk_warnings', [])
            if warnings:
                h.append(f'<div style="font-size:11px;color:#856404;margin-top:4px;">⚠ {" | ".join(warnings[:2])}</div>')

            plan = sig.get('action_plan', {})
            if plan:
                h.append(f'<div style="font-size:11px;color:#0c5460;margin-top:4px;">建议: {plan.get("action", "持有")} | 止损{plan.get("stop_loss", "5%")} 止盈{plan.get("take_profit", "15%")}</div>')
            h.append('</div>')

        h.append('</div>')
        return "\n".join(h)

    def _send(self, title: str, content: str, template: str = "html") -> bool:
        payload = {"token": self.token, "title": title, "content": content, "template": template}
        try:
            print(f"推送内容长度: {len(content)}")
            response = requests.post(self.api_url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"推送结果: {result}")
                return result.get("code") == 200
            print(f"推送失败，状态码: {response.status_code}")
            return False
        except Exception as e:
            print(f"推送失败: {e}")
            return False

    def send_signal_alert(self, fund_data: Dict[str, Any]) -> bool:
        if not self.token:
            return False
        signal = fund_data.get("signal", {})
        if signal.get("category") not in ["buy", "sell"]:
            return False
        title = f"{'买入' if signal['category'] == 'buy' else '卖出'} - {fund_data['name']}"
        content = f'<div style="padding:15px;text-align:center;"><h2>{title}</h2><p>置信度: {signal.get("confidence", 0):.0%}</p></div>'
        return self._send(title, content, "html")


def create_notifier(token: str = None) -> PushPlusNotifier:
    from .config import config
    if token is None:
        token = config.get_pushplus_token()
    return PushPlusNotifier(token)
