#!/usr/bin/env python3
"""
MBC20 Auto Mint Bot v6.0
智能数字匹配
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
MOLTBOOK_API_KEY = os.environ.get('MOLTBOOK_API_KEY', 'moltbook_sk_jQF9CfSCHTUm8TcEPvIFQ0P0Fbo6s8tU')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

MINT_JSON = '{"p":"mbc-20","op":"mint","tick":"CLAW","amt":"100"}'

# 数字关键词
NUMBER_KEYWORDS = {
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19, 'twenty': 20, 'thirty': 30,
    'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
    'eighty': 80, 'ninety': 90
}

def extract_numbers_smart(challenge):
    """智能提取数字"""
    print(f"   🔍 解析: {challenge[:60]}...")
    
    # 预处理：移除所有非字母字符，合并成一个长字符串
    cleaned = re.sub(r'[^a-zA-Z]', '', challenge).lower()
    print(f"   🧹 清理后: {cleaned}")
    
    numbers = []
    i = 0
    
    while i < len(cleaned):
        found = False
        
        # 检查所有可能的数字词（从长到短匹配）
        for num_word in sorted(NUMBER_KEYWORDS.keys(), key=len, reverse=True):
            if cleaned.startswith(num_word, i):
                value = NUMBER_KEYWORDS[num_word]
                numbers.append(value)
                print(f"   📝 找到: {num_word} = {value}")
                i += len(num_word)
                found = True
                break
        
        if not found:
            i += 1  # 跳过无法识别的字符
    
    total = sum(numbers)
    print(f"   📊 结果: {numbers} = {total}")
    return numbers

def solve_captcha(challenge):
    numbers = extract_numbers_smart(challenge)
    if not numbers:
        return "0"
    
    total = sum(numbers)
    time.sleep(3)  # 冷静期
    
    print(f"   ✅ 最终答案: {total}")
    return str(total)

def curl_post(url, data):
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {MOLTBOOK_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def send_telegram(msg):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        subprocess.run([
            "curl", "-s", "-X", "POST", url,
            "-d", f"chat_id={TELEGRAM_CHAT_ID}",
            "-d", f"text={msg}",
            "-d", "parse_mode=Markdown"
        ], capture_output=True)

def auto_mint():
    nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    post_data = {
        "submolt": "general",
        "title": f"Mint $CLAW #{nonce}",
        "content": f"{MINT_JSON}\n\nmbc20.xyz #{nonce}"
    }
    
    resp = curl_post("https://www.moltbook.com/api/v1/posts", post_data)
    
    try:
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
                answer = solve_captcha(challenge)
                
                verify_resp = curl_post("https://www.moltbook.com/api/v1/verify", {
                    "verification_code": code,
                    "answer": answer
                })
                
                verify_json = json.loads(verify_resp)
                
                if verify_json.get("success"):
                    result = f"✅ Mint成功！获得 100 $CLAW\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                else:
                    result = f"❌ 验证失败: {answer}"
            else:
                result = "✅ 帖子已发布"
        else:
            result = "✅ 帖子已发布"
        
        return result
        
    except Exception as e:
        return f"❌ 错误: {e}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        result = auto_mint()
        print(f"📊 {datetime.now()}: {result}")
    else:
        while True:
            try:
                status = auto_mint()
                send_telegram(f"📊 Mint状态: {status}")
            except Exception as e:
                send_telegram(f"❌ 错误: {e}")
            time.sleep(1800)
