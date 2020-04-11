"""
This file is part of "imapdiag".

Copyright © 2020 Ralph Seichter
"""
import re
from argparse import ArgumentParser

from imapdiag import DESCRIPTION
from imapdiag import PROGRAM
from imapdiag.core import IMAPClient
from imapdiag.database import init_db
from imapdiag.logger import get_logger


def scan(args) -> None:
    client = IMAPClient(args.server[0], args.search, args.exclude, args.include)
    client.connect(args)
    client.scan_account()
    client.disconnect()


def compare(args) -> None:
    client = IMAPClient(args.server[0], args.search, args.exclude, args.include)
    client.connect(args)
    for server in args.server[1:]:
        other_client = IMAPClient(server, args.search, args.exclude, args.include)
        other_client.connect(args)
        client.compare_accounts(other_client)
        other_client.disconnect()
    client.disconnect()


def main():
    search = 'UNDELETED'
    level = 'DEBUG'
    re_ex = r'(Deleted|Draft|Entw[uü]rf|Gelöscht|Junk|Papierkorb|Spam|Template|Trash|Vorlage)'
    re_in = r'^INBOX$'
    url = 'sqlite:///:memory:'
    p = ArgumentParser(prog=PROGRAM, description=DESCRIPTION, fromfile_prefix_chars='@')
    p.add_argument('-c', dest='dbclear', action='store_const', const=True, default=False,
                   help='Clear database on startup')
    p.add_argument('-f', dest='search', metavar='FILTER', default=search,
                   help=f'IMAP search filter (default: {search})')
    p.add_argument('-m', dest='include', metavar='REGEX', default=re_in,
                   help=f'Mailbox include regex (default: {re_in})')
    p.add_argument('-x', dest='exclude', metavar='REGEX', default=re_ex,
                   help=f'Mailbox exclude regex (default: see documentation)')
    p.add_argument('-l', dest='level', default=level, help=f'Log level (default: {level})')
    p.add_argument('-s', dest='dburl', metavar='URL', default=url, help=f'SQLAlchemy database URL (default: {url})')
    p.add_argument('-u', dest='user', help='User name')
    p.add_argument('-p', dest='password', help='Password')
    p.add_argument('server', nargs='+', help='IMAP server')
    args = p.parse_args()
    get_logger(args.level)
    args.include = re.compile(args.include, re.IGNORECASE)
    args.exclude = re.compile(args.exclude, re.IGNORECASE)
    init_db(args.dburl, args.dbclear)
    if len(args.server) > 1:
        compare(args)
    else:
        scan(args)


if __name__ == '__main__':
    main()
