"""
A simple implementation of bencoding in python.

Bencoding is a way to serialize and organize data. The format supports four data
types: Strings, Integers, Lists and Dictionaries.

Strings: <string length encoded in base ten ASCII>:<string data>
-------
Bencoded strings are encoded in the format:
"<string length encoded in base ten ASCII>:<string data>" there is no constant
beginning delimiter and no ending delimiter.
Example of bencoded string:
    "5:Hello" encodes the string "Hello"


Integers: i<integer encoded in base ten ASCII>e
--------
Integers are encoded as "i<integer encoded in base ten ASCII>e" the initial i
and trailing e is the beginning and ending delimiters. A negative integer can be
represented as i-42e while positive are represented as i42e. Padding the integer
with zeros are not allowed, as such i042e is invalid. However the value i0e is
allowed.
Example:
    "i42e" encodes the integer 42


Lists: l<bencoded elements>e
-----
The initial l and trailing e is the start end ending delimiters. A bencoded list
can contain any bencoded type, even lists containing lists.
Example:
    "li1ei2ei3ee" encodes the list [1, 2, 3]


Dictionaries: d<bencoded string><bencoded element>e
------------
The initial d and trailing e are the start and ending delimiters. A dictionary
is one or more key value pairs. Note that all key's must be bencoded strings.
The keys must appear in sorted order using a binary comparison.
Example:
    'd4:listli1ei2ei3ee3:str5:Helloe' encodes dict(str="Hello", list=[1, 2, 3])

"""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals
)

import sys
from pprint import pprint


if sys.version_info.major == 2:
    chr = unichr
    string_type = basestring
elif sys.version_info.major == 3:
    # chr should assume Unicode
    string_type = str


def decode(b_data):
    """
    Decodes a bencoded byte array into the relevant python data type

    :param b_data: Byte array of bencoded data
    :rtype : Either a {Dict|List|Integer|String}
    """

    def _bdecode(data):
        """
        Does the actual work of decoding bencoded data.

        :param data: A list of a byte array containing the bencoded data
        :rtype : {Dict|List|Integer|String}
        :raise Exception: If input is not valid bencoded data
        """
        while len(data) != 0:
            char = data.pop()

            # bencoded dictionary
            if char == 'd':
                char = data.pop()
                b_dict = {}
                while char != 'e':
                    data.append(char)
                    key = _bdecode(data)
                    b_dict[key] = _bdecode(data)
                    char = data.pop()
                return b_dict

            # bencoded list
            elif char == 'l':
                char = data.pop()
                b_list = []
                while char != 'e':
                    data.append(char)
                    b_list.append(_bdecode(data))
                    char = data.pop()
                return b_list

            # bencoded integer
            elif char == 'i':
                char = data.pop()
                b_int = ''
                while char != 'e':
                    b_int += char
                    char = data.pop()
                return int(b_int)

            # bencoded string
            elif char.isdigit():
                line_len = ''
                while char.isdigit():
                    line_len += char
                    char = data.pop()
                b_string = ''
                for _ in range(int(line_len)):
                    b_string += data.pop()
                return b_string
            else:
                raise Exception("Invalid bencoded input")

    data_list = list(b_data)
    data_list.reverse()  # We want to be able to pop from the start
    data_list = [chr(c) for c in data_list]  # map chr to data_list
    return _bdecode(data_list)


def encode(data):
    """
    Takes either a Dict, List, Integer or String and encodes it to a bencoded
    string
    :param data: {Dict|List|Integer|String}
    :return: a bencoded String
    :raise Exception: and exception is raised if the data could not be bencoded
    """

    # data is a string
    if isinstance(data, string_type):
        b_string = "{length}:{str}".format(length=len(data), str=data)
        return b_string

    # data is an integer
    elif isinstance(data, int):
        b_int = "i{integer}e".format(integer=str(data))
        return b_int

    # data is a list
    elif isinstance(data, list):
        list_elements = "".join([encode(element) for element in data])
        b_list = "l{list_elements}e".format(list_elements=list_elements)
        return b_list

    # data is a dictionary
    elif isinstance(data, dict):
        b_dict = "d"
        for key in sorted(data.keys()):
            b_dict += encode(key) + encode(data[key])
        b_dict += "e"
        return b_dict

    else:
        raise Exception("Input data could not be bencoded")


def main(argv):
    if len(argv) > 1:
        path = argv[1]
        with open(path, "rb") as f:
            content = bytearray(f.read())
            b_data = decode(content)
            b_data['info']['pieces'] = ''.join(["{0:02x}".format(ord(x)) for
                                                x in b_data['info']['pieces']])
            pprint(b_data)

    assert encode("Hello") == "5:Hello"
    assert encode(23) == "i23e"
    assert encode([1, 2, 3]) == "li1ei2ei3ee"
    assert encode(dict(str="Hello", list=[1, 2, 3])) == \
        'd4:listli1ei2ei3ee3:str5:Helloe'

    assert decode(bytearray("5:Hello", "utf-8")) == "Hello"
    assert decode(bytearray("i23e", "utf-8")) == 23
    assert decode(bytearray("li1ei2ei3ee", "utf-8")) == [1, 2, 3]
    assert decode(bytearray("d4:listli1ei2ei3ee3:str5:Helloe", "utf-8")) == \
        dict(str="Hello", list=[1, 2, 3])

    test_data = {
        "string": "String of data",
        "list": [1, 2, 3],
        "int": 42,
        "nested_dict": {
            "string": "another string of data",
            "list": [2, 4, 6],
            "int": -42
        }
    }

    b_data = encode(test_data)
    data = decode(bytearray(b_data, 'utf-8'))
    assert data == test_data


if __name__ == "__main__":
    main(sys.argv)
