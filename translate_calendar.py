from pathlib import Path
from urllib.request import Request, urlopen
import re

SOURCE = "https://www.manutd.com/en/Manchester_United.ics"
OUT = Path("manutd-cn.ics")

# Team and competition names used in SUMMARY / match DESCRIPTION.
# The official Manchester United feed often uses short aliases rather than
# full club names, so both forms are intentionally included.
MATCH_REPLACEMENTS = {
    # Manchester United
    "Manchester United": "曼联",
    "Man United": "曼联",
    "Man Utd": "曼联",

    # Competitions
    "UEFA Champions League": "欧洲冠军联赛",
    "Champions League": "欧洲冠军联赛",
    "UEFA Europa League": "欧足联欧洲联赛",
    "Europa League": "欧足联欧洲联赛",
    "Premier League": "英格兰超级联赛",
    "Emirates FA Cup": "英格兰足总杯",
    "FA Cup": "英格兰足总杯",
    "Carabao Cup": "英格兰联赛杯",
    "League Cup": "英格兰联赛杯",
    "Community Shield": "英格兰社区盾杯",
    "Friendly Match": "友谊赛",
    "Friendly": "友谊赛",

    # 2026/27 Premier League opponents and actual aliases used by the feed
    "Manchester City": "曼城",
    "Man City": "曼城",
    "Hull City": "赫尔城",
    "Hull": "赫尔城",
    "Ipswich Town": "伊普斯维奇",
    "Ipswich": "伊普斯维奇",
    "Everton": "埃弗顿",
    "Fulham": "富勒姆",
    "Tottenham Hotspur": "托特纳姆热刺",
    "Tottenham": "热刺",
    "Spurs": "热刺",
    "Leeds United": "利兹联",
    "Leeds": "利兹联",
    "AFC Bournemouth": "伯恩茅斯",
    "Bournemouth": "伯恩茅斯",
    "Chelsea": "切尔西",
    "Aston Villa": "阿斯顿维拉",
    "Villa": "阿斯顿维拉",
    "Liverpool": "利物浦",
    "Brentford": "布伦特福德",
    "Newcastle United": "纽卡斯尔联",
    "Newcastle": "纽卡斯尔联",
    "Coventry City": "考文垂",
    "Coventry": "考文垂",
    "Crystal Palace": "水晶宫",
    "Palace": "水晶宫",
    "Arsenal": "阿森纳",
    "Nottingham Forest": "诺丁汉森林",
    "Nott'm Forest": "诺丁汉森林",
    "Nottm Forest": "诺丁汉森林",
    "Nott Forest": "诺丁汉森林",
    "Forest": "诺丁汉森林",
    "Sunderland": "桑德兰",
    "Brighton & Hove Albion": "布莱顿",
    "Brighton and Hove Albion": "布莱顿",
    "Brighton": "布莱顿",

    # Other English clubs for cup fixtures / future seasons
    "West Ham United": "西汉姆联",
    "West Ham": "西汉姆联",
    "Wolverhampton Wanderers": "狼队",
    "Wolves": "狼队",
    "Leicester City": "莱斯特城",
    "Leicester": "莱斯特城",
    "Southampton": "南安普顿",
    "Burnley": "伯恩利",
    "Sheffield United": "谢菲尔德联",
    "Sheff Utd": "谢菲尔德联",
    "Luton Town": "卢顿",
    "Wrexham": "雷克瑟姆",

    # Common European clubs / official-feed aliases
    "Real Madrid": "皇家马德里",
    "Barcelona": "巴塞罗那",
    "Atlético Madrid": "马德里竞技",
    "Atletico Madrid": "马德里竞技",
    "Atlético": "马德里竞技",
    "Atletico": "马德里竞技",
    "Bayern Munich": "拜仁慕尼黑",
    "Borussia Dortmund": "多特蒙德",
    "Paris Saint-Germain": "巴黎圣日耳曼",
    "Paris SG": "巴黎圣日耳曼",
    "PSG": "巴黎圣日耳曼",
    "Inter Milan": "国际米兰",
    "Internazionale": "国际米兰",
    "AC Milan": "AC米兰",
    "Milan": "AC米兰",
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
    "Rosenborg": "罗森博格",
}

