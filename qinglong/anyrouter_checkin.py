#!/usr/bin/env python3
"""
AnyRouter.top 自动签到青龙脚本
适用于青龙面板定时任务执行
"""

import asyncio
import json
import os
import sys
from datetime import datetime

import httpx
from playwright.async_api import async_playwright


def ql_log(level, message):
    """青龙脚本标准日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def load_accounts():
    """从环境变量加载多账号配置"""
    accounts_str = os.getenv('ANYROUTER_ACCOUNTS')
    if not accounts_str:
        ql_log('ERROR', 'ANYROUTER_ACCOUNTS environment variable not found')
        return None

    try:
        accounts_data = json.loads(accounts_str)

        # 检查是否为数组格式
        if not isinstance(accounts_data, list):
            ql_log('ERROR', 'Account configuration must use array format [{}]')
            return None

        # 验证账号数据格式
        for i, account in enumerate(accounts_data):
            if not isinstance(account, dict):
                ql_log('ERROR', f'Account {i + 1} configuration format is incorrect')
                return None
            if 'cookies' not in account or 'api_user' not in account:
                ql_log('ERROR', f'Account {i + 1} missing required fields (cookies, api_user)')
                return None

        return accounts_data
    except Exception as e:
        ql_log('ERROR', f'Account configuration format is incorrect: {e}')
        return None


def parse_cookies(cookies_data):
    """解析 cookies 数据"""
    if isinstance(cookies_data, dict):
        return cookies_data

    if isinstance(cookies_data, str):
        cookies_dict = {}
        for cookie in cookies_data.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies_dict[key] = value
        return cookies_dict
    return {}


async def get_waf_cookies_with_playwright(account_name: str):
    """使用 Playwright 获取 WAF cookies（青龙环境优化版）"""
    ql_log('INFO', f'{account_name}: Starting browser to get WAF cookies...')

    try:
        async with async_playwright() as p:
            # 青龙环境下使用headless模式
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-gpu',
                    '--disable-extensions'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
            )
            
            page = await context.new_page()

            ql_log('INFO', f'{account_name}: Step 1: Access login page to get initial cookies...')

            await page.goto('https://anyrouter.top/login', wait_until='networkidle', timeout=30000)

            try:
                await page.wait_for_function('document.readyState === "complete"', timeout=5000)
            except Exception:
                await page.wait_for_timeout(3000)

            cookies = await page.context.cookies()

            waf_cookies = {}
            for cookie in cookies:
                if cookie['name'] in ['acw_tc', 'cdn_sec_tc', 'acw_sc__v2']:
                    waf_cookies[cookie['name']] = cookie['value']

            ql_log('INFO', f'{account_name}: Got {len(waf_cookies)} WAF cookies after step 1')

            required_cookies = ['acw_tc', 'cdn_sec_tc', 'acw_sc__v2']
            missing_cookies = [c for c in required_cookies if c not in waf_cookies]

            if missing_cookies:
                ql_log('ERROR', f'{account_name}: Missing WAF cookies: {missing_cookies}')
                await browser.close()
                return None

            ql_log('SUCCESS', f'{account_name}: Successfully got all WAF cookies')
            await browser.close()
            return waf_cookies

    except Exception as e:
        ql_log('ERROR', f'{account_name}: Error occurred while getting WAF cookies: {e}')
        return None


def get_user_info(client, headers):
    """获取用户信息"""
    try:
        response = client.get('https://anyrouter.top/api/user/self', headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_data = data.get('data', {})
                quota = round(user_data.get('quota', 0) / 500000, 2)
                used_quota = round(user_data.get('used_quota', 0) / 500000, 2)
                return f'💰 Current balance: ${quota}, Used: ${used_quota}'
    except Exception as e:
        return f'[FAIL] Failed to get user info: {str(e)[:50]}...'
    return None


async def check_in_account(account_info, account_index):
    """为单个账号执行签到操作"""
    account_name = f'Account {account_index + 1}'
    ql_log('INFO', f'Starting to process {account_name}')

    # 解析账号配置
    cookies_data = account_info.get('cookies', {})
    api_user = account_info.get('api_user', '')

    if not api_user:
        ql_log('ERROR', f'{account_name}: API user identifier not found')
        return False, None

    # 解析用户 cookies
    user_cookies = parse_cookies(cookies_data)
    if not user_cookies:
        ql_log('ERROR', f'{account_name}: Invalid configuration format')
        return False, None

    # 步骤1：获取 WAF cookies
    waf_cookies = await get_waf_cookies_with_playwright(account_name)
    if not waf_cookies:
        ql_log('ERROR', f'{account_name}: Unable to get WAF cookies')
        return False, None

    # 步骤2：使用 httpx 进行 API 请求
    client = httpx.Client(http2=True, timeout=30.0)

    try:
        # 合并 WAF cookies 和用户 cookies
        all_cookies = {**waf_cookies, **user_cookies}
        client.cookies.update(all_cookies)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://anyrouter.top/console',
            'Origin': 'https://anyrouter.top',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'new-api-user': api_user,
        }

        user_info_text = None

        user_info = get_user_info(client, headers)
        if user_info:
            ql_log('INFO', f'{account_name}: {user_info}')
            user_info_text = user_info

        ql_log('INFO', f'{account_name}: Executing check-in')

        # 更新签到请求头
        checkin_headers = headers.copy()
        checkin_headers.update({'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'})

        response = client.post('https://anyrouter.top/api/user/sign_in', headers=checkin_headers, timeout=30)

        ql_log('INFO', f'{account_name}: Response status code {response.status_code}')

        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('ret') == 1 or result.get('code') == 0 or result.get('success'):
                    ql_log('SUCCESS', f'{account_name}: Check-in successful!')
                    return True, user_info_text
                else:
                    error_msg = result.get('msg', result.get('message', 'Unknown error'))
                    ql_log('ERROR', f'{account_name}: Check-in failed - {error_msg}')
                    return False, user_info_text
            except json.JSONDecodeError:
                # 如果不是 JSON 响应，检查是否包含成功标识
                if 'success' in response.text.lower():
                    ql_log('SUCCESS', f'{account_name}: Check-in successful!')
                    return True, user_info_text
                else:
                    ql_log('ERROR', f'{account_name}: Check-in failed - Invalid response format')
                    return False, user_info_text
        else:
            ql_log('ERROR', f'{account_name}: Check-in failed - HTTP {response.status_code}')
            return False, user_info_text

    except Exception as e:
        ql_log('ERROR', f'{account_name}: Error occurred during check-in process - {str(e)[:50]}...')
        return False, user_info_text
    finally:
        client.close()


def send_notification(content):
    """发送青龙通知"""
    try:
        from ql_notify import send_notification as ql_send
        ql_send("AnyRouter签到结果", content)
    except ImportError:
        # 如果通知模块不可用，简单输出到控制台
        ql_log('INFO', 'Notification module not available, using console output')
        print("=" * 50)
        print("AnyRouter签到结果")
        print("=" * 50)
        print(content)
        print("=" * 50)
    except Exception as e:
        ql_log('ERROR', f'Failed to send notification: {e}')


async def main():
    """主函数"""
    ql_log('INFO', 'AnyRouter.top multi-account auto check-in script started (Qinglong Version)')
    ql_log('INFO', f'Execution time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

    # 加载账号配置
    accounts = load_accounts()
    if not accounts:
        ql_log('ERROR', 'Unable to load account configuration, program exits')
        sys.exit(1)

    ql_log('INFO', f'Found {len(accounts)} account configurations')

    # 为每个账号执行签到
    success_count = 0
    total_count = len(accounts)
    notification_content = []

    for i, account in enumerate(accounts):
        try:
            success, user_info = await check_in_account(account, i)
            if success:
                success_count += 1
            # 收集通知内容
            status = '✅ SUCCESS' if success else '❌ FAIL'
            account_result = f'{status} Account {i + 1}'
            if user_info:
                account_result += f'\n{user_info}'
            notification_content.append(account_result)
        except Exception as e:
            ql_log('ERROR', f'Account {i + 1} processing exception: {e}')
            notification_content.append(f'❌ FAIL Account {i + 1} exception: {str(e)[:50]}...')

    # 构建通知内容
    summary = [
        '📊 Check-in result statistics:',
        f'✅ Success: {success_count}/{total_count}',
        f'❌ Failed: {total_count - success_count}/{total_count}',
    ]

    if success_count == total_count:
        summary.append('🎉 All accounts check-in successful!')
        ql_log('SUCCESS', 'All accounts check-in successful!')
    elif success_count > 0:
        summary.append('⚠️  Some accounts check-in successful')
        ql_log('WARNING', f'{success_count}/{total_count} accounts check-in successful')
    else:
        summary.append('💥 All accounts check-in failed')
        ql_log('ERROR', 'All accounts check-in failed')

    time_info = f'⏰ Execution time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

    notify_content = '\n\n'.join([time_info, '\n'.join(notification_content), '\n'.join(summary)])

    # 发送通知
    send_notification(notify_content)

    # 设置退出码
    sys.exit(0 if success_count > 0 else 1)


def run_main():
    """运行主函数的包装函数"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        ql_log('WARNING', 'Program interrupted by user')
        sys.exit(1)
    except Exception as e:
        ql_log('ERROR', f'Error occurred during program execution: {e}')
        sys.exit(1)


if __name__ == '__main__':
    run_main()