import os
import pexpect
from pathlib import Path

class OTHEREXCEPTION(pexpect.ExceptionPexpect):
    '''Raised when a read time exceeds the timeout. '''

class NOTFOUND(Exception):
    ''' '''

class INode(int):
    ''''''

class FilePath(str):
    ''''''

def raiseIfError(error, type):
    if error is not None:
        raise type

class FileSpec:
    def __init__(self, path: str, lsLine: str):
        splitted = lsLine.split('\t')
        self.inode = int(splitted[0])
        self.__type = splitted[1].strip()
        if self.__type[0] == 4:
            self.type = "DIR"
        if self.__type[0] == "1" and self.__type[1] == "0":
            self.type = "FILE"
        else:
            self.type = "OTHER"
        
        self.filename = Path.joinpath(path, splitted[6].strip())
    
    def __str__(self):
        return self.filename

class DebugFs:
    def __init__(self):
        self.proc = pexpect.spawn('debugfs', timeout=600, env= os.environ | { "DEBUGFS_PAGER": "less -FX" })
        

    def __execCommand(self, command: str, timeout: int = -1) -> list[str]:
        self.proc.sendline(command)
        response = self.proc.expect([command, pexpect.EOF, pexpect.TIMEOUT], timeout)
        if response == 0:
            response = self.proc.expect(["debugfs:", pexpect.EOF, pexpect.TIMEOUT])

        if response == 0:
            return self.proc.before.decode("utf-8"), None
        if response == 1:
            return None, pexpect.EOF
        if response == 2:
            return None, pexpect.TIMEOUT
        return None, OTHEREXCEPTION

    def open(self, device: str) -> bool:
        (result, error) = self.__execCommand(f"open {device}")
        return error is not None
    
    def icheck(self, sector: str) -> INode:
        (result, error) = self.__execCommand(f"icheck {sector}")
        raiseIfError(error, NOTFOUND)
        return int(result)
    
    def ncheck(self, node: INode) -> FilePath:
        (result, error) = self.__execCommand(f"ncheck {node}")
        raiseIfError(error, NOTFOUND)
        return result
    
    def ls(self, path: str) -> list[FileSpec]:
        (result, error) = self.__execCommand(f"ls -l {path}")
        raiseIfError(error, NOTFOUND)
        lines = result.splitlines()
        return map(lambda x: FileSpec(x), lines)

    def blocks(self, filespec: FileSpec) -> list[int]:
        (result, error) = self.__execCommand(f"blocks {filespec.filename}")
        raiseIfError(error, NOTFOUND)
        return map(lambda x: int(x), result.split(" "))

