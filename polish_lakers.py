from pathlib import Path
import re

PATH = Path("lakers-cn.ics")

STATE_NAMES = {
    "CA": "加利福尼亚州",
    "TX": "德克萨斯州",
    "AZ": "亚利桑那州",
    "CO": "科罗拉多州",
    "OR": "俄勒冈州",
    "UT": "犹他州",
    "OK": "俄克拉荷马州",
    "MN": "明尼苏达州",
    "TN": "田纳西州",
    "LA": "路易斯安那州",
    "NY": "纽约州",
    "MA": "马萨诸塞州",
    "PA": "宾夕法尼亚州",
    "DC": "华盛顿哥伦比亚特区",
    "FL": "佛罗里达州",
    "GA": "佐治亚州",
    "NC": "北卡罗来纳州",
    "OH": "俄亥俄州",
    "MI": "密歇根州",
    "IL": "伊利诺伊州",
    "WI": "威斯康星州",
    "IN": "印第安纳州",
    "ON": "安大略省",
    "NV": "内华达州",
}

TEXT_REPLACEMENTS = {
    "NBA Store": "NBA商店",
    "NBA Stats": "NBA数据",
    "Manage my ECAL": "管理我的 ECAL",
    "Tap to Watch": "点击观看",
    "NBA Cup 101": "NBA杯介绍",
    "It's NBA Cup Time! Don't miss the thrilling action of the NBA杯. Watch every game live and on-demand with NBA League Pass!": "NBA杯来了！不要错过精彩比赛。通过 NBA League Pass 可观看直播及点播！",
}


def unfold(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    out = []
    for line in text.split("\n"):
        if line.startswith((" ", "\t")) and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return out


def fold(line: str, limit: int = 73) -> list[str]:
    parts = []
    current = ""
    current_bytes = 0
    first = True
    for ch in line:
        b = len(ch.encode("utf-8"))
        allowed = limit if first else limit - 1
        if current and current_bytes + b > allowed:
            parts.append(("" if first else " ") + current)
            first = False
            current = ch
            current_bytes = b
        else:
            current += ch
            current_bytes += b
    parts.append(("" if first else " ") + current)
    return parts


def polish_description(value: str) -> str:
    value = re.sub(r"\bWest Group ([A-Z])\b", r"西部\1组", value, flags=re.I)
    value = re.sub(r"\bEast Group ([A-Z])\b", r"东部\1组", value, flags=re.I)
    value = re.sub(r"Watch live on ([^\\]+)", lambda m: "观看直播：" + ("待定" if m.group(1).strip().upper() == "TBD" else m.group(1).strip()), value, flags=re.I)
    value = re.sub(r"Stream live with NBA League Pass", "通过 NBA League Pass 观看直播", value, flags=re.I)
    value = re.sub(r"Listen live on ([^\\]+)", r"收听直播：\1", value, flags=re.I)
    value = re.sub(r"Join in (#[^\\]+)", r"参与话题 \1", value, flags=re.I)
    for src, dst in TEXT_REPLACEMENTS.items():
        value = value.replace(src, dst)
    return value


def polish_location(value: str) -> str:
    for code, zh in STATE_NAMES.items():
        value = re.sub(r"(?<![A-Za-z])" + re.escape(code) + r"(?![A-Za-z])", zh, value)
    return value


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    result = []
    for line in unfold(text):
        if ":" not in line:
            result.append(line)
            continue
        head, value = line.split(":", 1)
        prop = head.split(";", 1)[0].upper()
        if prop == "DESCRIPTION":
            value = polish_description(value)
        elif prop == "LOCATION":
            value = polish_location(value)
        result.append(head + ":" + value)

    folded = []
    for line in result:
        folded.extend(fold(line))
    PATH.write_text("\r\n".join(folded).rstrip("\r\n") + "\r\n", encoding="utf-8", newline="")


if __name__ == "__main__":
    main()
