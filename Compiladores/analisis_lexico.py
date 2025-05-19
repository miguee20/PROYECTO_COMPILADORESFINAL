import re

patrones_token = {
    "KEYWORD": r"\b(if|else|while|for|return|int|float|void|print)\b",
    "IDENTIFIER": r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
    "NUMBER": r"\b\d+(\.\d+)?\b",
    "OPERATOR": r"[+\-*/]",
    "EQUAL": r"=",
    "RELATIONAL": r"(==|!=|>=|<=|>|<)",
    "LOGICAL": r"(&&|\|\||!)",
    "DELIMITER": r"[(),;{}]",
    "STRING": r'"[^"]*"',
    "WHITESPACE": r"\s+",
}

def identificar_tokens(texto):
    patron_general = "|".join(f"(?P<{tipo}>{patron})" for tipo, patron in patrones_token.items())
    patron_regex = re.compile(patron_general)
    tokens_encontrados = []
    for match in patron_regex.finditer(texto):
        for tipo, valor in match.groupdict().items():
            if valor is not None and tipo != "WHITESPACE":
                tokens_encontrados.append((tipo, valor))
    return tokens_encontrados

