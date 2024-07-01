"""
Copyright 2024 Lukas Kubelka and Xuemin Duan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

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
