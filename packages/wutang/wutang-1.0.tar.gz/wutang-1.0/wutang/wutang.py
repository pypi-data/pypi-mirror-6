import sys
import os
import random


import requests
import yaml
from bs4 import BeautifulSoup
import argh
from argh.decorators import arg, named

dat_yaml = os.path.join(os.path.dirname(__file__), 'wutang.yaml')

ATTRS = yaml.load(file(dat_yaml, 'r'))

def get_nickname(realname, style):

    if not style:
        style = random.choice(ATTRS.keys())

    headers = {'Content-Type':'application/x-www-form-urlencoded'}

    url = ATTRS[style]['url']
    submit = ATTRS[style]['submit']
    data = 'realname=%s&Submit=%s' % (realname, submit)
    res = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(res.content)
    soup = eval(ATTRS[style]['soup'])
    name = " ".join(soup.getText().split())

    return name

@named('me')
@arg('-s', '--style', choices=ATTRS.keys(), default=None,
     help='nickname style. if None, style will be randomized.', required=False)
@arg('realname', nargs=1, help='a name. your name. a string.')
def my_nickname(args):

    return get_nickname(args.realname, args.style)

@named('random')
@arg('-s', '--style', choices=ATTRS.keys(), default=None,
     help='nickname style. if None, style will be randomized.', required=False)
def random_nickname(args):

    realname = str(random.randint(1,99999))
    return get_nickname(realname, args.style)


def main():

    argp = argh.ArghParser()
    argp.add_commands([random_nickname, my_nickname])
    argp.dispatch()

if __name__ == '__main__':

    main()

