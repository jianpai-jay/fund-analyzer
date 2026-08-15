"""
基金研究助手 - Web控制面板启动脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_app import run_web_app

if __name__ == '__main__':
    print("=" * 60)
    print("📊 基金研究助手 - Web控制面板")
    print("=" * 60)
    print()
    print("启动后请访问: http://localhost:5000")
    print()
    print("功能说明:")
    print("  - 🔍 开始分析: 仅运行基金分析")
    print("  - 📤 分析并推送: 运行分析并推送到微信")
    print("  - 🔄 刷新状态: 手动刷新运行状态")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()

    run_web_app(host='0.0.0.0', port=5000, debug=False)
