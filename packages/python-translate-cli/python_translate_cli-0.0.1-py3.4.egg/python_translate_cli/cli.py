#!/usr/bin/env python3
#-*- coding: utf8 -*-
import requests
import sys
import re


def translate(text):
    url = 'http://translate.google.com/translate_a/t?client=t&ie=UTF-8&oe=UTF-8&sl=en&tl=zh-CN&text=' + text
    page = requests.get(url)
    prog = re.compile(r'\[\[\["(\w+)"')
    result = prog.match(page.text).group(1)
    return result


def help():
    print("Usage: tl TEXT1 TEXT2")


def main():
    if len(sys.argv) < 2:
        help()
        sys.exit()
    words = translate(' '.join(sys.argv[1:]))
    print(words)

if __name__ == '__main__':
    main()
