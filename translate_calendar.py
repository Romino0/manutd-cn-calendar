from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = "https://www.manutd.com/en/Manchester_United.ics"
OUT = Path("manutd-cn.ics")

REPLACEMENTS = {
    "Manchester United": "曼联",
    "Man Utd": "曼联",
    "Premier League": "英格兰超级联赛",
    "UEFA Champions League": "欧洲冠军联赛",
    "Champions League": "欧洲冠军联赛",
    "UEFA Europa League": "欧足联欧洲联赛",
    "Europa League": "欧足联欧洲联赛",
    "FA Cup": "英格兰足总杯",
    "Carabao Cup": "英格兰联赛杯",
    "League Cup": "英格兰联赛杯",
    "Community Shield": "英格兰社区盾杯",
    "Friendly": "友谊赛",
    "Old Trafford": "老特拉福德球场",
    "Manchester City": "曼城",
    "Liverpool": "利物浦",
    "Arsenal": "阿森纳",
    "Chelsea": "切尔西",
    "Tottenham Hotspur": "托特纳姆热刺",
    "Tottenham": "热刺",
    "Newcastle United": "纽卡斯尔联",
    "Aston Villa": "阿斯顿维拉",
    "Brighton & Hove Albion": "布莱顿",
    "Brighton and Hove Albion": "布莱顿",
    "Everton": "埃弗顿",
    "Fulham": "富勒姆",
    "Crystal Palace": "水晶宫",
    "Nottingham Forest": "诺丁汉森林",
    "Brentford": "布伦特福德",
    "AFC Bournemouth": "伯恩茅斯",
    "Bournemouth": "伯恩茅斯",
    "Leeds United": "利兹联",
    "Ipswich Town": "伊普斯维奇",
    "Sunderland": "桑德兰",
    "Coventry City": "考文垂",
    "Hull City": "赫尔城",
    "West Ham United": "西汉姆联",
    "Wolverhampton Wanderers": "狼队",
    "Wolves": "狼队",
    "Leicester City": "莱斯特城",
    "Southampton": "南安普顿",
    "Burnley": "伯恩利",
    "Sheffield United": "谢菲尔德联",
    "Luton Town": "卢顿",
    "Real Madrid": "皇家马德里",
    "Barcelona": "巴塞罗那",
    "Atletico Madrid": "马德里竞技",
    "Bayern Munich": "拜仁慕尼黑",
    "Borussia Dortmund": "多特蒙德",
    "Paris Saint-Germain": "巴黎圣日耳曼",
    "PSG": "巴黎圣日耳曼",
    "Inter Milan": "国际米兰",
    "AC Milan": "AC米兰",
    "Juventus": "尤文图斯",
    "Napoli": "那不勒斯",
    "Benfica": "本菲卡",
    "Porto": "波尔图",
    "Sporting CP": "葡萄牙体育",
    "Ajax": "阿贾克斯",
    "PSV Eindhoven": "埃因霍温",
    "Feyenoord": "费耶诺德",
    "Celtic": "凯尔特人",
    "Rangers": "格拉斯哥流浪者",
    "Atalanta": "亚特兰大",
    "Roma": "罗马",
    "Lazio": "拉齐奥",
    "Sevilla": "塞维利亚",
    "Villarreal": "比利亚雷亚尔",
    "Athletic Club": "毕尔巴鄂竞技",
    "RB Leipzig": "RB莱比锡",
    "Bayer Leverkusen": "勒沃库森",
    "Marseille": "马赛",
    "Monaco": "摩纳哥",
    "Lyon": "里昂",
}


def translate(text: str) -> str:
    # Longest strings first avoids partial replacements such as Tottenham before Tottenham Hotspur.
    for src in sorted(REPLACEMENTS, key=len, reverse=True):
        text = text.replace(src, REPLACEMENTS[src])
    text = text.replace("X-WR-CALNAME:曼联", "X-WR-CALNAME:曼联赛程（中文）")
    return text


def main() -> None:
    req = Request(SOURCE, headers={"User-Agent": "Mozilla/5.0 manutd-cn-calendar"})
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    if "BEGIN:VCALENDAR" not in text or "END:VCALENDAR" not in text:
        raise RuntimeError("Official source did not return a valid iCalendar feed")
    translated = translate(text)
    OUT.write_text(translated, encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
