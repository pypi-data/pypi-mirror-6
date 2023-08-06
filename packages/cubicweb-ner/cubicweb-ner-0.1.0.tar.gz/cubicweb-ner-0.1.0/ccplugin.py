import re
import os.path as osp
from string import punctuation
import codecs

from logilab.common.textutils import unormalize

from cubicweb import AuthenticationError
from cubicweb import cwconfig
from cubicweb.server.utils import manager_userpasswd
from cubicweb.dbapi import in_memory_repo_cnx
from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL

from cubes.dataio.dataimport import MassiveObjectStore


def _init_cw_connection(appid):
    config = cwconfig.instance_configuration(appid)
    sourcescfg = config.sources()
    config.set_sources_mode(('system',))
    cnx = repo = None
    while cnx is None:
        try:
            login = sourcescfg['admin']['login']
            pwd = sourcescfg['admin']['password']
        except KeyError:
            login, pwd = manager_userpasswd()
        try:
            repo, cnx = in_memory_repo_cnx(config, login=login, password=pwd)
        except AuthenticationError:
            print 'wrong user/password'
        else:
            break
    session = repo._get_session(cnx.sessionid)
    return cnx, session

def normalize_string(title, _transmap={}):
    if not _transmap:
        for i in xrange(2**16-1):
            newc = unormalize(unichr(i), substitute='_')
            if len(newc) == 1:
                _transmap[i] = ord(newc)
            else:
                _transmap[i] = newc
        for punc in punctuation:
            _transmap[ord(punc)] = u' '
    # lxml returns raw string if it contains only ascii characters
    if isinstance(title, str):
        title = unicode(title)
    title = title.translate(_transmap)
    title = u' '.join([t.strip() for t in title.split()])
    title = title.lower().strip()
    # Deal with non latin alphabet, if we have only space and _
    if title.strip(' _'):
        return title
    return ''


class NerImportDbpedia(Command):
    """
    Command for importing dbpedia in NER. File SHOULD be in NT format.
    """
    arguments = '<instance> <file>'
    name = 'ner-import-dbpedia'
    min_args = 2
    options = [('name', {'type': 'string', 'type': 'string',
                         'default': 'dbpedia',
                         'help': "Name of the source",}),]

    def run(self, args):
        appid = args.pop(0)
        cw_cnx, session = _init_cw_connection(appid)
        session.set_pool()
        filename = args.pop(0)
        if not osp.exists(filename):
            print 'Filename %s does not exists' % filename
            return
        ner_source = session.create_entity('NerSource', name=unicode(self.config.name))
        store = MassiveObjectStore(session, autoflush_metadata=False,
                                   replace_sep=u' ', build_entities=False)
        # XXX Use dataio.interfaces ? We need the languages...
        regexp = re.compile(r'^<(.*)>\s+<(.*)>\s+"(.*)"(\@.*)*\s*.\s*')
        # Parse file
        for ind, line in enumerate(open(filename)):
            if line:
                match = regexp.match(line)
                if match:
                    data = [m.decode('utf-8').strip() for m in match.groups()]
                    label = data[2]
                    label = codecs.unicode_escape_decode(label)[0]
                    unormalize_label=normalize_string(label)
                    store.create_entity('NerEntry', label=label, cwuri=data[0],
                                        unormalize_label=unormalize_label,
                                        lang=data[3].replace('@', ''),
                                        weight=1, ner_source=ner_source.eid)
            if ind and ind % 100000 == 0:
                print 'Flushing'
                store.flush()
        # Final flush
        store.flush()
        print 'Start flush metadata'
        store.flush_meta_data()
        store.cleanup()


CWCTL.register(NerImportDbpedia)
