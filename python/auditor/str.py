
def prefix(text: str, plen: int) -> str:
    if plen < len(text):
        return f"{text[:plen+1]}..."
    return text