import sys, shutil, os
PY3K = sys.version_info >= (3, 0)
import urllib.request as ulib
import urllib.parse as urlparse
import math






def bar_thermometer(current, total, width=80):
    avail_dots = width-2
    shaded_dots = int(math.floor(float(current) / total * avail_dots))
    return '[' + '.'*shaded_dots + ' '*(avail_dots-shaded_dots) + ']'





def to_unicode(filename):
    if PY3K:
        return filename
    else:
       return ("version error")

def filename_from_url(url):
   
    
    fname = os.path.basename(urlparse.urlparse(url).path)
    if len(fname.strip(" \n\t.")) == 0:
        return None
    return to_unicode(fname)


def filename_from_headers(headers):
    
    if type(headers) == str:
        headers = headers.splitlines()
    if type(headers) == list:
        headers = dict([x.split(':', 1) for x in headers])
    cdisp = headers.get("Content-Disposition")
    if not cdisp:
        return None
    cdtype = cdisp.split(';')
    if len(cdtype) == 1:
        return None
    if cdtype[0].strip().lower() not in ('inline', 'attachment'):
        return None
    
    fnames = [x for x in cdtype[1:] if x.strip().startswith('filename=')]
    if len(fnames) > 1:
        return None
    name = fnames[0].split('=')[1].strip(' \t"')
    name = os.path.basename(name)
    if not name:
        return None
    return name