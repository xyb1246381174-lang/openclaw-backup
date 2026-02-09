#!/usr/bin/env python3
"""
MBC20 Fully Automatic Mint Bot
完全自动Mint，无需人工干预
"""

import os
import time
import json
import subprocess
import random
import string
import re
from datetime import datetime

# 配置
MOLTBOOK_API_KEY = os.environ.get('MOLTBOOK_API_KEY', '${MOLTBOOK_API_KEY}')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

# 核心JSON
MINT_JSON = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}'

NUMBER_MAP = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
    'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
    'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18,
    'nineteen': 19, 'twenty': 20, 'thirty': 30, 'forty': 40,
    'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
}

def curl_post(url, data):
    """发送curl请求"""
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def extract_numbers(text):
    """提取数字"""
    text = text.lower()
    text = re.sub(r'[\[\]\{\}\<\>\(\)\^\-\+\=\_\|\/\\\.~,]', ' ', text)
    numbers = []
    for word in text.split():
        if word in NUMBER_MAP:
            numbers.append(NUMBER_MAP[word])
        elif word.isdigit():
            numbers.append(int(word))
    return numbers

def solve_captcha(challenge):
    """解决验证码"""
    numbers = extract_numbers(challenge)
    total = sum(numbers)
    time.sleep(3)  # 冷静期
    return f"{total:.2f}"

def send_telegram(msg):
    """发送Telegram消息"""
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        subprocess.run([
            "curl", "-s", "-X", "POST", url,
            "-d", f"chat_id={TELEGRAM_CHAT_ID}",
            "-d", f"text={msg}",
            "-d", "parse_mode=Markdown"
        ], capture_output=True)

def auto_mint():
    """自动Mint主函数"""
    result = "❌ Mint失败"
    nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # 1. 发送帖子
    post_data = {
        "submolt": "general",
        "title": f"Mint $CLAW #{nonce}",
        "content": f"{MINT_JSON}\n\nmbc20.xyz #{nonce}"
    }
    
    resp = curl_post("https://www.moltbook.com/api/v1/posts", post_data)
    resp_json = json.loads(resp)
    
    if not resp_json.get("success"):
        error = resp_json.get("error", "")
        if "once every" in error:
            wait = resp_json.get("retry_after_minutes", 30)
            result = f"⏰ 冷却中，还需 {wait} 分钟"
        else:
            result = f"❌ 失败: {error}"
        return result
    
    # 2. 如果需要验证码
    if resp_json.get("verification_required"):
        challenge = resp_json.get("verification", {}).get("challenge", "")
        code = resp_json.get("verification", {}).get("code", "")
        
        if challenge and code:
            answer = solve_captcha(challenge)
            verify_resp = curl_post("https://www.moltbook.com/api/v1/verify", {
                "verification_code": code,
                "answer": answer
            })
            verify_json = json.loads(verify_resp)
            
            if verify_json.get("success"):
                result = f"✅ Mint成功！获得 100 $CLAW\n⏰ {datetime.now().strftime('%H:%M:%S')}"
            else:
                result = f"❌ 验证失败"
        else:
            result = "✅ 帖子已发布"
    else:
        result = "✅ 帖子已发布"
    
    return result

def run_forever():
    """无限循环"""
    send_telegram("🚀 Fully Automatic Mint Bot 启动！\n每30分钟自动Mint并汇报。")
    
    while True:
        try:
            status = auto_mint()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            send_telegram(f"📊 {timestamp}\n{status}")
        except Exception as e:
            send_telegram(f"❌ 错误: {e}")
        
        # 等待30分钟
        for i in range(30):
            if i % 5 == 0:
                print(f"💤 等待 {30-i} 分钟...")
            time.sleep(60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        result = auto_mint()
        print(f"📊 {datetime.now()}: {result}")
    else:
        run_forever()
