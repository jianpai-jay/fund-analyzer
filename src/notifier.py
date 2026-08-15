"""
PushPlus 推送模块 - 优化版
"""
import requests
from typing import List, Dict, Any
from datetime import datetime


class PushPlusNotifier:
    """PushPlus 通知类"""

    # 信号翻译映射
    SIGNAL_MAP = {
        "bullish": "看涨",
        "bearish": "看跌",
        "neutral": "中性",
        "golden_cross": "金叉(看涨)",
        "death_cross": "死叉(看跌)",
        "bullish_divergence": "底背离(看涨)",
        "bearish_divergence": "顶背离(看跌)",
        "oversold": "超卖",
        "overbought": "超买",
        "above_upper": "突破上轨",
        "below_lower": "跌破下轨",
        "above_middle": "中轨上方",
        "below_middle": "中轨下方",
        "strong_bullish": "强烈看涨",
        "strong_bearish": "强烈看跌",
        "weak_bullish": "偏多",
        "weak_bearish": "偏空",
        "strong_inflow": "大幅流入",
        "inflow": "流入",
        "weak_inflow": "小幅流入",
        "strong_outflow": "大幅流出",
        "outflow": "流出",
        "weak_outflow": "小幅流出",
        "very_positive": "非常积极",
        "positive": "积极",
        "very_negative": "非常消极",
        "negative": "消极",
        "extreme_greed": "极度贪婪",
        "greed": "贪婪",
        "fear": "恐慌",
        "extreme_fear": "极度恐慌",
        "strong_buy": "强烈买入",
        "buy": "买入",
        "weak_buy": "弱买入",
        "strong_sell": "强烈卖出",
        "sell": "卖出",
        "weak_sell": "弱卖出",
        "hold": "持有",
        "unknown": "暂无数据",
        "N/A": "暂无数据"
    }

    def __init__(self, token: str):
        self.token = token
        self.api_url = "http://www.pushplus.plus/send"

    def _translate(self, value: str) -> str:
        """翻译信号值为中文"""
        if not value:
            return "暂无数据"
        return self.SIGNAL_MAP.get(value, value)

    def send_analysis_report(self, fund_data: List[Dict[str, Any]]) -> bool:
        """发送分析报告"""
        if not self.token:
            print("未配置 PushPlus Token，跳过推送")
            return False

        title = "基金每日分析报告"
        content = self._format_report(fund_data)
        return self._send_message(title, content, template="html")

    def _format_report(self, fund_data: List[Dict[str, Any]]) -> str:
        """格式化报告"""
        html = []
        html.append(self._header())

        for fund in fund_data:
            if "error" in fund:
                html.append(self._error_card(fund))
                continue
            html.append(self._fund_card(fund))

        html.append(self._footer())
        return "\n".join(html)

    def _header(self) -> str:
        """报告头部"""
        return f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 15px;">
<h2 style="text-align: center; color: #333; margin-bottom: 5px;">基金每日分析报告</h2>
<p style="text-align: center; color: #999; font-size: 12px; margin-top: 0;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
"""

    def _error_card(self, fund: Dict) -> str:
        """错误卡片"""
        return f"""
<div style="background: #fff5f5; border-radius: 8px; padding: 12px; margin-bottom: 15px; border-left: 4px solid #e74c3c;">
    <b style="color: #e74c3c;">{fund['name']} ({fund['code']})</b>
    <p style="color: #e74c3c; margin: 5px 0 0 0;">获取数据失败</p>
</div>
"""

    def _fund_card(self, fund: Dict) -> str:
        """基金卡片"""
        name = fund.get('name', '')
        code = fund.get('code', '')
        overall_score = fund.get('overall_score', {})
        rating = overall_score.get('rating', '暂无') if isinstance(overall_score, dict) else '暂无'
        score = overall_score.get('score', 0) if isinstance(overall_score, dict) else 0

        # 获取涨跌颜色
        daily_return = fund.get('daily_return', 0)
        total_return = fund.get('total_return', 0)
        color = "#e74c3c" if daily_return < 0 else "#27ae60"

        html = f"""
