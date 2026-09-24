import datetime
from zoneinfo import ZoneInfo

# ================= 配置区 =================
# 你家真实的收垃圾日 (0=周一, 1=周二, 2=周三, 3=周四, 4=周五)
COLLECTION_DAY = 3 
# 基准黄桶日
KNOWN_YELLOW_DATE = datetime.date(2026, 9, 24)
# 希望在收垃圾的前一天几点弹出手机闹钟？(24小时制，例如 19 代表晚上 7 点)
ALARM_HOUR = 19
# 一次性生成未来多少周的日历？（104周 = 刚好 2 年）
WEEKS_TO_GENERATE = 104
# =========================================

def generate_ics():
    nz_tz = ZoneInfo("Pacific/Auckland")
    today = datetime.datetime.now(nz_tz).date()
    
    # 找到最近的一个推桶日
    days_ahead = COLLECTION_DAY - today.weekday()
    if days_ahead < 0:
        days_ahead += 7
    next_collection = today + datetime.timedelta(days=days_ahead)

    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Christchurch Bin Reminder//CN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:基督城垃圾桶", # 手机上显示的日历名称
        "X-WR-TIMEZONE:Pacific/Auckland"
    ]

    # 全天事件默认从 00:00 算，计算提前几小时弹出闹钟
    hours_before = 24 - ALARM_HOUR

    for i in range(WEEKS_TO_GENERATE):
        current_date = next_collection + datetime.timedelta(weeks=i)
        delta_weeks = (current_date - KNOWN_YELLOW_DATE).days // 7
        
        if delta_weeks % 2 == 0:
            summary = "🟡 黄桶 + 🟢 绿桶"
            desc = "明天请推出 黄桶(可回收) 和 绿桶(厨余)。"
        else:
            summary = "🔴 红桶 + 🟢 绿桶"
            desc = "明天请推出 红桶(生活垃圾) 和 绿桶(厨余)。"

        dtstart = current_date.strftime("%Y%m%d")
        dtend = (current_date + datetime.timedelta(days=1)).strftime("%Y%m%d")
        uid = f"chch-bin-{dtstart}@yas1983.github.io"
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')

        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            # 定制系统闹钟
            "BEGIN:VALARM",
            f"TRIGGER:-PT{hours_before}H",
            "ACTION:DISPLAY",
            f"DESCRIPTION:{summary}",
            "END:VALARM",
            "END:VEVENT"
        ])

    ics_lines.append("END:VCALENDAR")

    with open("bins.ics", "w", encoding="utf-8") as f:
        f.write("\n".join(ics_lines))
    
    print(f"成功生成 bins.ics 日历文件，包含未来 {WEEKS_TO_GENERATE} 周的排期。")

if __name__ == "__main__":
    generate_ics()