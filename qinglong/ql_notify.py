"""
青龙专用简化通知系统
支持青龙面板常用的通知方式
"""

import os
from datetime import datetime
import httpx


def ql_log(level, message):
    """青龙脚本标准日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


class QinglongNotifier:
    """青龙专用通知器"""
    
    def __init__(self):
        # 企业微信通知
        self.weixin_webhook = os.getenv('WEIXIN_WEBHOOK')
        # 钉钉通知
        self.dingding_webhook = os.getenv('DINGDING_WEBHOOK')
        # 飞书通知
        self.feishu_webhook = os.getenv('FEISHU_WEBHOOK')
        # PushPlus通知
        self.pushplus_token = os.getenv('PUSHPLUS_TOKEN')
        # Server酱通知
        self.server_push_key = os.getenv('SERVERPUSHKEY')
        # Telegram通知
        self.telegram_bot_token = os.getenv('TG_BOT_TOKEN')
        self.telegram_user_id = os.getenv('TG_USER_ID')

    def send_wecom(self, title: str, content: str):
        """发送企业微信通知"""
        if not self.weixin_webhook:
            return False, "企业微信Webhook未配置"

        try:
            data = {
                'msgtype': 'text',
                'text': {
                    'content': f"🔔 {title}\n\n{content}"
                }
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.weixin_webhook, json=data)
                if response.status_code == 200:
                    return True, "企业微信通知发送成功"
                else:
                    return False, f"企业微信通知发送失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"企业微信通知发送异常: {e}"

    def send_dingtalk(self, title: str, content: str):
        """发送钉钉通知"""
        if not self.dingding_webhook:
            return False, "钉钉Webhook未配置"

        try:
            data = {
                'msgtype': 'text',
                'text': {
                    'content': f"🔔 {title}\n\n{content}"
                }
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.dingding_webhook, json=data)
                if response.status_code == 200:
                    return True, "钉钉通知发送成功"
                else:
                    return False, f"钉钉通知发送失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"钉钉通知发送异常: {e}"

    def send_feishu(self, title: str, content: str):
        """发送飞书通知"""
        if not self.feishu_webhook:
            return False, "飞书Webhook未配置"

        try:
            data = {
                'msg_type': 'text',
                'content': {
                    'text': f"🔔 {title}\n\n{content}"
                }
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(self.feishu_webhook, json=data)
                if response.status_code == 200:
                    return True, "飞书通知发送成功"
                else:
                    return False, f"飞书通知发送失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"飞书通知发送异常: {e}"

    def send_pushplus(self, title: str, content: str):
        """发送PushPlus通知"""
        if not self.pushplus_token:
            return False, "PushPlus Token未配置"

        try:
            data = {
                'token': self.pushplus_token,
                'title': title,
                'content': content.replace('\n', '<br>'),
                'template': 'html'
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post('http://www.pushplus.plus/send', json=data)
                if response.status_code == 200:
                    return True, "PushPlus通知发送成功"
                else:
                    return False, f"PushPlus通知发送失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"PushPlus通知发送异常: {e}"

    def send_server_chan(self, title: str, content: str):
        """发送Server酱通知"""
        if not self.server_push_key:
            return False, "Server酱SendKey未配置"

        try:
            data = {
                'title': title,
                'desp': content
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(f'https://sctapi.ftqq.com/{self.server_push_key}.send', data=data)
                if response.status_code == 200:
                    return True, "Server酱通知发送成功"
                else:
                    return False, f"Server酱通知发送失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Server酱通知发送异常: {e}"

    def send_telegram(self, title: str, content: str):
        """发送Telegram通知"""
        if not self.telegram_bot_token or not self.telegram_user_id:
            return False, "Telegram配置不完整"

        try:
            message = f"🔔 {title}\n\n{content}"
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_user_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=data)
                if response.status_code == 200:
                    return True, "Telegram通知发送成功"
                else:
                    return False, f"Telegram通知发送失败: HTTP {response.status_code}"
        except Exception as e:
            return False, f"Telegram通知发送异常: {e}"

    def send_all(self, title: str, content: str):
        """发送所有已配置的通知"""
        notifications = [
            ('企业微信', self.send_wecom),
            ('钉钉', self.send_dingtalk),
            ('飞书', self.send_feishu),
            ('PushPlus', self.send_pushplus),
            ('Server酱', self.send_server_chan),
            ('Telegram', self.send_telegram)
        ]

        success_count = 0
        total_configured = 0

        for name, send_func in notifications:
            try:
                success, message = send_func(title, content)
                if "未配置" not in message:
                    total_configured += 1
                    if success:
                        success_count += 1
                        ql_log('SUCCESS', f'{name}: {message}')
                    else:
                        ql_log('ERROR', f'{name}: {message}')
            except Exception as e:
                ql_log('ERROR', f'{name}: 发送异常 - {e}')

        if total_configured == 0:
            ql_log('WARNING', '未配置任何通知方式，仅控制台输出')
            print("\n" + "="*60)
            print(f"📢 {title}")
            print("="*60)
            print(content)
            print("="*60)
        else:
            ql_log('INFO', f'通知发送完成: {success_count}/{total_configured}')


# 全局通知器实例
notifier = QinglongNotifier()


def send_notification(title: str, content: str):
    """发送通知的便捷函数"""
    notifier.send_all(title, content)