#!/usr/bin/env python

# Copyright (c) 2019, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

try:
    from inspect import signature
except ImportError:
    try:
        from funcsigs import signature
    except ImportError:
        raise ImportError("Install funcsigs package with:\n    pip install funcsigs\nor\n    conda install funcsigs\n(or just use Python >= 3.3).")

import stagg
import stagg.checktype

classes = [stagg.Histogram]

prelude = """
"""

epilogue = """
"""

def formatted(cls, end="\n"):
    out = ["=== {0}{1}".format(cls.__name__, end)]
    
    for name, param in signature(cls.__init__).parameters.items():
        if name != "self":
            check = cls._params[name]
            hasdefault = param.default is not param.empty

            islist = False
            if isinstance(check, stagg.checktype.CheckBool):
                typestring = "bool"
            elif isinstance(check, stagg.checktype.CheckString):
                typestring = "str"
            elif isinstance(check, stagg.checktype.CheckNumber):
                typestring = "float in {0}{1}, {2}{3}".format(
                    "[" if check.min_inclusive else "(",
                    check.min,
                    check.max,
                    "]" if check.max_inclusive else ")")
            elif isinstance(check, stagg.checktype.CheckInteger):
                typestring = "int in {0}{1}, {2}{3}".format(
                    "(" if check.min == float("-inf") else "[",
                    check.min,
                    check.max,
                    ")" if check.max == float("inf") else "]")
            elif isinstance(check, stagg.checktype.CheckEnum):
                typestring = "one of " + check.choices[0].base + ".{" + ", ".join(str(x) for x in check.choices) + "}"
            elif isinstance(check, stagg.checktype.CheckClass):
                typestring = check.type.__name__
            elif isinstance(check, stagg.checktype.CheckKey) and check.type is str:
                typestring = "unique str"
            elif isinstance(check, (stagg.checktype.CheckVector, stagg.checktype.CheckLookup)):
                islist = True
                if check.type is str:
                    subtype = "str"
                elif check.type is int:
                    subtype = "int"
                elif check.type is float:
                    subtype = "float"
                elif check.type is list:
                    subtype = check.type[0].base + ".{" + ", ".join(str(x) for x in check.type) + "}"
                else:
                    subtype = check.type.__name__
                if check.minlen != 0 or check.maxlen != float("inf"):
                    withlength = " with length in [{0}, {1}{2}".format(
                        check.minlen,
                        check.maxlen,
                        ")" if check.maxlen == float("inf") else "]")
                else:
                    withlength = ""
                typestring = "list of {0}{1}".format(subtype, withlength)
            elif isinstance(check, stagg.checktype.CheckBuffer):
                typestring = "buffer"
            elif isinstance(check, stagg.checktype.CheckSlice):
                typestring = "slice (start:stop:step)"
            else:
                raise AssertionError(type(check))

            if hasdefault:
                defaultstring = " _(default: {0})_".format("[]" if islist and param.default is None else repr(param.default))
            else:
                defaultstring = ""

            out.append("* *{0}*: {1}{2}".format(name, typestring, defaultstring))

    return end.join(out)

if __name__ == "__main__":
    with open("../specification.adoc", "w") as file:
        file.write(prelude)

        for cls in classes:
            file.write(formatted(cls))

        file.write(epilogue)