# copyright 2003-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr

"""cubicweb-nazcaui startup views ils for web ui"""
import threading

from rdflib import Namespace as RdfNamespace, Graph as RdfGraph, \
     URIRef

from logilab.mtconverter import xml_escape

from cubicweb.predicates import anonymous_user

from cubicweb.view import StartupView
from cubicweb.web.views.startup import IndexView
from cubicweb.web.httpcache import NoHTTPCacheManager
from cubicweb.web.views.csvexport import CSVMixIn
from cubicweb.web.views.json import JsonMixIn

from cubes.nazcaui.views.utils import OUTPUTS, parseindexes, run_nazca

RDF = RdfNamespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
CW = RdfNamespace('http://ns.cubicweb.org/cubicweb/0.0/')
OWL = RdfNamespace('http://www.w3.org/2002/07/owl#')

class ResultsView(StartupView):
    __regid__ = 'nazca-results'

    def call(self, rset=None, **kwargs):
        _ = self._cw._
        threading.Thread(target=run_nazca, args=(self._cw,)).start()
        self.w(u'<h1>%s</h1>' % _('Alignment process started'))
        self._cw.add_onload('cw.cubes.nazca.setLanguage("%s"); cw.cubes.nazca.checkProgress("#progresslist")' %
                            self._cw.lang)
        self.w(u'<ul id="progresslist">')
        self.w(u'</ul>')


class AdminResultsView(StartupView):
    __select__ = ResultsView.__select__ & ~anonymous_user()

    def call(self, rset=None, **kwargs):
        super(AdminResultsView, self).call(rset)
        self.w(u'<a href="%s" class="btn btn-large">%s</a>'
               % (self._cw.base_url()+'?vid=nazca-save', self._cw._('Save the alignment')))


class SaveNazcaView(StartupView):
    __regid__ = 'nazca-save'
    http_cache_manager =  NoHTTPCacheManager

    def call(self, rset=None, **kwargs):
        if 'align_data' not in self._cw.session.data:
            self.w(u'An error occured - The process can not be saved')
            return
        (align_dict, align_parameters) = self._cw.session.data['align_data']
        align_entity = self._cw.create_entity('NazcaAlignment', **align_dict)
        for param in align_parameters:
            param_entity = self._cw.create_entity('AlignmentParameter', **param)
            align_entity.set_relations(alignment_parameters=param_entity.eid)
        self.w(u'<a href="%s">See the created entity</a>' % align_entity.absolute_url())


class HtmlResultsView(StartupView):
    __regid__ = 'nazca-html-results'
    http_cache_manager =  NoHTTPCacheManager

    def call(self, rset=None, **kwargs):
        data = self._cw.session.data['results']
        self.w(u'<table class="table table-condensed table-bordered table-hover">')
        self.w(u'<thead><tr><td colspan="%s">The Results</td></tr></thead>'
               % len(data))
        self.w(u'<tbody>')
        for line in sorted(data, key=lambda x:x[1]):
            if line[-1] == u'not_found':
                self.w(u'<tr class="error">')
            else:
                self.w(u'<tr class="success">')
            for elt in line:
                if isinstance(elt, basestring) and (elt.startswith('http://') or
                                                    elt.startswith('www.')):
                    self.w(u'<td><a href="%(e)s">%(e)s</a></td>'
                           % {'e': _(elt)})
                else:
                    self.w(u'<td>%s</td>' % _(elt))
            self.w(u'</tr>')
        self.w(u'</tbody>')
        self.w(u'</table>')

class CsvResultsView(CSVMixIn, StartupView):
    __regid__ = 'nazca-csv-results'

    def call(self, rset=None, **kwargs):
        data = self._cw.session.data['results']
        writer = self.csvwriter()
        for line in data:
            writer.writerow(line)

class JsonResultsView(JsonMixIn, StartupView):
    __regid__ = 'nazca-json-results'

    def call(self, rset=None, **kwargs):
        data = self._cw.session.data['results']
        self.wdata(data)

class RdfResultsView(CSVMixIn, StartupView):
    __regid__ = 'nazca-rdf-results'
    content_type = 'text/xml' # +rdf

    def call(self, rset=None, **kwargs):
        graph = RdfGraph()
        graph.bind('cw', CW)
        graph.bind('owl', OWL)
        data = self._cw.session.data['results']
        writer = self.csvwriter(**{'delimiter': ' '})
        for line in data:
            if line[-1] == 'not_found':
                continue
            graph.add( (URIRef(line[0]), OWL.sameAs, URIRef(line[-1])) )
        self.w(graph.serialize().decode('utf-8'))

class NazcaIndexView(IndexView):

    def call(self, **kwargs):
        card = self._cw.execute('Any X WHERE X is Card, X title "index"')
        if card:
            self.w(card.get_entity(0, 0).content)
        # rset = self._cw.execute('Any X ORDERBY D DESC WHERE X is NazcaAlignment, '
        #                         'NOT X name NULL, X creation_date D')
        # if len(rset):
        #     self.w(u'<h3>Recent alignments</h3>')
        #     self.w(u'<ul>')
        #     for entity in rset.entities():
        #         self.w(u'<li><a href="%s">%s</a></li>' %
        #                (entity.absolute_url(), entity.name))
        #     self.w(u'</ul>')
        self.w(u'<a href="%s" class="btn btn-large">%s</a>'
               % (xml_escape(self._cw.build_url(vid='nazca')),
                  xml_escape(self._cw._('Start a new alignment !'))))

def registration_callback(vreg):
    vreg.unregister(IndexView)
    vreg.register_all(globals().values(), __name__, ())
