"""
Web应用模块 - 移动端优化版
提供一键分析推送功能，支持手机访问
"""
import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.main import analyze_all_funds
from src.notifier import create_notifier

app = Flask(__name__)

# 全局状态
analysis_status = {
    "running": False,
    "last_run": None,
    "last_result": None,
    "error": None,
    "logs": []
}

# 移动端优化的HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>基金推送助手</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 15px;
            padding-bottom: 30px;
        }
        .container {
            max-width: 500px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 20px;
            padding: 20px 0;
        }
        .header h1 {
            font-size: 2em;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .header p {
            font-size: 1em;
            opacity: 0.9;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }
        .card-title {
            font-size: 1.1em;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
        }
        .status-item {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-item .label {
            font-size: 0.9em;
            color: #666;
        }
        .status-item .value {
            font-size: 1em;
            font-weight: bold;
            color: #333;
        }
        .status-item.running .value { color: #f39c12; }
        .status-item.success .value { color: #27ae60; }
        .status-item.error .value { color: #e74c3c; }

        /* 一键推送按钮 - 大尺寸，适合手机触摸 */
        .push-btn-container {
            padding: 20px 0;
        }
        .push-btn {
            width: 100%;
            padding: 25px 20px;
            border: none;
            border-radius: 16px;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            box-shadow: 0 8px 25px rgba(17, 153, 142, 0.4);
            min-height: 80px;
        }
        .push-btn:active:not(:disabled) {
            transform: scale(0.98);
            box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
        }
        .push-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
            box-shadow: none;
        }
        .push-btn .icon {
            font-size: 1.5em;
        }
        .push-btn .text {
            flex: 1;
        }
        .push-btn .subtext {
            font-size: 0.7em;
            font-weight: normal;
            opacity: 0.9;
            margin-top: 4px;
        }

        /* 次要按钮 */
        .btn-secondary {
            width: 100%;
            padding: 15px 20px;
            border: none;
            border-radius: 12px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-top: 10px;
            min-height: 50px;
        }
        .btn-secondary:active:not(:disabled) {
            transform: scale(0.98);
        }
        .btn-secondary:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }

        .fund-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .fund-tag {
            background: #e8f4fd;
            color: #2980b9;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }
        .log-box {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 12px;
            border-radius: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.8em;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .log-box .info { color: #4ec9b0; }
        .log-box .success { color: #6a9955; }
        .log-box .error { color: #f44747; }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 20px;
            opacity: 0.8;
            font-size: 0.85em;
        }

        /* 移动端优化 */
        @media (max-width: 480px) {
            body {
                padding: 10px;
            }
            .header h1 {
                font-size: 1.6em;
            }
            .push-btn {
                padding: 20px 15px;
                font-size: 1.2em;
                min-height: 70px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 基金推送助手</h1>
            <p>一键分析并推送到微信</p>
        </div>

        <!-- 状态显示 -->
        <div class="card">
            <div class="card-title">📈 运行状态</div>
            <div class="status-grid">
                <div class="status-item {{ 'running' if status.running else ('success' if status.last_run else '') }}">
                    <span class="label">当前状态</span>
                    <span class="value" id="statusText">{{ '运行中...' if status.running else ('就绪' if status.last_run else '等待中') }}</span>
                </div>
                <div class="status-item">
                    <span class="label">上次运行</span>
                    <span class="value" id="lastRun">{{ status.last_run or '从未运行' }}</span>
                </div>
                <div class="status-item {{ 'error' if status.error else '' }}">
                    <span class="label">状态信息</span>
                    <span class="value" id="statusMsg">{{ status.error or '正常' }}</span>
                </div>
            </div>
        </div>

        <!-- 一键推送按钮 -->
        <div class="card">
            <div class="push-btn-container">
                <button class="push-btn" onclick="runAndPush()" id="btnPush" {{ 'disabled' if status.running }}>
                    {% if status.running %}
                    <span class="spinner"></span>
                    <div class="text">
                        <div>分析推送中...</div>
                        <div class="subtext">请稍候，正在处理</div>
                    </div>
                    {% else %}
                    <span class="icon">📤</span>
                    <div class="text">
                        <div>一键分析并推送</div>
                        <div class="subtext">分析所有基金并推送到微信</div>
                    </div>
                    {% endif %}
                </button>
                <button class="btn-secondary" onclick="refreshStatus()" id="btnRefresh">
                    🔄 刷新状态
                </button>
            </div>
        </div>

        <!-- 基金列表 -->
        <div class="card">
            <div class="card-title">📋 监控基金</div>
            <div class="fund-list">
                {% for fund in config.funds %}
                <span class="fund-tag">{{ fund.name }}</span>
                {% endfor %}
            </div>
        </div>

        <!-- 运行日志 -->
        <div class="card">
            <div class="card-title">📝 运行日志</div>
            <div class="log-box" id="logBox">
{% if logs %}
{% for log in logs %}
{{ log }}
{% endfor %}
{% else %}
等待操作...
{% endif %}
            </div>
        </div>

        <div class="footer">
            <p>基金研究助手 v2.0 | 数据仅供参考</p>
        </div>
    </div>

    <script>
        function addLog(message, type = 'info') {
            const logBox = document.getElementById('logBox');
            const time = new Date().toLocaleTimeString();
            logBox.innerHTML += `<span class="${type}">[${time}] ${message}</span>\\n`;
            logBox.scrollTop = logBox.scrollHeight;
        }

        function updateStatus(data) {
            document.getElementById('statusText').textContent = data.running ? '运行中...' : '就绪';
            document.getElementById('lastRun').textContent = data.last_run || '从未运行';
            document.getElementById('statusMsg').textContent = data.error || '正常';

            const btnPush = document.getElementById('btnPush');
            btnPush.disabled = data.running;

            if (data.running) {
                btnPush.innerHTML = `
                    <span class="spinner"></span>
                    <div class="text">
                        <div>分析推送中...</div>
                        <div class="subtext">请稍候，正在处理</div>
                    </div>
                `;
            } else {
                btnPush.innerHTML = `
                    <span class="icon">📤</span>
                    <div class="text">
                        <div>一键分析并推送</div>
                        <div class="subtext">分析所有基金并推送到微信</div>
                    </div>
                `;
            }
        }

        async function refreshStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateStatus(data);
                addLog('状态已刷新', 'info');
            } catch (error) {
                addLog('刷新状态失败: ' + error.message, 'error');
            }
        }

        async function runAndPush() {
            if (!confirm('确定要分析并推送到微信吗？')) return;

            addLog('开始分析并推送...', 'info');
            document.getElementById('btnPush').disabled = true;

            try {
                const response = await fetch('/api/analyze-and-push', { method: 'POST' });
                const data = await response.json();

                if (data.success) {
                    addLog('分析推送任务已启动', 'success');
                    // 开始轮询状态
                    pollStatus();
                } else {
                    addLog('启动失败: ' + data.error, 'error');
                    document.getElementById('btnPush').disabled = false;
                }
            } catch (error) {
                addLog('请求失败: ' + error.message, 'error');
                document.getElementById('btnPush').disabled = false;
            }
        }

        async function pollStatus() {
            const pollInterval = setInterval(async () => {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    updateStatus(data);

                    if (!data.running) {
                        clearInterval(pollInterval);
                        if (data.error) {
                            addLog('分析失败: ' + data.error, 'error');
                        } else {
                            addLog('分析推送完成！', 'success');
                        }
                    }
                } catch (error) {
                    console.error('轮询状态失败:', error);
                }
            }, 2000);
        }

        // 页面加载时刷新状态
        refreshStatus();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """主页"""
    return render_template_string(
        HTML_TEMPLATE,
        status=analysis_status,
        config=config,
        logs=analysis_status.get('logs', [])
    )


@app.route('/api/status')
def api_status():
    """获取状态API"""
    return jsonify({
        "running": analysis_status["running"],
        "last_run": analysis_status["last_run"],
        "error": analysis_status["error"]
    })


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """分析API"""
    if analysis_status["running"]:
        return jsonify({"success": False, "error": "分析正在进行中"})

    def run_analysis():
        analysis_status["running"] = True
        analysis_status["error"] = None
        analysis_status["logs"] = []

        try:
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 开始分析...")
            results = analyze_all_funds()
            analysis_status["last_result"] = results
            analysis_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 分析完成，共分析{len(results)}只基金")
        except Exception as e:
            analysis_status["error"] = str(e)
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 错误: {str(e)}")
        finally:
            analysis_status["running"] = False

    thread = threading.Thread(target=run_analysis)
    thread.start()

    return jsonify({"success": True, "message": "分析已开始"})


@app.route('/api/analyze-and-push', methods=['POST'])
def api_analyze_and_push():
    """分析并推送API"""
    if analysis_status["running"]:
        return jsonify({"success": False, "error": "分析正在进行中"})

    def run_analysis_and_push():
        analysis_status["running"] = True
        analysis_status["error"] = None
        analysis_status["logs"] = []

        try:
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 开始分析...")
            results = analyze_all_funds()
            analysis_status["last_result"] = results
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 分析完成，共分析{len(results)}只基金")

            # 推送
            if config.pushplus_token:
                analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 开始推送...")
                notifier = create_notifier()
                push_result = notifier.send_daily_report(results)
                analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 推送{'成功' if push_result else '失败'}")
            else:
                analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 未配置PushPlus Token，跳过推送")

            analysis_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            analysis_status["error"] = str(e)
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 错误: {str(e)}")
        finally:
            analysis_status["running"] = False

    thread = threading.Thread(target=run_analysis_and_push)
    thread.start()

    return jsonify({"success": True, "message": "分析并推送已开始"})


def run_web_app(host='0.0.0.0', port=5000, debug=False):
    """运行Web应用"""
    print(f"🚀 启动Web服务: http://localhost:{port}")
    print(f"📱 手机访问: http://你的IP地址:{port}")
    print(f"📊 控制面板: http://localhost:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_web_app(debug=True)
