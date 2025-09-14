from datetime import datetime

def format_date(date_string: str) -> str:
    """Format date string for display"""
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date.strftime("%b %d, %Y %H:%M")
    except:
        return date_string

def format_price(price: float) -> str:
    """Format price with appropriate decimal places"""
    if price >= 1000:
        return f"₹{price:,.0f}"
    elif price >= 100:
        return f"₹{price:,.1f}"
    else:
        return f"₹{price:,.2f}"

def format_percentage(change: float) -> str:
    """Format percentage change"""
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.2f}%"