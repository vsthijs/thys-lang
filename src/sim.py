#!/usr/bin/env python3

import sys
import parse


def parse(file: str) -> Program:
    lexer = parse.Lexer(f.read())
    parser = parse.Parser(lexer)
    parsed = [tok for tok in parser.parse()]
    ip = 0
