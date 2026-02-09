#!/usr/bin/env python3
"""
MBC20 Auto Mint Bot v9.0
专门优化验证码识别，提高成功率
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

# 完整数字映射
NUMBER_MAP = {
    # 0-9
    'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
    # 10-19
    'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
    'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
    'eighteen': 18, 'nineteen': 19,
    # 20-90
    'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
    'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
    # 100+
    'hundred': 100
}

def human_delay(min_sec=3, max_sec=15):
    """模拟人类延迟"""
    delay = random.uniform(min_sec, max_sec)
    print(f"   🐢 延迟: {delay:.1f}秒")
    time.sleep(delay)

def parse_numbers_aggressive(challenge):
    """激进版数字解析 - 尝试多种方式"""
    print(f"   🔍 解析题目: {challenge[:100]}...")
    
    # 移除所有非字母字符
    cleaned = re.sub(r'[^a-zA-Z]', '', challenge).lower()
    print(f"   🧹 清理: {cleaned}")
    
    results = []
    
    # 方法1: 从头到尾扫描
    i = 0
    while i < len(cleaned):
        matched = False
        # 从长到短尝试
        for word in sorted(NUMBER_MAP.keys(), key=len, reverse=True):
            if cleaned.startswith(word, i):
                val = NUMBER_MAP[word]
                results.append(('M1', word, val))
                i += len(word)
                matched = True
                break
        if not matched:
            i += 1
    
    # 方法2: 检查空格分隔
    words = challenge.split()
    for word in words:
        clean = re.sub(r'[^a-zA-Z]', '', word).lower()
        if clean in NUMBER_MAP:
            results.append(('M2', clean, NUMBER_MAP[clean]))
    
    # 方法3: 检查 + 号分隔
    if '+' in challenge:
        parts = challenge.split('+')
        for part in parts:
            clean = re.sub(r'[^a-zA-Z]', '', part).lower()
            if clean in NUMBER_MAP:
                results.append(('M3', clean, NUMBER_MAP[clean]))
    
    print(f"   📊 方法结果: {results}")
    return results

def calculate_best_answer(results):
    """计算最佳答案"""
    if not results:
        return None, []
    
    # 取所有找到的数字
    all_numbers = [r[2] for r in results]
    unique_numbers = list(set(all_numbers))
    
    print(f"   🔢 找到的数字: {unique_numbers}")
    
    # 尝试不同组合
    candidates = []
    
    # 组合1: 所有数字相加
    sum1 = sum(unique_numbers)
    candidates.append(('全部相加', sum1))
    
    # 组合2: 只取最大的几个
    if len(unique_numbers) > 1:
        sum2 = sum(unique_numbers[:2])
        candidates.append(('前2个相加', sum2))
    
    # 组合3: 只取最小
    if unique_numbers:
        candidates.append(('最小值', min(unique_numbers)))
        candidates.append(('最大值', max(unique_numbers)))
    
    print(f"   📝 候选答案: {candidates}")
    
    # 返回所有候选答案
    answers = [c[1] for c in candidates]
    return answers, candidates

def solve_captcha(challenge):
    """解决验证码"""
    results = parse_numbers_aggressive(challenge)
    answers, candidates = calculate_best_answer(results)
    
    if not answers:
        print(f"   ⚠️ 无法识别数字")
        return ["0"]
    
    # 返回所有候选答案
    return [str(a) for a in answers]

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
    
    print(f"\n🚀 步骤1: 发送帖子...")
    human_delay(5, 15)
    
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
                print(f"\n🔐 步骤2: 解决验证码...")
                human_delay(8, 20)  # 思考时间
                
                candidate_answers = solve_captcha(challenge)
                
                print(f"\n✅ 步骤3: 提交验证...")
                human_delay(5, 15)
                
                # 尝试所有候选答案
                success = False
                tried = []
                
                for answer in candidate_answers:
                    if answer in tried:
                        continue
                    tried.append(answer)
                    
                    print(f"   尝试答案: {answer}")
                    
                    # 尝试小数格式
                    float_ans = f"{answer}.00"
                    verify_resp = curl_post("https://www.moltbook.com/api/v1/verify", {
                        "verification_code": code,
                        "answer": float_ans
                    })
                    verify_json = json.loads(verify_resp)
                    
                    if verify_json.get("success"):
                        result = f"✅ Mint成功！获得 100 $CLAW\n答案: {answer}"
                        success = True
                        break
                    
                    human_delay(2, 5)  # 每次尝试间隔
                    
                    # 尝试整数格式
                    verify_resp2 = curl_post("https://www.moltbook.com/api/v1/verify", {
                        "verification_code": code,
                        "answer": answer
                    })
                    verify_json2 = json.loads(verify_resp2)
                    
                    if verify_json2.get("success"):
                        result = f"✅ Mint成功！获得 100 $CLAW\n答案: {answer}"
                        success = True
                        break
                
                if not success:
                    result = f"❌ 验证失败\n尝试: {tried}"
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
        print(f"\n📊 {datetime.now()}: {result}")
    else:
        while True:
            try:
                status = auto_mint()
                send_telegram(f"📊 Mint: {status}")
            except Exception as e:
                send_telegram(f"❌ 错误: {e}")
            time.sleep(1800)  # 30分钟冷却
