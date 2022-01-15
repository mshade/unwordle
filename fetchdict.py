#!/usr/bin/env python
import json
import re
import requests


def fetch(filename="words.json"):
    homepage = "https://www.powerlanguage.co.uk/wordle/"
    r = requests.get(homepage)

    js_regex = "main\.[a-z0-9]{8}\.js"

    jsfile = re.findall(js_regex, r.text)

    mainjs = requests.get(homepage + jsfile[0])

    vars_regex = '=(\[("[a-z]+"(,|))+\]),'

    jsvars = re.findall(vars_regex, mainjs.text)

    dictionary = []

    for match in jsvars:
        if len(match[0]) > 100:
            dictionary += json.loads(match[0])

    with open(filename, "w") as file:
        json.dump(dictionary, file)


if __name__ == "__main__":
    fetch()
