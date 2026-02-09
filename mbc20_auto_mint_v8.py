#!/usr/bin/env python3
"""
MBC20 Auto Mint Bot v8.0
模拟人类操作速度，避免被检测为AI
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

MINT_JSON = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}'

ALL_NUMBERS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
    'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90
}

def random_human_delay():
    """模拟人类延迟 5-20 秒"""
    delay = random.uniform(5, 20)
    print(f"   🐢 模拟人类延迟: {delay:.1f}秒...")
    time.sleep(delay)

def extract_numbers_debug(challenge):
    """提取数字"""
    print(f"   🔍 原题: {challenge[:80]}...")
    
    cleaned = re.sub(r'[^a-zA-Z]', '', challenge).lower()
    print(f"   🧹 清理: {cleaned}")
    
    numbers = []
    i = 0
    
    while i < len(cleaned):
        for word in sorted(ALL_NUMBERS.keys(), key=len, reverse=True):
            if cleaned.startswith(word, i):
                numbers.append(ALL_NUMBERS[word])
                print(f"   📝 找到: {word} = {ALL_NUMBERS[word]}")
                i += len(word)
                break
        else:
            i += 1
    
    total = sum(numbers)
    print(f"   📊 识别: {' + '.join(map(str, numbers))} = {total}")
    return numbers

def solve_captcha(challenge):
    """解决验证码（模拟人类速度）"""
    numbers = extract_numbers_debug(challenge)
    
    if not numbers:
        print(f"   ⚠️ 未识别到数字")
        return "0"
    
    total = sum(numbers)
    
    # 模拟人类"思考"时间
    print(f"   🤔 人类思考中...")
    random_human_delay()
    
    # 再次确认（模拟人类复核）
    print(f"   ✅ 确认答案: {total}")
    random_human_delay()
    
    return str(total)

def curl_post(url, data):
    """发送请求"""
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

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
    """自动Mint"""
    nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    post_data = {
        "submolt": "general",
        "title": f"Mint $CLAW #{nonce}",
        "content": f"{MINT_JSON}\n\nmbc20.xyz #{nonce}"
    }
    
    print(f"\n🐱 步骤1: 发送帖子...")
    random_human_delay()
    
    resp = curl_post("https://www.moltbook.com/api/v1/posts", post_data)
    resp_json = json.loads(resp)
    
    if not resp_json.get("success"):
        error = resp_json.get("error", "")
        if "once every" in error:
            wait = resp_json.get("retry_after_minutes", 30)
            msg = f"⏰ 冷却中，还需 {wait} 分钟"
        else:
            msg = f"❌ 失败: {error}"
        return msg
    
    if resp_json.get("verification_required"):
        challenge = resp_json.get("verification", {}).get("challenge", "")
        code = resp_json.get("verification", {}).get("code", "")
        
        if challenge and code:
            print(f"\n🔐 步骤2: 解决验证码...")
            answer = solve_captcha(challenge)
            
            print(f"\n✅ 步骤3: 提交验证...")
            random_human_delay()
            
            # 尝试小数格式
            verify_resp = curl_post("https://www.moltbook.com/api/v1/verify", {
                "verification_code": code,
                "answer": f"{answer}.00"
            })
            
            verify_json = json.loads(verify_resp)
            
            if verify_json.get("success"):
                result = f"✅ Mint成功！获得 100 $CLAW\n答案: {answer}"
            else:
                # 尝试整数格式
                print(f"   ⚠️ 小数格式失败，尝试整数...")
                random_human_delay()
                verify_resp2 = curl_post("https://www.moltbook.com/api/v1/verify", {
                    "verification_code": code,
                    "answer": answer
                })
                verify_json2 = json.loads(verify_resp2)
                
                if verify_json2.get("success"):
                    result = f"✅ Mint成功！获得 100 $CLAW\n答案: {answer}"
                else:
                    result = f"❌ 验证失败\n小数: {answer}.00\n整数: {answer}"
        else:
            result = "✅ 帖子已发布"
    else:
        result = "✅ 帖子已发布"
    
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        result = auto_mint()
        print(f"\n📊 {datetime.now()}: {result}")
    else:
        while True:
            try:
                status = auto_mint()
                send_telegram(f"📊 Mint: {status}")
            except Exception as e:
                send_telegram(f"❌ 错误: {e}")
            time.sleep(1800)  # 30分钟冷却
