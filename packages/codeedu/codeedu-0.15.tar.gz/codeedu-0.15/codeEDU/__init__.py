import sys
import requests
import json
import random
import textwrap
from splinter import Browser
import time

MAX = 196
PAGE = random.randint(2, MAX)
WIDTH = 78

def remove_non_ascii(text):
    return ''.join(c for c in text if ord(c) < 128)

def process(r):
    return '{url}'.format(url=r['url'])

def get_page(language):
    URL_POP = 'https://api.github.com/legacy/repos/search/'
    URL_POP += language + "?language=" + language
    r = requests.get(URL_POP)
    repos = json.loads(r.text)['repositories']
    repo = random.choice(repos)
    page_url = process(repo)
    with Browser() as browser:
        browser.visit(page_url)
        while True:
            time.sleep(10)

def code_main(args):
	print "welcome to codeEDU where we show you an interesting piece of code"
	if len(args) <= 1:
		print "generating PYTHON repo"
		get_page('python')
	else:
		print "generating " + args[1].upper() + " repo"
		get_page(args[1])

def go():
    print "welcome to codeEDU where we show you an interesting piece of code"
    print "generating PYTHON repo"
    get_page('python')

if __name__ == "__main__":
    code_main(sys.argv)