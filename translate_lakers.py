from pathlib import Path
from urllib.request import Request, urlopen
import gzip
import re

SOURCE = "https://ics.ecal.com/ecal-sub/6a7d89f67f27260002e9818f/NBA.ics"
OUT = Path("lakers-cn.ics")

# NBA China official Chinese team names. Include full names, common short names,
# and three-letter abbreviations because calendar providers may use any of them.
TEAM_ALIASES = [
    (["Los Angeles Lakers", "LA Lakers", "L.A. Lakers", "Lakers", "LAL"], "洛杉矶湖人"),
    (["Atlanta Hawks", "Hawks", "ATL"], "亚特兰大老鹰"),
    (["Boston Celtics", "Celtics", "BOS"], "波士顿凯尔特人"),
    (["Brooklyn Nets", "Nets", "BKN"], "布鲁克林篮网"),
    (["Charlotte Hornets", "Hornets", "CHA"], "夏洛特黄蜂"),
    (["Chicago Bulls", "Bulls", "CHI"], "芝加哥公牛"),
    (["Cleveland Cavaliers", "Cavaliers", "Cavs", "CLE"], "克利夫兰骑士"),
    (["Dallas Mavericks", "Mavericks", "Mavs", "DAL"], "达拉斯独行侠"),
    (["Denver Nuggets", "Nuggets", "DEN"], "丹佛掘金"),
    (["Detroit Pistons", "Pistons", "DET"], "底特律活塞"),
    (["Golden State Warriors", "GS Warriors", "Warriors", "GSW"], "金州勇士"),
    (["Houston Rockets", "Rockets", "HOU"], "休斯顿火箭"),
    (["Indiana Pacers", "Pacers", "IND"], "印第安纳步行者"),
    (["Los Angeles Clippers", "LA Clippers", "L.A. Clippers", "Clippers", "LAC"], "洛杉矶快船"),
    (["Memphis Grizzlies", "Grizzlies", "MEM"], "孟菲斯灰熊"),
    (["Miami Heat", "Heat", "MIA"], "迈阿密热火"),
    (["Milwaukee Bucks", "Bucks", "MIL"], "密尔沃基雄鹿"),
    (["Minnesota Timberwolves", "Timberwolves", "T-Wolves", "Wolves", "MIN"], "明尼苏达森林狼"),
    (["New Orleans Pelicans", "Pelicans", "NOP", "NO"], "新奥尔良鹈鹕"),
    (["New York Knicks", "NY Knicks", "Knicks", "NYK"], "纽约尼克斯"),
    (["Oklahoma City Thunder", "OKC Thunder", "Thunder", "OKC"], "俄克拉荷马雷霆"),
    (["Orlando Magic", "Magic", "ORL"], "奥兰多魔术"),
    (["Philadelphia 76ers", "Philadelphia Sixers", "76ers", "Sixers", "PHI"], "费城76人"),
    (["Phoenix Suns", "Suns", "PHX"], "菲尼克斯太阳"),
    (["Portland Trail Blazers", "Trail Blazers", "Blazers", "POR"], "波特兰开拓者"),
    (["Sacramento Kings", "Kings", "SAC"], "萨克拉门托国王"),
    (["San Antonio Spurs", "Spurs", "SAS"], "圣安东尼奥马刺"),
    (["Toronto Raptors", "Raptors", "TOR"], "多伦多猛龙"),
    (["Utah Jazz", "Jazz", "UTA"], "犹他爵士"),
    (["Washington Wizards", "Wizards", "WAS"], "华盛顿奇才"),
]

COMPETITIONS = {
    "Emirates NBA Cup": "NBA杯",
    "NBA In-Season Tournament": "NBA杯",
    "In-Season Tournament": "NBA杯",
    "NBA Regular Season": "NBA常规赛",
    "Regular Season": "常规赛",
    "NBA Preseason": "NBA季前赛",
    "Preseason": "季前赛",
    "NBA Playoffs": "NBA季后赛",
    "Playoffs": "季后赛",
    "NBA Finals": "NBA总决赛",
    "Western Conference Finals": "西部决赛",
    "Eastern Conference Finals": "东部决赛",
    "Western Conference Semifinals": "西部半决赛",
    "Eastern Conference Semifinals": "东部半决赛",
    "First Round": "首轮",
    "NBA Summer League": "NBA夏季联赛",
    "Summer League": "夏季联赛",
    "NBA All-Star": "NBA全明星",
    "All-Star": "全明星",
}

# Use established Chinese arena names where they are widely used. Unknown or newly
# renamed venues are intentionally left in English rather than inventing a translation.
VENUES = {
    "Crypto.com Arena": "Crypto.com球馆",
    "Chase Center": "大通中心",
    "Madison Square Garden": "麦迪逊广场花园",
    "Barclays Center": "巴克莱中心",
    "TD Garden": "TD花园",
    "United Center": "联合中心",
    "Toyota Center": "丰田中心",
    "Ball Arena": "波尔球馆",
    "Moda Center": "摩达中心",
    "Delta Center": "德尔塔中心",
    "Paycom Center": "Paycom中心",
    "Target Center": "标靶中心",
    "Golden 1 Center": "黄金一号中心",
    "Intuit Dome": "Intuit Dome球馆",
    "Frost Bank Center": "弗罗斯特银行中心",
    "American Airlines Center": "美国航空中心",
    "FedExForum": "联邦快递球馆",
    "Smoothie King Center": "冰沙王中心",
    "Kia Center": "起亚中心",
    "Kaseya Center": "卡西亚中心",
    "State Farm Arena": "州立农业保险球馆",
    "Spectrum Center": "光谱中心",
    "Capital One Arena": "第一资本球馆",
    "Gainbridge Fieldhouse": "盖恩布里奇球馆",
    "Scotiabank Arena": "丰业银行球馆",
    "Little Caesars Arena": "小凯撒球馆",
}

