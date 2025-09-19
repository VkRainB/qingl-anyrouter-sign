# 🚀 青龙脚本部署验证清单

## 📋 部署前检查

### ✅ 环境准备
- [ ] 青龙面板正常运行
- [ ] Python 3.8+ 可用
- [ ] 容器有足够内存 (建议512MB+)
- [ ] 网络可访问 anyrouter.top

### ✅ 文件上传
- [ ] `anyrouter_checkin.py` - 主脚本
- [ ] `ql_notify.py` - 通知模块  
- [ ] `requirements.txt` - 依赖文件
- [ ] `install.sh` - 安装脚本
- [ ] `README.md` - 使用说明

### ✅ 权限设置
- [ ] 脚本文件有执行权限
- [ ] install.sh 有执行权限

## 🔧 安装验证

### ✅ 依赖安装
```bash
# 检查依赖安装状态
pip3 list | grep -E "(httpx|playwright)"

# 预期输出包含:
# httpx         x.x.x
# playwright    x.x.x
```

### ✅ 浏览器安装  
```bash
# 检查 Playwright 浏览器
playwright --version
# 预期输出: Version x.x.x

# 检查 Chromium 安装
ls ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome
# 预期：文件存在
```

### ✅ 系统依赖
```bash
# 检查关键系统库
ldd ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome | grep -E "(not found)"
# 预期：无 "not found" 输出
```

## 🔧 配置验证

### ✅ 环境变量配置
```bash
# 检查主要环境变量
echo $ANYROUTER_ACCOUNTS
# 预期：JSON格式的账号配置

# 验证JSON格式
echo $ANYROUTER_ACCOUNTS | python3 -m json.tool
# 预期：格式化的JSON输出，无错误
```

### ✅ 账号配置验证
- [ ] 至少配置1个账号
- [ ] 每个账号包含 `cookies` 和 `api_user`
- [ ] cookies 格式正确 (字符串或对象)
- [ ] api_user 为有效的用户ID

### ✅ 通知配置 (可选)
- [ ] 至少配置一种通知方式
- [ ] Webhook 地址格式正确
- [ ] Token/Key 有效

## 🧪 功能测试

### ✅ 语法检查
```bash
cd /ql/scripts/anyrouter
python3 syntax_check.py
# 预期：所有检查通过 ✅
```

### ✅ 环境测试
```bash  
cd /ql/scripts/anyrouter
python3 qinglong_test.py
# 预期：大部分测试通过，生成诊断报告
```

### ✅ 通知测试
```bash
cd /ql/scripts/anyrouter  
python3 -c "from ql_notify import send_notification; send_notification('测试', '这是测试通知')"
# 预期：通知发送成功或控制台输出
```

## ⏰ 定时任务配置

### ✅ 任务创建
- [ ] 任务名称: `AnyRouter自动签到`
- [ ] 命令: `python3 /ql/scripts/anyrouter/anyrouter_checkin.py`  
- [ ] 定时规则: `0 8 * * *` (每天上午8点)
- [ ] 状态: 启用

### ✅ 权限检查
```bash
# 检查脚本文件权限
ls -la /ql/scripts/anyrouter/anyrouter_checkin.py
# 预期：有读取权限

# 检查Python路径
which python3
# 预期：返回有效路径
```

## 🚀 运行测试

### ✅ 手动执行
```bash
cd /ql/scripts/anyrouter
python3 anyrouter_checkin.py
```

### ✅ 预期输出检查
- [ ] 日志格式: `[时间] [级别] 信息`
- [ ] 显示账号数量  
- [ ] 显示处理过程
- [ ] 显示最终结果统计
- [ ] 发送通知 (如已配置)

### ✅ 成功标识
```
[时间] [SUCCESS] All accounts check-in successful!
```

### ✅ 错误排查
常见问题检查：
- [ ] 401错误 → cookies过期，需重新获取
- [ ] 超时错误 → 网络问题或服务器压力
- [ ] 依赖错误 → 检查包安装状态  
- [ ] 权限错误 → 检查文件权限设置

## 📊 监控验证

### ✅ 日志监控
```bash  
# 查看最近的任务日志
tail -f /ql/logs/任务名称.log

# 查看特定日期日志
grep "$(date +%Y-%m-%d)" /ql/logs/任务名称.log
```

### ✅ 成功指标
- [ ] 任务正常启动
- [ ] 浏览器成功启动
- [ ] WAF cookies 获取成功
- [ ] 签到请求成功  
- [ ] 通知发送成功

### ✅ 性能监控
- [ ] 内存使用正常 (<512MB)
- [ ] CPU使用合理
- [ ] 执行时间合理 (<5分钟/账号)
- [ ] 网络请求成功率高

## 🔧 故障排除

### ❌ 安装失败
```bash
# 重新安装依赖
pip3 uninstall httpx playwright -y
pip3 install -r requirements.txt

# 重新安装浏览器
playwright uninstall chromium  
playwright install chromium
```

### ❌ 运行失败
```bash
# 检查详细错误
python3 anyrouter_checkin.py 2>&1 | tee debug.log

# 检查环境
python3 qinglong_test.py > diagnostic.log 2>&1
```

### ❌ 通知失败
```bash
# 测试网络连通性
curl -I https://qyapi.weixin.qq.com  # 企业微信
curl -I https://oapi.dingtalk.com   # 钉钉

# 测试通知配置  
python3 -c "import os; print(os.getenv('WEIXIN_WEBHOOK'))"
```

## ✅ 部署完成确认

当所有检查项都通过时：
- [x] 环境配置正确
- [x] 依赖安装完成
- [x] 脚本运行正常
- [x] 定时任务启用
- [x] 通知系统可用

🎉 **恭喜！AnyRouter 青龙脚本部署成功！**

---

💡 **提示**: 建议保存此清单，用于日常维护和问题排查。