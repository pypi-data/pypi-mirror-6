import json
import urllib.request, urllib.parse
from . import __version__

HEADERS = {"User-Agent": "dnasnout-client-v{0}".format(__version__)}

class Results(object):
    """ Results from a DNAsnout server. """
    def __init__(self, 
                 fileinfo,
                 matches,
                 maxupload):
        _d = dict()
        _d['fileinfo'] = fileinfo
        _d['matches'] = matches
        _d['maxupload'] = maxupload
        self._d = _d

    def json(self):
        return jsonify(fileinfo = self.fileinfo,
                       matches = self.matches,
                       maxupload = self.maxupload)

    matches = property(lambda x: x._d['matches'],
                       None, None,
                       'Matching references')
    
    @classmethod
    def from_json(cls, jsonstring):
        data = json.loads(jsonstring)
        return cls(data['fileinfo'],
                   data['matches'],
                   data['maxupload'])

def list_asfasta(lst):
    """ Turn a list of Entry objects into a FASTA string """
    return b'\n'.join(b'\n'.join((b'>'+x.header[1:], x.sequence)) for x in lst)

def sniff_samples(dnareads, 
                  server = "http://tapir.cbs.dtu.dk", 
                  timeout = 30):
    """ Query a dnasnout server (such as Tapir).

    :param reads: an iterable of objects with attributes 'sequence' 
                  and 'quality' 
    :param timeout: timeout in seconds
    """

    q = {'sequences': list_asfasta(dnareads), 'refid_ignore': list()}
    req = urllib.request.Request(server + '/_sniff_paste',
                                 urllib.parse.urlencode(q).encode('ASCII'),
                                 HEADERS)

    con = urllib.request.urlopen(req, timeout=timeout)
    jsonstring = con.read().decode('ASCII')
    con.close()
    return Results.from_json(jsonstring)

