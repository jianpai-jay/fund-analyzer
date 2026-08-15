"""
配置管理模块
"""
import json
import os
from typing import List, Dict, Any


class Config:
    """配置管理类"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            # 默认配置文件路径
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "funds.json"
            )
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件不存在: {self.config_path}")
            return {"funds": [], "analysis_days": 90, "notify_webhook": ""}
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return {"funds": [], "analysis_days": 90, "notify_webhook": ""}

    def get_funds(self) -> List[Dict[str, str]]:
        """获取基金列表"""
        return self.config.get("funds", [])

    def get_analysis_days(self) -> int:
        """获取分析天数"""
        return self.config.get("analysis_days", 30)

    def get_webhook_url(self) -> str:
        """获取企业微信 Webhook URL"""
        # 优先从环境变量获取
        webhook_url = os.environ.get("WECHAT_WEBHOOK_URL")
        if webhook_url:
            return webhook_url
        # 否则从配置文件获取
        return self.config.get("notify_webhook", "")

    def get_pushplus_token(self) -> str:
        """获取 PushPlus Token"""
        # 优先从环境变量获取
        token = os.environ.get("PUSHPLUS_TOKEN")
        if token:
            return token
        # 否则从配置文件获取
        return self.config.get("pushplus_token", "")

    def get_pushplus_topic(self) -> str:
        """获取 PushPlus Topic（群组推送）"""
        # 优先从环境变量获取
        topic = os.environ.get("PUSHPLUS_TOPIC")
        if topic:
            return topic
        # 否则从配置文件获取
        return self.config.get("pushplus_topic", "")

    def add_fund(self, code: str, name: str, fund_type: str) -> bool:
        """添加基金"""
        # 检查基金是否已存在
        for fund in self.config["funds"]:
            if fund["code"] == code:
                print(f"基金 {code} 已存在")
                return False

        self.config["funds"].append({
            "code": code,
            "name": name,
            "type": fund_type
        })
        self._save_config()
        return True

    def remove_fund(self, code: str) -> bool:
        """删除基金"""
        original_length = len(self.config["funds"])
        self.config["funds"] = [
            fund for fund in self.config["funds"]
            if fund["code"] != code
        ]

        if len(self.config["funds"]) < original_length:
            self._save_config()
            return True
        print(f"基金 {code} 不存在")
        return False

    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")


# 全局配置实例
config = Config()
