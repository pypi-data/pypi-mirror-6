
from cubicweb import AuthenticationError
from cubicweb import cwconfig
from cubicweb.server.utils import manager_userpasswd
from cubicweb.dbapi import in_memory_repo_cnx
from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL

from cubicweb.dataimport import SQLGenObjectStore

from nerdy import core


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

def process_nerdy_article(session, store, article, current_uris, verbose=False):
    """ Process an article with nerdy """
    lang = article.source[0].lang or 'fr'
    comps = [comp(session) for comp in session.vreg['nerdy-source'].all_objects()
             if  comp(session).lang == lang]
    sources = [c.get_nerdy_source() for c in comps if c.get_nerdy_source()]
    if not sources:
        return
    # Nerdy
    filters = comps[0].get_filters()
    preprocessors = list(comps[0].get_preprocessors())
    if article.__regid__ == 'Tweet':
        preprocessors.append(core.NerdyHashTagPreprocessor())
    nerdy = core.NerdyProcess(sources, preprocessors=preprocessors,
                              filters=filters, unique=True)
    seen_uris = set([r[0] for r in session.execute('Any U WHERE X eid %(e)s, '
                                                   'X recognized_entities E, E uri U',
                                                   {'e': article.eid})])
    named_entities = nerdy.process_text(article.text_content)
    # Push URIs
    sentences = {}
    for uri in set([u for u, p, t in named_entities]):
        if verbose:
            print repr(uri)
        if uri in current_uris:
            current_uri_eid = current_uris[uri]
        else:
            current_uri_eid = store.create_entity('ExternalUri',
                                                  activated=True,
                                                  cwuri=unicode(uri),
                                                  uri=unicode(uri)).eid
            current_uris[uri] = current_uri_eid
        if uri not in seen_uris:
            store.relate(article.eid, 'recognized_entities', current_uri_eid)
            seen_uris.add(uri)
        sentences.setdefault(t.sentence, []).append(current_uri_eid)
    # Push sentences
    for sentence, eids in sentences.iteritems():
        sentence_eid = store.create_entity('Sentence',
                                           indice=sentence.indice,
                                           start=sentence.start,
                                           stop=sentence.end).eid
        store.relate(article.eid, 'sentences', sentence_eid)
        for eid in eids:
            store.relate(sentence_eid, 'found_entities', eid)
    store.rql('SET X processed TRUE WHERE X eid %(e)s', {'e': article.eid})


class SemnewsProcessNERArticle(Command):
    """
    Command for processing NER in Semnews
    """
    arguments = '<instance>'
    name = 'process-ner'

    def run(self, args):
        appid = args.pop(0)
        cw_cnx, session = _init_cw_connection(appid)
        session.set_pool()
        # Import
        store = SQLGenObjectStore(session)
        current_uris = dict(session.execute('Any U,X WHERE X is ExternalUri, X uri U'))
        articles_rset = session.execute('Any N WHERE N is IN (NewsArticle, Tweet), N processed False')
        for ind, article in enumerate(articles_rset.entities()):
            print 80*'*'
            print '--->', ind
            process_nerdy_article(session, store, article, current_uris, verbose=True)
            if ind and ind % 100 == 0:
                try:
                    store.flush()
                except:
                    return
        # Final flush
        store.flush()
        store.commit()


CWCTL.register(SemnewsProcessNERArticle)
