def mask_credential(value: str) -> str:
    """
    Маскирует чувствительные данные (Data Redaction / Obfuscation).
    Паттерн обфускации: оставляет первые 3 и последние 3 символа (abc...xyz).
    Если длина <= 6, оставляет первый и последний символ (a***z).
    """
    if not value:
        return ""
    val_str = str(value).strip()
    length = len(val_str)
    if length <= 2:
        return "***"
    elif length <= 6:
        return f"{val_str[0]}***{val_str[-1]}"
    return f"{val_str[:3]}...{val_str[-3:]}"

def mask_url(url: str) -> str:
    """
    Маскирует значение токена авторизации в URL адресе.
    """
    if not url:
        return ""
    if "?token=" in url:
        parts = url.split("?token=", 1)
        token_part = parts[1]
        # Если есть дополнительные query-параметры
        if "&" in token_part:
            t_val, rest = token_part.split("&", 1)
            return f"{parts[0]}?token={mask_credential(t_val)}&{rest}"
        return f"{parts[0]}?token={mask_credential(token_part)}"
    return url
