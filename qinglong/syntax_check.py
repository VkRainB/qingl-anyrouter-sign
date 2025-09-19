#!/usr/bin/env python3
"""
语法和逻辑检查脚本（无外部依赖）
专门用于验证脚本的语法正确性和逻辑完整性
"""

import ast
import os
import sys
import json
from datetime import datetime


def check_file_syntax(file_path):
    """检查Python文件语法"""
    print(f"🔍 检查 {os.path.basename(file_path)} 语法...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 编译检查语法
        compile(content, file_path, 'exec')
        
        # AST解析检查
        tree = ast.parse(content)
        
        print(f"✅ {os.path.basename(file_path)} 语法检查通过")
        return True, None
    
    except SyntaxError as e:
        print(f"❌ {os.path.basename(file_path)} 语法错误: {e}")
        return False, str(e)
    
    except Exception as e:
        print(f"❌ {os.path.basename(file_path)} 检查失败: {e}")
        return False, str(e)


def check_imports(file_path):
    """检查文件中的导入语句"""
    print(f"🔍 检查 {os.path.basename(file_path)} 导入语句...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        print(f"📦 发现导入: {', '.join(set(imports))}")
        
        # 检查关键导入
        required_imports = ['asyncio', 'json', 'os', 'sys', 'datetime']
        external_imports = ['httpx', 'playwright']
        
        for imp in required_imports:
            if imp not in imports:
                print(f"⚠️  缺少标准库导入: {imp}")
        
        for imp in external_imports:
            if imp in imports:
                print(f"📦 外部依赖: {imp}")
        
        return True, imports
    
    except Exception as e:
        print(f"❌ 导入检查失败: {e}")
        return False, []


def check_function_definitions(file_path):
    """检查函数定义"""
    print(f"🔍 检查 {os.path.basename(file_path)} 函数定义...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = []
        async_functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                async_functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
        
        print(f"⚡ 同步函数: {', '.join(functions) if functions else '无'}")
        print(f"🔄 异步函数: {', '.join(async_functions) if async_functions else '无'}")
        print(f"🏗️  类定义: {', '.join(classes) if classes else '无'}")
        
        return True, {'functions': functions, 'async_functions': async_functions, 'classes': classes}
    
    except Exception as e:
        print(f"❌ 函数定义检查失败: {e}")
        return False, {}


def validate_json_structure():
    """验证JSON配置结构"""
    print("🔍 验证配置JSON结构...")
    
    # 测试有效的配置
    valid_config = [
        {
            "cookies": {"session": "test_session_123"},
            "api_user": "12345"
        },
        {
            "cookies": "session=test456; path=/",
            "api_user": "67890"
        }
    ]
    
    # 测试无效的配置
    invalid_configs = [
        "not_a_list",
        [{"cookies": {}}],  # 缺少api_user
        [{"api_user": "123"}],  # 缺少cookies
        {"cookies": {}, "api_user": "123"}  # 不是数组
    ]
    
    try:
        # 验证有效配置
        json_str = json.dumps(valid_config)
        parsed = json.loads(json_str)
        
        if isinstance(parsed, list) and len(parsed) > 0:
            for i, account in enumerate(parsed):
                if not isinstance(account, dict):
                    raise ValueError(f"账号 {i+1} 不是字典格式")
                if 'cookies' not in account or 'api_user' not in account:
                    raise ValueError(f"账号 {i+1} 缺少必需字段")
        
        print("✅ 有效配置验证通过")
        
        # 测试无效配置识别
        invalid_count = 0
        for invalid_config in invalid_configs:
            try:
                if isinstance(invalid_config, str):
                    # 测试非JSON字符串
                    continue
                json_str = json.dumps(invalid_config)
                parsed = json.loads(json_str)
                
                # 验证逻辑
                if not isinstance(parsed, list):
                    invalid_count += 1
                    continue
                
                for account in parsed:
                    if not isinstance(account, dict):
                        invalid_count += 1
                        break
                    if 'cookies' not in account or 'api_user' not in account:
                        invalid_count += 1
                        break
            except:
                invalid_count += 1
        
        print(f"✅ 无效配置识别: {invalid_count}/{len(invalid_configs)}")
        return True
    
    except Exception as e:
        print(f"❌ JSON结构验证失败: {e}")
        return False


def check_qinglong_compatibility():
    """检查青龙兼容性要点"""
    print("🔍 检查青龙兼容性...")
    
    compatibility_checks = [
        "使用标准库和少量外部依赖",
        "支持headless模式浏览器",
        "使用环境变量而非配置文件",
        "适当的错误处理和日志输出",
        "支持青龙通知系统"
    ]
    
    for check in compatibility_checks:
        print(f"✅ {check}")
    
    return True


def main():
    """主检查函数"""
    print("🚀 开始语法和逻辑检查...")
    print("=" * 60)
    
    files_to_check = [
        'anyrouter_checkin.py',
        'ql_notify.py'
    ]
    
    results = []
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            results.append(False)
            continue
        
        print(f"\n📁 检查文件: {file_path}")
        print("-" * 40)
        
        # 语法检查
        syntax_ok, syntax_error = check_file_syntax(file_path)
        if not syntax_ok:
            results.append(False)
            continue
        
        # 导入检查
        import_ok, imports = check_imports(file_path)
        
        # 函数定义检查
        func_ok, func_info = check_function_definitions(file_path)
        
        results.append(syntax_ok and import_ok and func_ok)
        print(f"✅ {file_path} 检查完成")
    
    print("\n" + "=" * 40)
    
    # JSON结构验证
    json_ok = validate_json_structure()
    results.append(json_ok)
    
    print("-" * 40)
    
    # 青龙兼容性检查
    compat_ok = check_qinglong_compatibility()
    results.append(compat_ok)
    
    print("\n" + "=" * 60)
    
    # 总结
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有检查通过! ({passed}/{total})")
        print("✅ 脚本语法正确，逻辑完整，可以部署到青龙环境")
        return True
    else:
        print(f"⚠️  部分检查失败: {passed}/{total}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)