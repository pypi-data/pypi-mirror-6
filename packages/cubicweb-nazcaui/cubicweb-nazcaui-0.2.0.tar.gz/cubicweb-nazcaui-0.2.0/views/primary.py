# copyright 2003-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr

"""cubicweb-nazcaui primary views"""
from cubicweb.predicates import is_instance

from cubicweb.web.views.primary import PrimaryView
from cubicweb.view import EntityView


class NazcaAlignmentPrimaryView(PrimaryView):
    __select__ = PrimaryView.__select__ & is_instance('NazcaAlignment')

    def entity_call(self, entity):
        entity = self.cw_rset.get_entity(0, 0)
        super(NazcaAlignmentPrimaryView, self).entity_call(entity)
        entity = self.cw_rset.get_entity(0, 0)
        self.w(u'<a href="%s" class="btn btn-large">%s</a>'
               % (self._cw.build_url(vid='relaunch-nazca',
                                     rql='Any X WHERE X eid %s' % entity.eid),
                  self._cw._('Relaunch alignment')))

class NazcaRelaunchAlignmentPrimaryView(EntityView):
    __regid__ = 'relaunch-nazca'
    __select__ = EntityView.__select__ & is_instance('NazcaAlignment')

    def call(self, rset=None, **kwargs):
        _ = self._cw._
        entity = self.cw_rset.get_entity(0, 0)
        threading.Thread(target=run_nazca, args=(self._cw, entity)).start()
        self.w(u'<h1>%s</h1>' % _('Alignment process started'))
        self._cw.add_onload('cw.cubes.nazca.setLanguage("%s"); cw.cubes.nazca.checkProgress("#progresslist")' %
                            self._cw.lang)
        self.w(u'<ul id="progresslist">')
        self.w(u'</ul>')
