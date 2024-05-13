import os
import pexpect
import pathlib
import argparse
from lib.debugfs import DebugFs

parser = argparse.ArgumentParser(
    prog="DebugFS Wrapper",
    description="Opens a session with DebugFS to discover which files on the disk are broken"
)

parser.add_argument('diskname', dest="diskname",  action='store_const')
parser.add_argument('path', '--path', dest="path", action='store_const', default="/")
args = parser.parse_args(["diskname", "path"])

dfs = DebugFs()
dfs.open(args.diskname)

def readFileList(path:str, soFar: list[int] = []):
    try:
        folders = dfs.ls(args.path)
        for folder in folders:
            if folder.type == "DIR" and not folder.filename.startswith("."):
                readFileList(folder.filename, soFar)
    except Exception as e:
        print(f"Caught error {e}")
    finally:
        return soFar

files = readFileList(args.path)
