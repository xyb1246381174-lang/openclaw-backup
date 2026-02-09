#!/usr/bin/env python3
"""
MBC20 Auto Mint Bot v3.0
自动每30分钟 mint $CLAW 代币
mint完成后自动发送消息到Telegram汇报
"""

import os
import time
import json
import subprocess
import random
import string
import re
from datetime import datetime

# 配置 - 从环境变量读取
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
MOLTBOOK_API_KEY = os.environ.get('MOLTBOOK_API_KEY', '${MOLTBOOK_API_KEY}')

# 核心 JSON 模板
MINT_JSON_CORE = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}'

# 数字映射
NUMBER_MAP = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
    'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
}

def generate_nonce(length=6):
    """生成随机nonce"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_mint_content():
    """创建Mint内容"""
    nonce = generate_nonce()
    content = f"{MINT_JSON_CORE}\n\nmbc20.xyz #{nonce}"
    title = f"Mint $CLAW #{nonce}"
    return title, content

def extract_numbers(challenge):
    """从验证码提取数字"""
    text = challenge.lower()
    text = re.sub(r'[\[\]\{\}\<\>\(\)\^\-\+\=\_\|\/\\\.~,]', ' ', text)
    words = text.split()
    
    numbers = []
    for word in words:
        word = word.strip()
        if word in NUMBER_MAP:
            numbers.append(NUMBER_MAP[word])
        elif word.isdigit():
            numbers.append(int(word))
    
    return numbers

def solve_captcha(challenge):
    """解决验证码（防错版）"""
    print(f"📝 验证码: {challenge[:50]}...")
    
    # 提取数字
    time.sleep(3)
    numbers = extract_numbers(challenge)
    print(f"📊 数字: {numbers}")
    
    # 计算
    time.sleep(3)
    total = sum(numbers)
    print(f"🧮 计算: {' + '.join(map(str, numbers))} = {total}")
    
    # 验证
    time.sleep(3)
    if sum(numbers) != total:
        total = sum(numbers)
    
    answer = f"{total:.2f}"
    print(f"✅ 答案: {answer}")
    
    # 冷静期
    time.sleep(3)
    
    return answer

def post_to_moltbook(content, title):
    """发帖到Moltbook"""
    url = "https://www.moltbook.com/api/v1/posts"
    data = {
        "submolt": "general",
        "title": title,
        "content": content
    }
    
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def verify_post(code, answer):
    """验证帖子"""
    url = "https://www.moltbook.com/api/v1/verify"
    data = {
        "verification_code": code,
        "answer": answer
    }
    
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def send_telegram_message(message):
    """发送Telegram消息"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"📱 Telegram通知: {message}")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-d", f"chat_id={TELEGRAM_CHAT_ID}",
        "-d", f"text={message}",
        "-d", "parse_mode=Markdown"
    ]
    
    subprocess.run(cmd, capture_output=True)

def mint_once():
    """执行一次Mint"""
    print(f"\n{'='*50}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🪙 Mint $CLAW")
    print(f"{'='*50}")
    
    title, content = create_mint_content()
    print(f"📝 标题: {title}")
    
    response = post_to_moltbook(content, title)
    
    try:
        resp_json = json.loads(response)
        
        # 检查是否成功创建帖子
        if resp_json.get("success"):
            # 检查是否需要验证码
            if resp_json.get("verification_required"):
                challenge = resp_json.get("verification", {}).get("challenge", "")
                code = resp_json.get("verification", {}).get("code", "")
                
                if challenge and code:
                    answer = solve_captcha(challenge)
                    verify_result = verify_post(code, answer)
                    
                    verify_json = json.loads(verify_result)
                    if verify_json.get("success"):
                        msg = f"✅ 成功！Mint $CLAW 完成！\n时间: {datetime.now().strftime('%H:%M:%S')}\n答案: {answer}"
                        print(msg)
                        send_telegram_message(msg)
                        return True
                    else:
                        msg = f"❌ 验证失败: {verify_json.get('error', 'Unknown')}"
                        print(msg)
                        send_telegram_message(msg)
                        return False
            else:
                msg = f"✅ 帖子已发布（无需验证）\n时间: {datetime.now().strftime('%H:%M:%S')}"
                print(msg)
                send_telegram_message(msg)
                return True
        else:
            error = resp_json.get("error", "Unknown")
            if "once every" in error:
                msg = f"⏰ 冷却中: {resp_json.get('hint', '')}"
                print(msg)
                send_telegram_message(msg)
            else:
                msg = f"❌ 失败: {error}"
                print(msg)
                send_telegram_message(msg)
            return False
        
    except Exception as e:
        msg = f"❌ 错误: {e}"
        print(msg)
        send_telegram_message(msg)
        return False

def auto_mint_loop(interval_minutes=30, count=None):
    """自动Mint循环"""
    print("🚀 MBC20 Auto Mint Bot v3.0 启动")
    print(f"⏱️ 间隔: {interval_minutes} 分钟")
    print("📱 完成会自动通知您")
    print("="*50)
    
    sent_count = 0
    
    while True:
        success = mint_once()
        if success:
            sent_count += 1
        
        if count and sent_count >= count:
            msg = f"🎉 完成！共 mint {sent_count} 次"
            print(msg)
            send_telegram_message(msg)
            break
        
        print(f"\n💤 等待 {interval_minutes} 分钟...")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            mint_once()
        else:
            interval = int(sys.argv[1])
            count = int(sys.argv[2]) if len(sys.argv) > 2 else None
            auto_mint_loop(interval, count)
    else:
        # 默认：每30分钟mint一次，无限循环
        auto_mint_loop(30)