<div style="background: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 1px solid #e9ecef;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <b style="font-size: 16px; color: #333;">{name}</b>
        <span style="color: #999; font-size: 12px;">{code}</span>
    </div>
    <div style="text-align: center; padding: 10px; background: white; border-radius: 8px; margin-bottom: 15px;">
        <div style="font-size: 24px; font-weight: bold; color: {color};">{daily_return:+.2f}%</div>
        <div style="font-size: 12px; color: #999;">今日涨跌</div>
    </div>
"""

        # 基础信息
        html += f"""
    <div style="background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">基础信息</div>
        <table style="width: 100%; font-size: 13px;">
            <tr><td style="padding: 4px 0; color: #666;">最新净值</td><td style="padding: 4px 0; text-align: right;">{fund.get('latest_nav', 0):.4f}</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">区间收益</td><td style="padding: 4px 0; text-align: right; color: {'#27ae60' if total_return >= 0 else '#e74c3c'};">{total_return:+.2f}%</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">年化波动率</td><td style="padding: 4px 0; text-align: right;">{fund.get('volatility', 0):.2f}%</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">最大回撤</td><td style="padding: 4px 0; text-align: right;">{fund.get('max_drawdown', 0):.2f}%</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">夏普比率</td><td style="padding: 4px 0; text-align: right;">{fund.get('sharpe_ratio', 0):.2f}</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">综合评级</td><td style="padding: 4px 0; text-align: right; font-weight: bold;">{rating}</td></tr>
        </table>
    </div>
"""

        # 技术分析
        technical = fund.get('technical', {})
        if technical:
            html += f"""
    <div style="background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">技术分析</div>
        <table style="width: 100%; font-size: 13px;">
            <tr><td style="padding: 4px 0; color: #666;">综合信号</td><td style="padding: 4px 0; text-align: right;">{self._translate(technical.get('overall_signal', ''))}</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">MACD</td><td style="padding: 4px 0; text-align: right;">{self._translate(technical.get('macd_signal', ''))}</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">RSI</td><td style="padding: 4px 0; text-align: right;">{self._translate(technical.get('rsi_signal', ''))}</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">布林带</td><td style="padding: 4px 0; text-align: right;">{self._translate(technical.get('bollinger_signal', ''))}</td></tr>
        </table>
    </div>
"""

        # 资金流向
        capital = fund.get('capital', {})
        if capital:
            html += f"""
    <div style="background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">资金流向</div>
        <table style="width: 100%; font-size: 13px;">
            <tr><td style="padding: 4px 0; color: #666;">主力资金</td><td style="padding: 4px 0; text-align: right;">{capital.get('main_flow', '暂无数据')}</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">北向资金</td><td style="padding: 4px 0; text-align: right;">{capital.get('north_flow', '暂无数据')}</td></tr>
        </table>
    </div>
"""

        # 新闻分析
        news = fund.get('news', {})
        if news:
            html += f"""
    <div style="background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">新闻分析</div>
        <table style="width: 100%; font-size: 13px;">
            <tr><td style="padding: 4px 0; color: #666;">市场情绪</td><td style="padding: 4px 0; text-align: right;">{news.get('sentiment', '暂无')}</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">政策影响</td><td style="padding: 4px 0; text-align: right;">{news.get('policy_impact', '暂无')}</td></tr>
        </table>
    </div>
"""

        # 情绪分析
        sentiment = fund.get('sentiment', {})
        if sentiment:
            fear_greed = sentiment.get('fear_greed_index', '暂无')
            advice = sentiment.get('advice', '暂无')
            html += f"""
    <div style="background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">情绪分析</div>
        <table style="width: 100%; font-size: 13px;">
            <tr><td style="padding: 4px 0; color: #666;">恐慌贪婪指数</td><td style="padding: 4px 0; text-align: right;">{fear_greed}</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">操作建议</td><td style="padding: 4px 0; text-align: right;">{advice}</td></tr>
        </table>
    </div>
"""

        # 交易信号
        signal = fund.get('signal', {})
        if signal:
            signal_type = signal.get('type', '')
            conditions = signal.get('conditions', [])
            confidence = signal.get('confidence', 0)
            signal_color = "#27ae60" if signal.get('category') == 'buy' else "#e74c3c" if signal.get('category') == 'sell' else "#f39c12"

            html += f"""
    <div style="background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">交易信号</div>
        <div style="text-align: center; padding: 8px; background: {signal_color}15; border-radius: 6px; margin-bottom: 8px;">
            <span style="color: {signal_color}; font-weight: bold; font-size: 15px;">{self._translate(signal_type)}</span>
            <span style="color: #999; font-size: 12px; margin-left: 8px;">置信度 {confidence:.0%}</span>
        </div>
        <div style="font-size: 12px; color: #666;">
            <b>触发条件:</b> {', '.join(conditions) if conditions else '无'}
        </div>
    </div>
