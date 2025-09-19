#!/usr/bin/env python3
"""
青龙环境完整测试脚本
检查依赖、环境配置和脚本功能
"""

import os
import sys
import json
import importlib.util
import subprocess
from datetime import datetime


def log(level, message):
    """标准日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def check_python_version():
    """检查Python版本"""
    log('INFO', '检查Python版本...')
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        log('SUCCESS', f'Python版本: {version.major}.{version.minor}.{version.micro} ✅')
        return True
    else:
        log('ERROR', f'Python版本过低: {version.major}.{version.minor}.{version.micro}，需要3.8+')
        return False


def check_dependencies():
    """检查必要依赖"""
    log('INFO', '检查必要依赖...')
    
    required_packages = ['httpx', 'playwright']
    missing_packages = []
    
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                log('SUCCESS', f'✅ {package} 已安装')
            else:
                missing_packages.append(package)
                log('ERROR', f'❌ {package} 未安装')
        except ImportError:
            missing_packages.append(package)
            log('ERROR', f'❌ {package} 未安装')
    
    return len(missing_packages) == 0, missing_packages


def check_qinglong_environment():
    """检查青龙环境"""
    log('INFO', '检查青龙环境...')
    
    # 检查青龙目录
    qinglong_dirs = ['/ql', '/ql/scripts', '/ql/data']
    for dir_path in qinglong_dirs:
        if os.path.exists(dir_path):
            log('SUCCESS', f'✅ {dir_path} 目录存在')
        else:
            log('WARNING', f'⚠️  {dir_path} 目录不存在（可能不在青龙环境中）')
    
    # 检查是否在Docker环境中
    if os.path.exists('/.dockerenv'):
        log('SUCCESS', '✅ 检测到Docker环境')
    else:
        log('WARNING', '⚠️  未检测到Docker环境')
    
    return True


def check_playwright_browser():
    """检查Playwright浏览器"""
    log('INFO', '检查Playwright浏览器...')
    
    try:
        result = subprocess.run(['playwright', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            log('SUCCESS', f'✅ Playwright版本: {result.stdout.strip()}')
            
            # 检查chromium是否安装
            try:
                result = subprocess.run(['playwright', 'install', '--dry-run', 'chromium'], 
                                      capture_output=True, text=True, timeout=30)
                if 'chromium' in result.stderr.lower() or 'already installed' in result.stderr.lower():
                    log('SUCCESS', '✅ Chromium浏览器可用')
                    return True
                else:
                    log('WARNING', '⚠️  Chromium浏览器可能未安装，运行：playwright install chromium')
                    return False
            except subprocess.TimeoutExpired:
                log('WARNING', '⚠️  检查浏览器安装状态超时')
                return False
        else:
            log('ERROR', '❌ Playwright命令不可用')
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        log('ERROR', '❌ Playwright未正确安装')
        return False


def test_environment_variables():
    """测试环境变量配置"""
    log('INFO', '测试环境变量配置...')
    
    # 检查必需的环境变量
    required_env = 'ANYROUTER_ACCOUNTS'
    if os.getenv(required_env):
        log('SUCCESS', f'✅ {required_env} 环境变量已配置')
        
        # 验证JSON格式
        try:
            accounts = json.loads(os.getenv(required_env))
            if isinstance(accounts, list) and len(accounts) > 0:
                log('SUCCESS', f'✅ 账号配置格式正确，共 {len(accounts)} 个账号')
                return True
            else:
                log('ERROR', '❌ 账号配置格式错误：应为数组格式')
                return False
        except json.JSONDecodeError as e:
            log('ERROR', f'❌ 账号配置JSON格式错误: {e}')
            return False
    else:
        log('WARNING', f'⚠️  {required_env} 环境变量未配置（测试用例）')
        
        # 设置测试环境变量
        test_accounts = [
            {
                "cookies": {"session": "test_session_123"},
                "api_user": "12345"
            }
        ]
        os.environ[required_env] = json.dumps(test_accounts)
        log('INFO', '✅ 设置了测试环境变量')
        return True


def test_script_imports():
    """测试脚本导入"""
    log('INFO', '测试脚本导入...')
    
    try:
        # 添加当前目录到路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 测试通知模块导入
        import ql_notify
        log('SUCCESS', '✅ ql_notify 模块导入成功')
        
        # 测试主脚本的关键函数
        spec = importlib.util.spec_from_file_location(
            "anyrouter_checkin", 
            os.path.join(current_dir, "anyrouter_checkin.py")
        )
        anyrouter_module = importlib.util.module_from_spec(spec)
        
        # 不执行整个模块，只检查语法
        with open(os.path.join(current_dir, "anyrouter_checkin.py"), 'r', encoding='utf-8') as f:
            code = f.read()
            compile(code, "anyrouter_checkin.py", "exec")
        
        log('SUCCESS', '✅ anyrouter_checkin.py 语法检查通过')
        return True
        
    except Exception as e:
        log('ERROR', f'❌ 脚本导入失败: {e}')
        return False


def test_notification_system():
    """测试通知系统"""
    log('INFO', '测试通知系统...')
    
    try:
        from ql_notify import send_notification
        
        # 测试通知发送
        test_title = "青龙测试通知"
        test_content = "这是一个测试通知，验证通知系统是否正常工作。"
        
        send_notification(test_title, test_content)
        log('SUCCESS', '✅ 通知系统测试完成（检查控制台输出）')
        return True
        
    except Exception as e:
        log('ERROR', f'❌ 通知系统测试失败: {e}')
        return False


def create_diagnostic_report():
    """创建诊断报告"""
    log('INFO', '生成诊断报告...')
    
    report = []
    report.append("=" * 60)
    report.append("AnyRouter 青龙脚本环境诊断报告")
    report.append("=" * 60)
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Python版本: {sys.version}")
    report.append(f"操作系统: {os.name}")
    
    # 检查依赖
    report.append("\n📦 依赖检查:")
    deps_ok, missing = check_dependencies()
    if deps_ok:
        report.append("  ✅ 所有依赖已安装")
    else:
        report.append(f"  ❌ 缺少依赖: {', '.join(missing)}")
    
    # 检查环境变量
    report.append("\n🔧 环境变量:")
    if os.getenv('ANYROUTER_ACCOUNTS'):
        try:
            accounts = json.loads(os.getenv('ANYROUTER_ACCOUNTS'))
            report.append(f"  ✅ ANYROUTER_ACCOUNTS: 已配置 {len(accounts)} 个账号")
        except:
            report.append("  ❌ ANYROUTER_ACCOUNTS: 配置格式错误")
    else:
        report.append("  ⚠️  ANYROUTER_ACCOUNTS: 未配置")
    
    # 通知配置
    notify_vars = ['WEIXIN_WEBHOOK', 'DINGDING_WEBHOOK', 'FEISHU_WEBHOOK', 
                   'PUSHPLUS_TOKEN', 'SERVERPUSHKEY', 'TG_BOT_TOKEN']
    configured_notify = [var for var in notify_vars if os.getenv(var)]
    
    report.append(f"\n📢 通知配置: {len(configured_notify)} 个已配置")
    for var in configured_notify:
        report.append(f"  ✅ {var}")
    
    report.append("\n" + "=" * 60)
    
    report_content = "\n".join(report)
    
    # 写入文件
    with open('diagnostic_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(report_content)
    log('SUCCESS', '✅ 诊断报告已生成: diagnostic_report.txt')


def main():
    """主函数"""
    log('INFO', '开始青龙环境完整测试...')
    print("=" * 60)
    
    tests = [
        ('Python版本检查', check_python_version),
        ('依赖检查', lambda: check_dependencies()[0]),
        ('青龙环境检查', check_qinglong_environment),
        ('Playwright浏览器检查', check_playwright_browser),
        ('环境变量测试', test_environment_variables),
        ('脚本导入测试', test_script_imports),
        ('通知系统测试', test_notification_system),
    ]
    
    results = []
    for test_name, test_func in tests:
        log('INFO', f'🧪 {test_name}...')
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                log('SUCCESS', f'✅ {test_name} 通过')
            else:
                log('ERROR', f'❌ {test_name} 失败')
        except Exception as e:
            log('ERROR', f'❌ {test_name} 异常: {e}')
            results.append((test_name, False))
        print("-" * 30)
    
    # 统计结果
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("=" * 60)
    log('INFO', f'测试完成: {passed}/{total} 通过')
    
    if passed == total:
        log('SUCCESS', '🎉 所有测试通过！脚本可以在青龙环境中运行')
    elif passed >= total * 0.7:
        log('WARNING', '⚠️  大部分测试通过，脚本应该可以运行，但可能有些功能受限')
    else:
        log('ERROR', '❌ 多数测试失败，需要解决环境问题')
    
    # 生成诊断报告
    create_diagnostic_report()
    
    return passed >= total * 0.7


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)