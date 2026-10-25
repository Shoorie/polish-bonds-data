def month_after(month: str) -> str:
    year, number = (int(part) for part in str(month).split("-"))
    if number == 12:
        return f"{year + 1}-01"
    return f"{year}-{number + 1:02d}"