"""

        # 持仓分析
        holdings = fund.get('holdings', {})
        if holdings and holdings.get('has_data'):
            concentration = holdings.get('concentration', {})
            html += f"""
    <div style="background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">持仓分析</div>
        <table style="width: 100%; font-size: 13px;">
            <tr><td style="padding: 4px 0; color: #666;">持仓数量</td><td style="padding: 4px 0; text-align: right;">{holdings.get('total_holdings', 0)}只</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">集中度</td><td style="padding: 4px 0; text-align: right;">{concentration.get('description', '暂无')}</td></tr>
        </table>
    </div>
"""

        # 定投策略
        dca = fund.get('dca_strategy', {})
        if dca and dca.get('has_data'):
            dca_result = dca.get('dca_result', {})
            dca_signal = dca.get('signal', {})
            html += f"""
    <div style="background: white; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
        <div style="font-weight: bold; color: #333; margin-bottom: 8px; border-bottom: 1px solid #eee; padding-bottom: 5px;">定投策略</div>
        <table style="width: 100%; font-size: 13px;">
            <tr><td style="padding: 4px 0; color: #666;">定投收益率</td><td style="padding: 4px 0; text-align: right;">{dca_result.get('return_rate', 0):.2f}%</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">建议</td><td style="padding: 4px 0; text-align: right;">{dca_signal.get('description', '暂无')}</td></tr>
        </table>
    </div>
"""

        html += "</div>"
        return html

    def _footer(self) -> str:
        """报告底部"""
        return """
<div style="text-align: center; padding: 15px; font-size: 11px; color: #999;">
    <p style="margin: 0;">以上分析仅供参考，不构成投资建议</p>
    <p style="margin: 5px 0 0 0;">基金有风险，投资需谨慎</p>
</div>
</div>
"""

    def _send_message(self, title: str, content: str, template: str = "html") -> bool:
        """发送消息"""
        payload = {
            "token": self.token,
            "title": title,
            "content": content,
            "template": template
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    print("推送成功")
                    return True
                else:
                    print(f"推送失败: {result.get('msg')}")
                    return False
            else:
                print(f"推送失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"推送失败: {e}")
            return False

    def send_signal_alert(self, fund_data: Dict[str, Any]) -> bool:
        """发送交易信号提醒"""
        if not self.token:
            return False

        signal = fund_data.get("signal", {})
        signal_category = signal.get("category")

        if signal_category not in ["buy", "sell"]:
            return False

        title = f"{'买入' if signal_category == 'buy' else '卖出'}信号 - {fund_data['name']}"
        content = self._format_signal_alert(fund_data)
        return self._send_message(title, content, template="html")

    def _format_signal_alert(self, fund_data: Dict[str, Any]) -> str:
        """格式化信号提醒"""
        signal = fund_data.get("signal", {})
        signal_category = signal.get("category")
        signal_color = "#27ae60" if signal_category == "buy" else "#e74c3c"

        return f"""
<div style="font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; padding: 15px;">
    <div style="background: {signal_color}; color: white; text-align: center; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
        <div style="font-size: 20px; font-weight: bold;">{'买入' if signal_category == 'buy' else '卖出'}信号</div>
        <div style="font-size: 14px; margin-top: 5px;">{fund_data['name']} ({fund_data['code']})</div>
    </div>
    <div style="background: #f8f9fa; border-radius: 8px; padding: 15px;">
        <p style="margin: 5px 0;"><b>信号强度:</b> {signal.get('confidence', 0):.0%}</p>
        <p style="margin: 5px 0;"><b>触发条件:</b> {', '.join(signal.get('conditions', []))}</p>
    </div>
</div>
"""


def create_notifier(token: str = None) -> PushPlusNotifier:
    """创建通知器"""
    from .config import config
    if token is None:
        token = config.get_pushplus_token()
    return PushPlusNotifier(token)