# Venue-specific translations. Keep these separate from team aliases so a
# city such as Leeds is rendered as “利兹”, not the club name “利兹联”.
LOCATION_REPLACEMENTS = {
    # Stadiums
    "Tottenham Hotspur Stadium": "托特纳姆热刺球场",
    "American Express Community Stadium": "美国运通社区球场",
    "American Express Stadium": "美国运通社区球场",
    "Coventry Building Society Arena": "考文垂建筑协会球场",
    "Hill Dickinson Stadium": "希尔·迪金森球场",
    "Gtech Community Stadium": "Gtech社区球场",
    "Old Trafford": "老特拉福德球场",
    "Etihad Stadium": "伊蒂哈德球场",
    "Emirates Stadium": "酋长球场",
    "Stamford Bridge": "斯坦福桥球场",
    "Craven Cottage": "克拉文农场球场",
    "Elland Road": "埃兰路球场",
    "Villa Park": "维拉公园球场",
    "Anfield": "安菲尔德球场",
    "St James' Park": "圣詹姆斯公园球场",
    "St. James' Park": "圣詹姆斯公园球场",
    "Selhurst Park": "塞尔赫斯特公园球场",
    "The City Ground": "城市球场",
    "City Ground": "城市球场",
    "Stadium of Light": "光明球场",
    "Amex Stadium": "美国运通社区球场",
    "Vitality Stadium": "活力球场",
    "MKM Stadium": "MKM球场",
    "Portman Road": "波特曼路球场",

    # 2026/27 league cities / regions
    "Newcastle upon Tyne": "泰恩河畔纽卡斯尔",
    "West Yorkshire": "西约克郡",
    "West Midlands": "西米德兰兹",
    "East Sussex": "东萨塞克斯郡",
    "Tyne and Wear": "泰恩-威尔郡",
    "Merseyside": "默西塞德",
    "Middlesex": "米德尔塞克斯郡",
    "Nottinghamshire": "诺丁汉郡",
    "Suffolk": "萨福克郡",
    "Dorset": "多塞特郡",
    "Manchester": "曼彻斯特",
    "Liverpool": "利物浦",
    "Birmingham": "伯明翰",
    "Nottingham": "诺丁汉",
    "Bournemouth": "伯恩茅斯",
    "Sunderland": "桑德兰",
    "Coventry": "考文垂",
    "Brighton": "布莱顿",
    "Falmer": "法尔默",
    "Brentford": "布伦特福德",
    "Ipswich": "伊普斯维奇",
    "London": "伦敦",
    "Leeds": "利兹",
    "Hull": "赫尔",

    # Current pre-season venues
    "Helsingin olympiastadion": "赫尔辛基奥林匹克体育场",
    "Helsinki (Helsingfors)": "赫尔辛基",
    "Lerkendal Stadion": "莱肯达尔球场",
    "Trondheim": "特隆赫姆",
    "Strawberry Arena": "草莓竞技场",
    "Solna": "索尔纳",
    "Nya Ullevi": "新乌利维球场",
    "Göteborg": "哥德堡",
    "Croke Park": "克罗克公园球场",
    "Dublin": "都柏林",
    "Tarczyński Arena": "塔尔琴斯基竞技场",
    "Wrocław": "弗罗茨瓦夫",
}


def replace_terms(text: str, mapping: dict[str, str]) -> str:
    # Longest first prevents partial matches such as Tottenham before
    # Tottenham Hotspur or Milan before AC Milan.
    for src in sorted(mapping, key=len, reverse=True):
        text = text.replace(src, mapping[src])
    return text


def unfold_ical(text: str) -> list[str]:
    """Unfold RFC 5545 continuation lines into logical lines."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    physical = text.split("\n")
    logical: list[str] = []
    for line in physical:
        if line.startswith((" ", "\t")) and logical:
            logical[-1] += line[1:]
        else:
            logical.append(line)
    return logical


def fold_ical_line(line: str, limit: int = 73) -> list[str]:
    """Fold long iCalendar lines without splitting a UTF-8 character."""
    if len(line.encode("utf-8")) <= limit:
        return [line]

    chunks: list[str] = []
    current = ""
    current_bytes = 0
    first = True

    for ch in line:
        b = len(ch.encode("utf-8"))
        allowed = limit if first else limit - 1
        if current and current_bytes + b > allowed:
            chunks.append(current if first else " " + current)
            first = False
            current = ch
            current_bytes = b
        else:
            current += ch
            current_bytes += b

    if current:
        chunks.append(current if first else " " + current)
    return chunks


def translate_description(value: str) -> str:
    value = replace_terms(value, MATCH_REPLACEMENTS)

    # Replace Manchester United's standard English disclaimer, but keep the
    # official URLs so users can still jump to fixture, MUTV and ticket pages.
    marker = "\\n\\nAll dates subject to change."
    if marker in value:
        match_info = value.split(marker, 1)[0]
        return (
            match_info
            + "\\n\\n赛程日期及开球时间可能调整。"
            + "赛程信息：https://www.manutd.com/en/matches/mens-team/fixtures。"
            + "比赛直播、集锦及赛后内容：https://www.manutd.com/en/mutv。"
            + "门票及贵宾服务：https://tickets.manutd.com。"
        )

    return value.replace("All dates subject to change.", "赛程日期及开球时间可能调整。")


def validate_premier_league_summaries(logical_lines: list[str]) -> None:
    """Fail if a Premier League title still contains an untranslated English team name."""
    for line in logical_lines:
        if not line.startswith("SUMMARY:") or "英格兰超级联赛" not in line:
            continue
        # 'vs' is intentionally retained as the matchup separator. Remove it,
        # then any remaining ASCII letters indicate an untranslated alias.
        check = line.replace("SUMMARY:", "").replace("vs", "")
        if re.search(r"[A-Za-z]", check):
            raise RuntimeError(f"Untranslated Premier League team alias remains: {line}")


def translate_calendar(text: str) -> str:
    output: list[str] = []

    for line in unfold_ical(text):
        if not line:
            continue

        if line.startswith("X-WR-CALNAME:"):
            line = "X-WR-CALNAME:曼联赛程（中文）"
        elif line.startswith("SUMMARY:"):
            line = "SUMMARY:" + replace_terms(
                line[len("SUMMARY:"):], MATCH_REPLACEMENTS
            )
        elif line.startswith("DESCRIPTION:"):
            value = line[len("DESCRIPTION:"):]
            if value == "Reminder":
                value = "比赛提醒"
            else:
                value = translate_description(value)
            line = "DESCRIPTION:" + value
        elif line.startswith("LOCATION:"):
            line = "LOCATION:" + replace_terms(
                line[len("LOCATION:"):], LOCATION_REPLACEMENTS
            )
        # UID, DTSTART/DTEND, SEQUENCE and other machine-readable metadata are
        # deliberately left untouched so subscriptions update correctly.

        output.extend(fold_ical_line(line))

    translated = "\r\n".join(output) + "\r\n"
    validate_premier_league_summaries(unfold_ical(translated))
    return translated


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

    OUT.write_text(translate_calendar(text), encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
