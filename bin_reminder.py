import datetime
import requests
import json
from zoneinfo import ZoneInfo

# ================= 1. 配置区 =================

# WxPusher 配置
APP_TOKEN = "AT_5KmJe1AVfGI7zrN3DX8EiS74Bk9GuqbL"  

TOPIC_IDS = [47113]  # 把这里的 12345 换成你刚才创建的主题ID (注意是数字，不要加引号)

# 垃圾桶日期配置
# 你的收垃圾日是星期几？(0=星期一, 1=星期二, 2=星期三, 3=星期四, 4=星期五, 5=星期六, 6=星期日)
# 请务必修改为你家实际收垃圾的星期
COLLECTION_DAY = 4  

# 设定一个已知的【黄桶日】作为基准日期 (年, 月, 日)
# 程序会通过计算明天距离这个日期的周数差，来判断推红桶还是黄桶
KNOWN_YELLOW_DATE = datetime.date(2026, 9, 24) 

# ================= 2. 逻辑区 =================

def get_bins_for_tomorrow(today):
    tomorrow = today + datetime.timedelta(days=1)
    
    # 检查明天是不是收垃圾的日子
    if tomorrow.weekday() != COLLECTION_DAY:
        return None
        
    # 计算明天距离基准日期过了多少个完整的周
    delta_days = (tomorrow - KNOWN_YELLOW_DATE).days
    delta_weeks = delta_days // 7
    
    # 根据周数的奇偶性判断 (偶数周推黄桶，奇数周推红桶)
    if delta_weeks % 2 == 0:
        return "🟢 绿桶 (厨余/花园) \n🟡 黄桶 (可回收物)"
    else:
        return "🟢 绿桶 (厨余/花园) \n🔴 红桶 (一般生活垃圾)"


def send_wx_notification(bins_info):
    url = "https://wxpusher.zjiecode.com/api/send/message"
    
    # 使用 Markdown 格式，并显式保留空的 uids 数组以符合严格接口规范
    payload = {
        "appToken": APP_TOKEN,
        "content": f"### 🗑️ 基督城垃圾收集提醒\n\n**明天是收垃圾日！**\n\n请在今晚把以下垃圾桶推到马路边（桶间距保持50厘米）：\n\n**{bins_info}**",
        "summary": "🗑️ 明天该推垃圾桶啦！查看是哪两个桶", 
        "contentType": 3, 
        "topicIds": TOPIC_IDS,
        "uids": [] 
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        result = response.json()
        if result.get("code") == 1000:
            print("微信推送成功！")
        else:
            print(f"微信推送失败：{result.get('msg')}")
    except Exception as e:
        print(f"请求发生异常：{e}")

# ================= 3. 运行区 =================

if __name__ == "__main__":
    # 强制获取新西兰当前的准确时间，避免 GitHub Actions 服务器时区干扰
    nz_tz = ZoneInfo("Pacific/Auckland")
    nz_now = datetime.datetime.now(nz_tz)
    today = nz_now.date()
    
    print(f"当前新西兰系统时间: {nz_now}")
    print(f"识别到的今天的日期: {today}")
    
    bins_to_take_out = get_bins_for_tomorrow(today)
    
    if bins_to_take_out:
        send_wx_notification(bins_to_take_out)
    else:
        print("明天无需推垃圾桶，跳过推送。")
        
