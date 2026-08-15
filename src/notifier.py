"""
企业微信推送模块
"""
import requests
import json
from typing import List, Dict, Any
from datetime import datetime


class WeChatNotifier:
    """企业微信通知类"""

    def __init__(self, webhook_url: str):
        """
        初始化

        Args:
            webhook_url: 企业微信机器人 Webhook URL
        """
        self.webhook_url = webhook_url

    def send_analysis_report(self, fund_data: List[Dict[str, Any]]) -> bool:
        """
        发送分析报告

        Args:
            fund_data: 基金分析数据列表

        Returns:
            bool: 是否发送成功
        """
        if not self.webhook_url:
            print("未配置 Webhook URL，跳过推送")
            return False

        message = self._format_message(fund_data)

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": message
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    print("推送成功")
                    return True
                else:
                    print(f"推送失败: {result.get('errmsg')}")
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

    def _format_message(self, fund_data: List[Dict[str, Any]]) -> str:
        """
        格式化消息内容

        Args:
            fund_data: 基金分析数据列表

        Returns:
            str: 格式化后的消息
        """
        lines = []

        # 标题
        lines.append("# 📊 基金每日分析报告")
        lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 基金分析结果
        for fund in fund_data:
            if "error" in fund:
                lines.append(f"## ❌ {fund['name']} ({fund['code']})")
                lines.append(f"错误: {fund['error']}")
                lines.append("")
                continue

            # 基金名称和评级
            lines.append(f"## {fund['name']} ({fund['code']})")
            lines.append(f"**综合评级: {fund.get('overall_score', 'N/A')}**")
            lines.append("")

            # 基础指标
            lines.append("### 📈 基础指标")
            lines.append(f"- 最新净值: **{fund.get('latest_nav', 0):.4f}**")
            lines.append(f"- 日涨跌幅: **{fund.get('daily_return', 0):+.2f}%**")
            lines.append(f"- 区间收益率: **{fund.get('total_return', 0):+.2f}%**")
            lines.append("")

            # 风险指标
            lines.append("### ⚠️ 风险指标")
            lines.append(f"- 年化波动率: {fund.get('volatility', 0):.2f}%")
            lines.append(f"- 最大回撤: {fund.get('max_drawdown', 0):.2f}%")
            lines.append(f"- 夏普比率: {fund.get('sharpe_ratio', 0):.2f}")
            lines.append(f"- 卡玛比率: {fund.get('calmar_ratio', 0):.2f}")
            lines.append(f"- 索提诺比率: {fund.get('sortino_ratio', 0):.2f}")
            lines.append("")

            # 分隔线
            lines.append("---")
            lines.append("")

        # 免责声明
        lines.append("📌 **免责声明**")
        lines.append("以上分析仅供参考，不构成投资建议。基金有风险，投资需谨慎。")

        return "\n".join(lines)

    def send_text_message(self, content: str) -> bool:
        """
        发送纯文本消息

        Args:
            content: 消息内容

        Returns:
            bool: 是否发送成功
        """
        if not self.webhook_url:
            print("未配置 Webhook URL，跳过推送")
            return False

        payload = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("errcode") == 0
            return False

        except Exception as e:
            print(f"推送文本消息失败: {e}")
            return False

    def send_error_report(self, error_message: str) -> bool:
        """
        发送错误报告

        Args:
            error_message: 错误信息

        Returns:
            bool: 是否发送成功
        """
        message = f"""# ❌ 基金分析系统错误报告

> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 错误信息
{error_message}

---
请检查系统运行状态。"""

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": message
            }
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("errcode") == 0
            return False

        except Exception as e:
            print(f"推送错误报告失败: {e}")
            return False


def create_notifier(webhook_url: str = None) -> WeChatNotifier:
    """
    创建通知器实例

    Args:
        webhook_url: Webhook URL，如果不提供则从配置获取

    Returns:
        WeChatNotifier: 通知器实例
    """
    from .config import config

    if webhook_url is None:
        webhook_url = config.get_webhook_url()

    return WeChatNotifier(webhook_url)
