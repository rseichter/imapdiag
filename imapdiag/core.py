"""
This file is part of "imapdiag".

Copyright © 2020 Ralph Seichter
"""
from imaplib import IMAP4
from imaplib import IMAP4_SSL
from logging import Logger
from re import IGNORECASE
from re import Pattern
from re import compile
from ssl import CERT_NONE
from ssl import SSLContext
from typing import List

from imapdiag.database import Session
from imapdiag.database import scan_result
from imapdiag.logger import get_logger

MID_RE = compile(r'MESSAGE-ID:\s+([\S]+)', IGNORECASE)
UID_RE = compile(r'UID\s+([\S]+)', IGNORECASE)
UTF_8 = 'utf-8'


def needs_processing(mailbox: str, exclude: Pattern, include: Pattern) -> bool:
    return exclude.search(mailbox) is None and include.search(mailbox) is not None


def ssl_context() -> SSLContext:
    context = SSLContext()
    context.load_default_certs()
    context.check_hostname = False
    context.verify_mode = CERT_NONE
    return context


def mailbox_name(name: bytes) -> str:
    s = name.decode(UTF_8)
    if s.endswith('"'):
        s = s[::-1]
        i = s.index('"', 1)
        s = s[:i + 1]
        s = s[::-1]
    else:
        s = s.split(' ')[2]
    return s


class IMAPClient(IMAP4_SSL):
    exclude: Pattern
    include: Pattern
    log: Logger
    other_client: str = None
    search_term: str
    selected_mailbox: str = None
    user: str

    def __init__(self, address: str, search_term: str, exclude: Pattern, include: Pattern) -> None:
        self.search_term = search_term
        self.exclude = exclude
        self.include = include
        self.log = get_logger()
        host = address.split(':')
        if len(host) > 1:
            port = int(host[1])
        else:
            port = 993
        self.log = get_logger()
        self.log.debug(f'Host {host[0]}:{port}')
        super().__init__(host=host[0], port=port, ssl_context=ssl_context())

    def connect(self, args) -> None:
        self.user = args.user
        self.log.debug(f'Login {self.user}')
        status, data = self.login(self.user, args.password)
        self.log.debug(f'{status} {self.state}')
        self.enable('UTF8=ACCEPT')

    def disconnect(self) -> None:
        if self.selected_mailbox is not None:
            self.close()
        self.logout()

    def mailboxes(self) -> List[str]:
        result = list()
        if needs_processing('INBOX', self.exclude, self.include):
            result.append('INBOX')
        status, data = self.lsub()
        for d in data:
            mailbox = mailbox_name(d)
            if (mailbox not in result) and needs_processing(mailbox, self.exclude, self.include):
                result.append(mailbox)
        return result

    def select_readonly(self, mailbox: str):
        if mailbox != self.selected_mailbox:
            self.selected_mailbox = mailbox
            return self.select(mailbox=mailbox, readonly=True)
        return None, None

    def compare_accounts(self, other_client) -> int:
        self.other_client = other_client
        return self.scan_account()

    def scan_account(self) -> int:
        mismatch_count = 0
        for mailbox in self.mailboxes():
            status, data = self.select_readonly(mailbox)
            message_count = int(data[0])
            self.log.debug(f'{mailbox} {message_count}')
            mismatch_count += self._scan_mailbox(mailbox)
        if mismatch_count > 0:
            self.log.warning(f'Total mismatch count: {mismatch_count}')
        else:
            self.log.info('Comparison successful')
        return mismatch_count

    def _scan_mailbox(self, mailbox: str) -> int:
        status, data = self.search(None, self.search_term)
        session = Session()
        row_count = mismatch_count = 0
        for num in data[0].split():
            status, data = self.fetch(num, '(UID BODY[HEADER.FIELDS (MESSAGE-ID)])')
            if not (isinstance(data, list) and len(data) > 1):
                self.log.error(f'Unexpected fetch result: {status} {data}')
                mismatch_count += 1
                continue
            x = data[0][0].decode(UTF_8)
            match = UID_RE.search(x)
            uid = match[1]
            x = data[0][1].decode(UTF_8)
            match = MID_RE.search(x)
            if match and match[1]:
                mid = match[1]
            else:
                self.log.error(f'Missing message ID for UID {uid}')
                mid = None
            sr = scan_result(self.host, self.user, mailbox, uid, mid)
            if mid and isinstance(self.other_client, IMAPClient):
                sr.otherhost = self.other_client.host
                sr.found = self.other_client._mid_exists(mid, mailbox)
                if not sr.found:
                    mismatch_count += 1
            session.add(sr)
            row_count += 1
        if row_count > 0:
            session.commit()
        if mismatch_count > 0:
            self.log.warning(f'Mismatch count: {mailbox} {mismatch_count}')
        return mismatch_count

    def _mid_exists(self, mid: str, mailbox: str) -> bool:
        try:
            self.select_readonly(mailbox)
            status, data = self.search(None, f'HEADER MESSAGE-ID {mid}')
            return len(data[0]) > 0
        except IMAP4.error as e:
            self.log.exception(e)
        return False
