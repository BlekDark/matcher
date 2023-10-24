from src.utils import preprocess_string, translit_rule, translit_rule_ruen, translit_rule_esen


def transliterate2(rule: dict, s: str) -> str:
    translit_result = []
    s = preprocess_string(s)
    for symbol in s:
        lower_symbol = symbol.lower()
        if lower_symbol in rule.keys():
            translit_symb = rule[lower_symbol]
        else:
            translit_symb = lower_symbol

        if symbol.isupper():
            translit_symb = translit_symb.upper()

        translit_result.append(translit_symb)

    return "".join(translit_result)


def get_transliteration(rule: dict):
    return lambda s: transliterate2(rule, s)


def transliterate(s: str) -> str:
    translit_result = []
    s = preprocess_string(s)
    for symbol in s:
        lower_symbol = symbol.lower()
        if lower_symbol in translit_rule.keys():
            translit_symb = translit_rule[lower_symbol]
        else:
            translit_symb = lower_symbol

        if symbol.isupper():
            translit_symb = translit_symb.upper()

        translit_result.append(translit_symb)

    return "".join(translit_result)
