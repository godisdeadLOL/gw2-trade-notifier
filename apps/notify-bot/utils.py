from shared import ItemUpdate


def escape_markdown(text: str):
    special_chars = "_*[]()~`>#+-=|{}.! "
    escaped = ""
    for ch in text:
        if ch in special_chars:
            escaped += "\\" + ch
        else:
            escaped += ch
    return escaped


def truncate(line: str, width: int):
    if len(line) <= width:
        return line

    return line[: width - 3] + "..."


def format_price(price: int):
    # 🟡⚪️🟠

    gold = price // 10000

    price %= 10000

    silver = price // 100
    price %= 100

    copper = price

    msg = ""
    if gold > 0:
        value = str(gold)
        msg += f"{value.ljust(2)}🟡 "
    if silver > 0:
        value = str(silver)
        msg += f"{value.ljust(2)}⚪️ "
    if copper > 0:
        value = str(copper)
        msg += f"{value.ljust(2)}🟠 "

    return msg.strip()


def format_update(update: ItemUpdate):
    name = update.name
    price = format_price(update.price)

    return f"{price} — x{update.count} {name}"


def format_updates(updates: list[ItemUpdate]):
    msg = ""

    for transaction in updates:
        msg += format_update(transaction) + "\n"

    return escape_markdown(msg)