PLACES = {
    "Los Angeles": "洛杉矶",
    "San Francisco": "旧金山",
    "Sacramento": "萨克拉门托",
    "Phoenix": "菲尼克斯",
    "Denver": "丹佛",
    "Portland": "波特兰",
    "Salt Lake City": "盐湖城",
    "Oklahoma City": "俄克拉荷马城",
    "Minneapolis": "明尼阿波利斯",
    "San Antonio": "圣安东尼奥",
    "Houston": "休斯顿",
    "Dallas": "达拉斯",
    "Memphis": "孟菲斯",
    "New Orleans": "新奥尔良",
    "New York": "纽约",
    "Brooklyn": "布鲁克林",
    "Boston": "波士顿",
    "Philadelphia": "费城",
    "Washington": "华盛顿",
    "Miami": "迈阿密",
    "Orlando": "奥兰多",
    "Atlanta": "亚特兰大",
    "Charlotte": "夏洛特",
    "Cleveland": "克利夫兰",
    "Detroit": "底特律",
    "Chicago": "芝加哥",
    "Milwaukee": "密尔沃基",
    "Indianapolis": "印第安纳波利斯",
    "Toronto": "多伦多",
}

PHRASES = {
    "Add to Calendar": "添加到日历",
    "Buy Tickets": "购买门票",
    "Tickets": "门票",
    "Game Reminder": "比赛提醒",
    "Reminder": "比赛提醒",
    "Home": "主场",
    "Away": "客场",
}


def replace_alias(text: str, alias: str, replacement: str) -> str:
    pattern = re.compile(r"(?<![A-Za-z0-9])" + re.escape(alias) + r"(?![A-Za-z0-9])", re.IGNORECASE)
    return pattern.sub(replacement, text)


def translate_teams(text: str) -> str:
    entries = []
    for aliases, zh in TEAM_ALIASES:
        for alias in aliases:
            entries.append((alias, zh))
    for alias, zh in sorted(entries, key=lambda x: len(x[0]), reverse=True):
        text = replace_alias(text, alias, zh)
    return text


def translate_general(text: str) -> str:
    text = translate_teams(text)
    for src, dst in sorted(COMPETITIONS.items(), key=lambda x: len(x[0]), reverse=True):
        text = replace_alias(text, src, dst)
    for src, dst in sorted(PHRASES.items(), key=lambda x: len(x[0]), reverse=True):
        text = replace_alias(text, src, dst)
    text = text.replace(" vs. ", " vs ").replace(" VS. ", " vs ")
    return text


def translate_location(text: str) -> str:
    for src, dst in sorted(VENUES.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(src, dst)
    for src, dst in sorted(PLACES.items(), key=lambda x: len(x[0]), reverse=True):
        text = replace_alias(text, src, dst)
    return text


def unfold_ical(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for line in text.split("\n"):
        if line.startswith((" ", "\t")) and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out


def fold_line(line: str, limit: int = 73) -> list[str]:
    # Fold by UTF-8 bytes so the file remains friendly to strict iCalendar clients.
    parts = []
    current = ""
    current_bytes = 0
    prefix = ""
    for ch in line:
        b = len(ch.encode("utf-8"))
        allowed = limit if not parts else limit - 1
        if current and current_bytes + b > allowed:
            parts.append(prefix + current)
            current = ch
            current_bytes = b
            prefix = " "
        else:
            current += ch
            current_bytes += b
    parts.append(prefix + current)
    return parts


def process(text: str) -> str:
    result = []
    for line in unfold_ical(text):
        if ":" not in line:
            result.append(line)
            continue
        head, value = line.split(":", 1)
        prop = head.split(";", 1)[0].upper()
        if prop == "X-WR-CALNAME":
            value = "洛杉矶湖人赛程（中文）"
        elif prop == "LOCATION":
            value = translate_location(translate_general(value))
        elif prop in {"SUMMARY", "DESCRIPTION", "COMMENT", "CATEGORIES", "X-ALT-DESC"}:
            value = translate_general(value)
        result.append(head + ":" + value)

    # Add a Chinese calendar name if the upstream feed does not provide one.
    if not any(x.upper().startswith("X-WR-CALNAME:") for x in result):
        try:
            idx = next(i for i, x in enumerate(result) if x.upper().startswith("BEGIN:VEVENT"))
        except StopIteration:
            idx = len(result) - 1
        result.insert(idx, "X-WR-CALNAME:洛杉矶湖人赛程（中文）")

    folded = []
    for line in result:
        folded.extend(fold_line(line))
    return "\r\n".join(folded).rstrip("\r\n") + "\r\n"


def main() -> None:
    req = Request(
        SOURCE,
        headers={
            "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 lakers-cn-calendar",
            "Accept": "text/calendar,text/plain,*/*",
        },
    )
    with urlopen(req, timeout=45) as resp:
        raw = resp.read()
        if (resp.headers.get("Content-Encoding") or "").lower() == "gzip":
            raw = gzip.decompress(raw)
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    if "BEGIN:VCALENDAR" not in text or "END:VCALENDAR" not in text:
        raise RuntimeError("eCal source did not return a valid iCalendar feed")
    OUT.write_text(process(text), encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
