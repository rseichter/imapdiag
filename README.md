# imapdiag
Copyright © 2020 Ralph Seichter

Compare message IDs across server pairs to verify replication success.
Requires Python 3.7 or newer.
```
usage: imapdiag [-h] [-c] [-f FILTER] [-m REGEX] [-x REGEX] [-l LEVEL]
                [-s URL] [-u USER] [-p PASSWORD]
                server [server ...]

IMAP server diagnostics

positional arguments:
  server       IMAP server

optional arguments:
  -h, --help   show this help message and exit
  -c           Clear database on startup
  -f FILTER    IMAP search filter (default: UNDELETED)
  -m REGEX     Mailbox include regex (default: ^INBOX$)
  -x REGEX     Mailbox exclude regex (default: see documentation)
  -l LEVEL     Log level (default: DEBUG)
  -s URL       SQLAlchemy database URL (default: sqlite:///:memory:)
  -u USER      User name
  -p PASSWORD  Password
```

## Default installation
```
python3.7 -m venv venv
source venv/bin/activate
pip install imapdiag
```
## Alternative: Ubuntu 18 LTS without "pip"
Download the source distribution file imapdiag-VERSION.tar.gz from [PyPI.org](https://pypi.org/project/imapdiag/#files)
```
sudo apt install python3.7 python3.7-venv python3-sqlalchemy sqlite3
tar xzf /path/to/imapdiag-VERSION.tar.gz
cd imapdiag-VERSION
alias imapdiag="PYTHONPATH=. python3.7 -m imapdiag"
```

## Mode of operation
* If only one server is specified, _imapdiag_ will execute a scan of that server and exit.
This can be used for connection testing.

* If two servers are specified, _imapdiag_ compares message IDs for the specified IMAP account and
mailboxes across both servers.

* If three or more servers are specified, _imapdiag_ will compare message IDs on server1 with server2,
then compare server1 with server3, and so forth.

## Database configuration
Detailed information about SQLAlchemy URLs and supported database dialects is available
[here](https://docs.sqlalchemy.org/en/13/core/engines.html).
_Imapdiag_ will attempt to create missing databases and the necessary structure.
This usually works well when using SQLite, but may fail with other database types.

## Server names and ports
Server names can be specified as fully qualified names or IP addresses.
An optional colon and a port number can be added, e.g. `imapserver.domain.tld:567`.
The default is TCP port 993 (imaps).

## Argument files
You can specify arguments on the command line and/or in files.
The latter can be referenced using the `@` character prefix.
When using files, argument keys and values must be specified on separate lines:
```
-s
sqlite:////tmp/imapdiag.db
-l
INFO
-f
UNDELETED SINCE 01-Mar-2020
-p
MASTERPASSWORD
server1.domain.tld
server2.otherdomain.tld
```
If you choose to save password data in a file, make very sure to restrict access.
Specifying passwords on the command line is not a safer option, because other users on the machine
may be able to inspect process arguments.

Assuming you have stored this configuration in the file `/tmp/args`, you can call the utility as follows:
```
imapdiag @/tmp/args -u janedoe*MASTERUSER
```

## Specifying mailbox names
Exclusion and inclusion of mailbox names is specified using case-insensitive Python 3
[regular expressions](https://docs.python.org/3/howto/regex.html#regex-howto).
Make sure to quote expressions as required by your shell.
To include all subscribed mailboxes of an IMAP account, use `-m .` (a single dot, not an asterisk).
The default exclusion RE is this:
```
(Deleted|Draft|Entw[uü]rf|Gelöscht|Junk|Papierkorb|Spam|Template|Trash|Vorlage)
```
Note that exclusion has higher priority than inclusion.
