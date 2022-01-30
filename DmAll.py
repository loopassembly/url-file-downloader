from  filelogs.filee import filename_from_headers,to_unicode,filename_from_url,bar_thermometer
import sys, shutil, os
import tempfile
import math

PY3K = sys.version_info >= (3, 0)
if PY3K:
  import urllib.request as ulib
  import urllib.parse as urlparse
else:
  import urllib as ulib


__version__ = "3.2"

def bar_thermometer(current, total, width=80):
    avail_dots = width-2
    shaded_dots = int(math.floor(float(current) / total * avail_dots))
    return '[' + '.'*shaded_dots + ' '*(avail_dots-shaded_dots) + ']'

def bar_adaptive(current, total, width=80):
 

    
    if not total or total < 0:
        msg = "%s / unknown" % current
        if len(msg) < width:    
            return msg
        if len("%s" % current) < width:
            return "%s" % current

  

    min_width = {
      'percent': 4,  
      'bar': 3,    
      'size': len("%s" % total)*2 + 3, 
    }
    priority = ['percent', 'bar', 'size']

    
    selected = []
    avail = width
    for field in priority:
      if min_width[field] < avail:
        selected.append(field)
        avail -= min_width[field]+1   
                               

    output = ''
    for field in selected:

      if field == 'percent':
        
        output += ('%s%%' % (100 * current // total)).rjust(min_width['percent'])
      elif field == 'bar':  
        
        output += bar_thermometer(current, total, min_width['bar']+avail)
      elif field == 'size':
        
        output += ("%s / %s" % (current, total)).rjust(min_width['size'])

      selected = selected[1:]
      if selected:
        output += ' '  

    return output



#filelogs###############################################################################################################

def detect_filename(url=None, out=None, headers=None, default="download.wget"):
   
    names = dict(out='', url='', headers='')
    if out:
        names["out"] = out or ''
    if url:
        names["url"] = filename_from_url(url) or ''
    if headers:
        names["headers"] = filename_from_headers(headers) or ''
    return names["out"] or names["headers"] or names["url"] or default




def get_console_width():
   

    if os.name == 'nt':
        STD_INPUT_HANDLE  = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE  = -12

        
        from ctypes import windll, Structure, byref
        try:
            from ctypes.wintypes import SHORT, WORD, DWORD
        except ImportError:
            
            from ctypes import (
                c_short as SHORT, c_ushort as WORD, c_ulong as DWORD)
        console_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        
        class COORD(Structure):
            _fields_ = [("X", SHORT), ("Y", SHORT)]

        class SMALL_RECT(Structure):
            _fields_ = [("Left", SHORT), ("Top", SHORT),
                        ("Right", SHORT), ("Bottom", SHORT)]

        class CONSOLE_SCREEN_BUFFER_INFO(Structure):
            _fields_ = [("dwSize", COORD),
                        ("dwCursorPosition", COORD),
                        ("wAttributes", WORD),
                        ("srWindow", SMALL_RECT),
                        ("dwMaximumWindowSize", DWORD)]

        sbi = CONSOLE_SCREEN_BUFFER_INFO()
        ret = windll.kernel32.GetConsoleScreenBufferInfo(
            console_handle, byref(sbi))
        if ret == 0:
            return 0
        return sbi.srWindow.Right+1

    elif os.name == 'posix':
        from fcntl import ioctl
        from termios import TIOCGWINSZ
        from array import array

        winsize = array("H", [0] * 4)
        try:
            ioctl(sys.stdout.fileno(), TIOCGWINSZ, winsize)
        except IOError:
            pass
        return (winsize[1], winsize[0])[0]

    return 80
__current_size = 0

def callback_progress(blocks, block_size, total_size, bar_function):
   
    global __current_size
 
    width = min(100, get_console_width())

    if sys.version_info[:3] == (3, 3, 0):  
        if blocks == 0:  
            __current_size = 0
        else:
            __current_size += block_size
        current_size = __current_size
    else:
        current_size = min(blocks*block_size, total_size)
    progress = bar_function(current_size, total_size, width)
    if progress:
        sys.stdout.write("\r" + progress)

def filename_fix_existing(filename):
    
    dirname = u'.'
    name, ext = filename.rsplit('.', 1)
    names = [x for x in os.listdir(dirname) if x.startswith(name)]
    names = [x.rsplit('.', 1)[0] for x in names]
    suffixes = [x.replace(name, '') for x in names]
    
    suffixes = [x[2:-1] for x in suffixes
                   if x.startswith(' (') and x.endswith(')')]
    indexes  = [int(x) for x in suffixes
                   if set(x) <= set('0123456789')]
    idx = 1
    if indexes:
        idx += sorted(indexes)[-1]
    return '%s (%d).%s' % (name, idx, ext)

def download(url, out=None, bar=bar_adaptive):
    
    
    outdir = None
    if out and os.path.isdir(out):
        outdir = out
        out = None

    
    prefix = detect_filename(url, out)
    (fd, tmpfile) = tempfile.mkstemp(".tmp", prefix=prefix, dir=".")
    os.close(fd)
    os.unlink(tmpfile)

    
    def callback_charged(blocks, block_size, total_size):
        
        callback_progress(blocks, block_size, total_size, bar_function=bar)
    if bar:
        callback = callback_charged
    else:
        callback = None

    if PY3K:
        
        binurl = list(urlparse.urlsplit(url))
        binurl[2] = urlparse.quote(binurl[2])
        binurl = urlparse.urlunsplit(binurl)
    else:
        binurl = url
    (tmpfile, headers) = ulib.urlretrieve(binurl, tmpfile, callback)
    filename = detect_filename(url, out, headers)
    if outdir:
        filename = outdir + "/" + filename

    
    if os.path.exists(filename):
        filename = filename_fix_existing(filename)
    shutil.move(tmpfile, filename)

    
    return filename


usage = """\
usage: wget.py [options] URL

options:
  -o --output FILE|DIR   output filename or directory
  -h --help
  --version
"""
def win32_utf8_argv():
    from ctypes import POINTER, byref, cdll, c_int, windll
    from ctypes.wintypes import LPCWSTR, LPWSTR

    GetCommandLineW = cdll.kernel32.GetCommandLineW
    GetCommandLineW.argtypes = []
    GetCommandLineW.restype = LPCWSTR

    CommandLineToArgvW = windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
    CommandLineToArgvW.restype = POINTER(LPWSTR)

    cmd = GetCommandLineW()
    argc = c_int(0)
    argv = CommandLineToArgvW(cmd, byref(argc))
    argnum = argc.value
    sysnum = len(sys.argv)
    result = []
    if argnum > 0:
        
        start = argnum - sysnum
        for i in range(start, argnum):
            result.append(argv[i].encode('utf-8'))
    return result




def win32_unicode_console():
    import codecs
    from ctypes import WINFUNCTYPE, windll, POINTER, byref, c_int
    from ctypes.wintypes import BOOL, HANDLE, DWORD, LPWSTR, LPCWSTR, LPVOID

    original_stderr = sys.stderr

    
    def _complain(message):
        original_stderr.write(message if isinstance(message, str) else repr(message))
        original_stderr.write('\n')

    codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

    try:
        GetStdHandle = WINFUNCTYPE(HANDLE, DWORD)(("GetStdHandle", windll.kernel32))
        STD_OUTPUT_HANDLE = DWORD(-11)
        STD_ERROR_HANDLE = DWORD(-12)
        GetFileType = WINFUNCTYPE(DWORD, DWORD)(("GetFileType", windll.kernel32))
        FILE_TYPE_CHAR = 0x0002
        FILE_TYPE_REMOTE = 0x8000
        GetConsoleMode = WINFUNCTYPE(BOOL, HANDLE, POINTER(DWORD))(("GetConsoleMode", windll.kernel32))
        INVALID_HANDLE_VALUE = DWORD(-1).value

        def not_a_console(handle):
            if handle == INVALID_HANDLE_VALUE or handle is None:
                return True
            return ((GetFileType(handle) & ~FILE_TYPE_REMOTE) != FILE_TYPE_CHAR
                    or GetConsoleMode(handle, byref(DWORD())) == 0)

        old_stdout_fileno = None
        old_stderr_fileno = None
        if hasattr(sys.stdout, 'fileno'):
            old_stdout_fileno = sys.stdout.fileno()
        if hasattr(sys.stderr, 'fileno'):
            old_stderr_fileno = sys.stderr.fileno()

        STDOUT_FILENO = 1
        STDERR_FILENO = 2
        real_stdout = (old_stdout_fileno == STDOUT_FILENO)
        real_stderr = (old_stderr_fileno == STDERR_FILENO)

        if real_stdout:
            hStdout = GetStdHandle(STD_OUTPUT_HANDLE)
            if not_a_console(hStdout):
                real_stdout = False

        if real_stderr:
            hStderr = GetStdHandle(STD_ERROR_HANDLE)
            if not_a_console(hStderr):
                real_stderr = False

        if real_stdout or real_stderr:
            WriteConsoleW = WINFUNCTYPE(BOOL, HANDLE, LPWSTR, DWORD, POINTER(DWORD), LPVOID)(("WriteConsoleW", windll.kernel32))

            class UnicodeOutput:
                def __init__(self, hConsole, stream, fileno, name):
                    self._hConsole = hConsole
                    self._stream = stream
                    self._fileno = fileno
                    self.closed = False
                    self.softspace = False
                    self.mode = 'w'
                    self.encoding = 'utf-8'
                    self.name = name
                    self.flush()

                def isatty(self):
                    return False

                def close(self):
                    
                    self.closed = True

                def fileno(self):
                    return self._fileno

                def flush(self):
                    if self._hConsole is None:
                        try:
                            self._stream.flush()
                        except Exception as e:
                            _complain("%s.flush: %r from %r" % (self.name, e, self._stream))
                            raise

                def write(self, text):
                    try:
                        if self._hConsole is None:
                            if  PY3K and isinstance(text, str):
                                text = text.encode('utf-8')
                            
                            
                            self._stream.write(text)
                        else:
                            if PY3K and not isinstance(text, str):
                                text = text.decode('utf-8')
                            
                            
                            remaining = len(text)
                            while remaining:
                                n = DWORD(0)
                                
                                
                                
                                retval = WriteConsoleW(self._hConsole, text, min(remaining, 10000), byref(n), None)
                                if retval == 0 or n.value == 0:
                                    raise IOError("WriteConsoleW returned %r, n.value = %r" % (retval, n.value))
                                remaining -= n.value
                                if not remaining:
                                    break
                                text = text[n.value:]
                    except Exception as e:
                        _complain("%s.write: %r" % (self.name, e))
                        raise

                def writelines(self, lines):
                    try:
                        for line in lines:
                            self.write(line)
                    except Exception as e:
                        _complain("%s.writelines: %r" % (self.name, e))
                        raise

            if real_stdout:
                sys.stdout = UnicodeOutput(hStdout, None, STDOUT_FILENO, '<Unicode console stdout>')
            else:
                sys.stdout = UnicodeOutput(None, sys.stdout, old_stdout_fileno, '<Unicode redirected stdout>')

            if real_stderr:
                sys.stderr = UnicodeOutput(hStderr, None, STDERR_FILENO, '<Unicode console stderr>')
            else:
                sys.stderr = UnicodeOutput(None, sys.stderr, old_stderr_fileno, '<Unicode redirected stderr>')
    except Exception as e:
        _complain("exception %r while fixing up sys.stdout and sys.stderr" % (e,))



if __name__ == "__main__":
    if len(sys.argv) < 2 or "-h" in sys.argv or "--help" in sys.argv:
        sys.exit(usage)
    if "--version" in sys.argv:
        sys.exit("wget.py " + __version__)

    
    if not PY3K and sys.platform == "win32":
        sys.argv = win32_utf8_argv()
    
    if sys.platform == "win32":
        win32_unicode_console()

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="output")
    (options, args) = parser.parse_args()

    url = sys.argv[1]
    filename = download(args[0], out=options.output)

    print("")
    print("Saved under %s" % filename)


