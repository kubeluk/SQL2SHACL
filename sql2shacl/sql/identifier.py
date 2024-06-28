import unicodedata


def is_valid_identifier(s: str) -> bool:
    """Returns if string is <identifier part>.

    ```
    <identifier part> ::=
        <identifier start>
        | <identifier extend>

    <identifier start> ::=
        An <identifier start> is any character in the Unicode General Category
        classes “Lu”, “Ll”, “Lt”, “Lm”, “Lo”, or “Nl”

    <identifier extend> ::=
        An <identifier extend> is U+00B7, “Middle Dot”, or any character in the Unicode General Category
        classes “Mn”, “Mc”, “Nd”, or “Pc”
    ```
    """

    if not s:
        return False

    for char in s:
        category = unicodedata.category(char)

        # Check if it is an <identifier start>
        if category in ("Lu", "Ll", "Lt", "Lm", "Lo", "Nl"):
            continue

        # Check if it is an <identifier extend>
        if category in ("Mn", "Mc", "Nd", "Pc") or char == "\u00B7":
            continue

        return False

    return True
