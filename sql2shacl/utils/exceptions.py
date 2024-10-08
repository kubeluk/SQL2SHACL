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


class MissingSQLDatatypeException(Exception):
    """Raised when column definition does not contain a data type."""

    pass


class UnsupportedSQLDatatypeException(Exception):
    """Raised when SQL datatype is not found in XSDSchema mapping file."""

    pass


class ColumnNotFoundException(Exception):
    """Raised when the column of a UNIQUE/ PRIMARY KEY table constraint does not exist in the relation."""

    pass
