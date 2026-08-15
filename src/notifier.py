"""
PushPlus 推送模块
"""
import requests
import json
from typing import List, Dict, Any
from datetime import datetime


class PushPlusNotifier:
    """PushPlus 通知类"""

    def __init__(self, token: str):
        """
        初始化

        Args:
            token: PushPlus Token
        """
        self.token = token
        self.api_url = "http://www.pushplus.plus/send"

    def send_analysis_report(self, fund_data: List[Dict[str, Any]]) -> bool:
        """
        发送分析报告

        Args:
            fund_data: 基金分析数据列表

        Returns:
            bool: 是否发送成功
        """
        if not self.token:
            print("未配置 PushPlus Token，跳过推送")
            return False

        title = "📊 基金每日分析报告"
        content = self._format_html_message(fund_data)

        return self._send_message(title, content, template="html")

    def _format_html_message(self, fund_data: List[Dict[str, Any]]) -> str:
        """
        格式化 HTML 消息

        Args:
            fund_data: 基金分析数据列表

        Returns:
            str: HTML 格式的消息
        """
        html = []

        # 标题
        html.append(f"""
<h2>📊 基金每日分析报告</h2>
<p style="color: #666; font-size: 14px;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<hr>
""")

        # 基金分析结果
        for fund in fund_data:
            if "error" in fund:
                html.append(f"""
<div style="margin-bottom: 20px; padding: 15px; background-color: #fff3f3; border-radius: 8px;">
    <h3 style="color: #e74c3c;">❌ {fund['name']} ({fund['code']})</h3>
    <p style="color: #e74c3c;">错误: {fund['error']}</p>
</div>
""")
                continue

            # 获取数据
            latest_nav = fund.get('latest_nav', 0)
            daily_return = fund.get('daily_return', 0)
            total_return = fund.get('total_return', 0)
            volatility = fund.get('volatility', 0)
            max_drawdown = fund.get('max_drawdown', 0)
            sharpe_ratio = fund.get('sharpe_ratio', 0)
            calmar_ratio = fund.get('calmar_ratio', 0)
            sortino_ratio = fund.get('sortino_ratio', 0)
            overall_score = fund.get('overall_score', 'N/A')

            # 涨跌颜色
            daily_color = "#27ae60" if daily_return >= 0 else "#e74c3c"
            total_color = "#27ae60" if total_return >= 0 else "#e74c3c"
            daily_icon = "📈" if daily_return >= 0 else "📉"

            html.append(f"""
<div style="margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db;">
    <h3 style="margin-top: 0; color: #2c3e50;">{fund['name']} ({fund['code']})</h3>
    <p style="font-size: 16px; font-weight: bold; color: #8e44ad;">综合评级: {overall_score}</p>

    <h4 style="color: #2980b9;">📈 基础指标</h4>
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">最新净值</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold;">{latest_nav:.4f}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">日涨跌幅 {daily_icon}</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold; color: {daily_color};">{daily_return:+.2f}%</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">区间收益率</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd; font-weight: bold; color: {total_color};">{total_return:+.2f}%</td>
        </tr>
    </table>

    <h4 style="color: #e67e22;">⚠️ 风险指标</h4>
    <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">年化波动率</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{volatility:.2f}%</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">最大回撤</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{max_drawdown:.2f}%</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">夏普比率</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{sharpe_ratio:.2f}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">卡玛比率</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{calmar_ratio:.2f}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">索提诺比率</td>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{sortino_ratio:.2f}</td>
        </tr>
    </table>
</div>
<hr>
""")

        # 免责声明
        html.append("""
<div style="margin-top: 20px; padding: 10px; background-color: #fff3cd; border-radius: 8px; font-size: 12px; color: #856404;">
    📌 <strong>免责声明</strong>: 以上分析仅供参考，不构成投资建议。基金有风险，投资需谨慎。
</div>
""")

        return "\n".join(html)

    def _send_message(self, title: str, content: str, template: str = "html") -> bool:
        """
        发送消息

        Args:
            title: 消息标题
            content: 消息内容
            template: 模板类型 (html, markdown, txt)

        Returns:
            bool: 是否发送成功
        """
        payload = {
            "token": self.token,
            "title": title,
            "content": content,
            "template": template
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10
            )

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

        except requests.exceptions.Timeout:
            print("推送超时")
            return False
        except requests.exceptions.RequestException as e:
            print(f"推送请求异常: {e}")
            return False
        except Exception as e:
            print(f"推送失败: {e}")
            return False

    def send_text_message(self, content: str) -> bool:
        """
        发送纯文本消息

        Args:
            content: 消息内容

        Returns:
            bool: 是否发送成功
        """
        title = "基金分析通知"
        return self._send_message(title, content, template="txt")

    def send_error_report(self, error_message: str) -> bool:
        """
        发送错误报告

        Args:
            error_message: 错误信息

        Returns:
            bool: 是否发送成功
        """
        title = "❌ 基金分析系统错误报告"

        content = f"""
<h2>❌ 基金分析系统错误报告</h2>
<p style="color: #666;">时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<hr>
<h3>错误信息</h3>
<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">{error_message}</pre>
<hr>
<p style="color: #856404;">请检查系统运行状态。</p>
"""

        return self._send_message(title, content, template="html")


def create_notifier(token: str = None) -> PushPlusNotifier:
    """
    创建通知器实例

    Args:
        token: PushPlus Token，如果不提供则从配置获取

    Returns:
        PushPlusNotifier: 通知器实例
    """
    from .config import config

    if token is None:
        token = config.get_pushplus_token()

    return PushPlusNotifier(token)
