# copyright 2003-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr

"""cubicweb-nazcaui align form ils for web ui"""

import re

from contextlib import contextmanager

from logilab.mtconverter import xml_escape

from cubicweb.web.views.ajaxcontroller import ajaxfunc
from cubicweb.web.views.startup import ManageView

from cubes.nazcaui.views.utils import OUTPUTS, parseindexes

_ = unicode

### GLOBAL VARIABLES ##########################################################
# Distances
DISTANCES = {_('Levenshtein'): 'levenshtein',
             _('Geographical'): 'geographical',
             _('Soundex'): 'soundex',
             # _('Exact match'): 'exact_match',
             _('Euclidean'): 'euclidean',
            }

# Normalizers
NORMALIZERS = {_(''): [],
               _('Simplify'): 'simplify',
               _('Unicode'): 'unicode',
               _('Regexp'): 'regexp',
              }

# Blockings
BLOCKINGS =  { _(''): None,
               _('NGram'): 'ngram',
                _('Kdtree'): 'kdtree',
                _('Minhashing'): 'minhashing',
                _('Kmeans'): 'kmeans',
               # _('Minibatch'): 'minibatch',
              }


### DISTANCES #################################################################
def exact_match(x, y):
    """ Exact match distance for string """
    if isinstance(x, basestring):
        x = x.strip().lower()
    if isinstance(y, basestring):
        y = y.strip().lower()
    return 0 if x == y else 1


### AJAX FUNCTIONS ############################################################
@ajaxfunc(output_type='json')
def load_blocking_options(self, blocking, idx):
    html = []
    NazcaFormBuilder(html.append, self._cw).blockings('blocking', funcname=blocking, idx=idx)
    return u'\n'.join(html)

@ajaxfunc(output_type='json')
def load_distance_options(self, distance, idx):
    html = []
    NazcaFormBuilder(html.append, self._cw).distances('distance',  funcname=distance, idx=idx)
    return u'\n'.join(html)

@ajaxfunc(output_type='json')
def load_normalization_options(self, normalization, idx):
    html = []
    NazcaFormBuilder(html.append, self._cw).normalization('normalization', normalization, idx=idx)
    return u'\n'.join(html)

@ajaxfunc(output_type='json')
def get_outputs(self):
    return OUTPUTS

@ajaxfunc(output_type='json')
def checkprogress(self):
    _ = self._cw._
    messages = self._cw.session.data['messages']
    results = {'msg': messages.pop(0) if len(messages) else None}
    # do not change the id message as it is used to check the resluts
    # in javascrtip `checkProgress`
    results.update({'finished': True if results['msg'] == _('results_done') else False})
    results.update({'error': True if results['msg'] == _('results_aborded') else False})
    return results


###############################################################################
### FORM BUILDER ##############################################################
###############################################################################
class NazcaFormBuilder(object):
    # XXX Use CW utilities for form building ?

    def __init__(self, writer, session):
        self.w = writer
        self.session = session

    def alert(self, id):
        self.w(u''' <div id="alert%s" class="alert alert-warning hidden">
            <span></span>
           </div>''' % id)

    @contextmanager
    def form(self, args):
        self.w(u'''
        <form id="form" class="form-horizontal" action="%(action)s"
        enctype="multipart/form-data" method="post">

          <div id="alert" class="hidden">
            <div class="alert alert-warning">
               <button type="button" class="close" data-dismiss="alert">&times;</button>
               <span id="msg">
               </span>
            </div>
           </div>''' % args)
        yield
        self.w(u'''
            <input type="hidden" name="step" value="1"/>
            <input type="submit" value="%(submit)s" class="btn btn-primary"/>
            </form>''' % args)

    @contextmanager
    def table(self):
        self.w(u'<table class="table table-condensed table-hover table-bordered">')
        yield
        self.w(u'''</table>''')

    def selector(self, label, choices, name='', default=None):
        _ = self.session._
        choices = choices or []
        if label:
            self.w(u'''<div class="form-group">
            <label class="col-sm-2 control-label" for="%s">%s</label>
            <div class="col-sm-10">'''% (name, label))
        self.w(u'<select id="%s"  name="%s"  class="form-control" tabindex="13">' % (name, name))
        if choices:
            default = default or choices[0][1]
        for _label, val in choices:
            if default == val:
                self.w(u'<option value="%s" selected="selected">%s</option>'
                       % (val, _(_label)))
            else:
                self.w(u'<option value="%s">%s</option>' % (val, _(_label)))
        self.w(u'</select>')
        self.alert(name)
        if label:
            self.w(u'</div></div>')

    def source_target_options(self, name, castfunc='int'):
        _ = self.session._
        # source
        source_label = self.popover(_('Source index'),
                                    _('source_index_info'),
                                    placement='right',
                                    write=False)
        # target
        target_label = self.popover(_('Target index'),
                                    _('target_index_info'),
                                    placement='right',
                                    write=False)
        self.w(u'''<div class="col-sm-4">
          <label class="control-label required" for="%(name)s_source">%(source_label)s</label>
          <input type="text" size=3 name="%(name)s_source%(cast)s" placeholder="%(placeholder)s" class="form-control integer"/>
        </div>
        <div class="col-sm-4">
          <label class="control-label required" for="%(name)s_target">%(target_label)s</label>
          <input type="text" size=3 name="%(name)s_target%(cast)s" placeholder="%(placeholder)s" class="form-control integer"/>
        </div>
            ''' % {'name': name,
                   'cast': ':%s' % castfunc,
                   'source_label': source_label,
                   'placeholder': 1 if castfunc == 'int' else '1,3,4',
                   'target_label': target_label})

    def source_target_weigthing_options(self, name, castfunc='int'):
        _ = self.session._
        self.source_target_options(name, castfunc=castfunc)
        weight_label = self.popover(_('Weighting'),
                                    _('weighting_info'),
                                 placement='right',
                                 write=False)
        self.w(u'''<div class="col-sm-4">
                    <label class="control-label" for="%(name)s_weight">%(weight_label)s</label>
                    <input type="text" size=3 name="%(name)s_weight" placeholder="%(placeholder)s" value="%(weight_value)s" class="form-control integer"/>
                    </div>
                    ''' % {'name': name,
                           'weight_label': weight_label,
                           'placeholder': 1,
                           'weight_value': 1})

    def blockings(self, holderid, funcname=None, idx=0):
        _ = self.session._
        label = self.popover(
            _('Blocking'),
            _('blocking_info'),
            placement='right', write=False
            )
        choices = BLOCKINGS.keys()[:]
        if funcname:
            choices.remove('')
        name = '__neighbours_%s' % idx
        if idx == 0:
            self.w(u'''<div class="form-group">''')
            self.w(u'''<label class="col-sm-4 control-label" for="%s">%s</label>''' % (name, label))
            self.w(u'<div class="col-sm-8">''')
            self.w(u'<div class="input-group">')
            self.w(u'<select class="form-control" tabindex="13">')
            default = ''
            for val, choice in zip(choices, choices):
                if default == choice:
                    self.w(u'<option value="%s" selected="selected">%s</option>'
                           % (val, _(choice) if choice else choice))
                else:
                    self.w(u'<option value="%s">%s</option>' % (val,
                                                                _(choice) if choice else choice))
            self.w(u'</select>')
            self.w(u'''<a href="javascript:$.noop()" onclick="cw.cubes.nazca.addNewOption($(this), 'blocking', '%(holderid)s')" data-blocking="%(idx)s" class="btn btn-default js-nazca-add-blocking input-group-addon" title="%(add-title)s"><span class="glyphicon glyphicon-plus"></span></a>''' % {'add-title': _('add a blocking'), 'idx': idx, 'holderid': holderid})
            self.w(u'</div>')
            self.w(u'</div>')
            self.w(u'</div>')
            self.w(u'<ol id="%s" class="options-holder"></ol>' % holderid)
        else:
            self.w(u'<div class="panel panel-default panel-blocking">')
            self.w(u'<div class="panel-heading">')
            self.w(u'<input name="%s__funcname" type="hidden" value="%s" />' % (name, funcname))
            self.w(u'<div class="input-group">')
            self.w(u'<div>%s</div>' % _('Blocking function: "%s"') % _(funcname))
            self.w(u'''<a href="javascript:$.noop()" onclick="cw.cubes.nazca.removeOption($(this), 'blocking')" data-blocking="%(idx)s" class="btn btn-default js-nazca-remove-blocking input-group-addon" title="%(remove-title)s"><span class="glyphicon glyphicon-minus"></span></a>''' % {'remove-title': _('remove this blocking'), 'idx': idx, 'holderid': holderid})
            self.w(u'</div>') # end input-group
            self.w(u'</div>') # end panel-heading
            self.w(u'<div class="panel-body">')
            self.w(u'<div class="form-group col-sm-12">')
            self.source_target_options(name)
            self.w(u'</div>')
            getattr(self, '%s_options' % BLOCKINGS[funcname])(name)
            self.w(u'</div>')
            self.w(u'</div>') # end panel-body
            self.w(u'</div>') # end panel

    def popover(self, title, content, placement='top', write=True):
        data = u'''%s&#160;<a data-content="%s" rel="popover" data-trigger="hover"  data-placement="%s"
                   href="#"><i class="glyphicon glyphicon-question-sign"></i></a>''' % (title,
                   xml_escape(content),
                   placement)
        if write:
            self.w(data)
        else:
            return data

    def help(self, content):
        self.w(u'<p class="help-block">%s</p>' % content)

    def add_checkbox_option(self, **kwargs):
        kwargs['col_ind'] = kwargs.get('col_ind', '4')
        return u'''<div class="col-sm-4">
          <div class="checkbox">
            <label>
              <input type="checkbox" name="%(name)s">%(label)s
            </label>
          </div>
        </div>''' % kwargs

    def add_input_option(self, **kwargs):
        _ = self.session._
        kwargs['colidx'] = kwargs.get('colidx', '4')
        label_class  = [kwargs.get('label_class', ''), 'control-label']
        kwargs['label_class'] = ' '.join(label_class)
        input_class  = [kwargs.get('input_class', ''), 'form-control']
        kwargs['input_class'] = ' '.join(input_class)
        #  value
        value =  kwargs.get('value', '')
        if value:
            kwargs['value'] = 'value="%s"' % kwargs['value']
        else:
            kwargs['value'] = ''
        return '''<div class="col-sm-%(colidx)s">
          <label class="%(label_class)s" for="%(name)s">%(label)s</label>
          <input type="int" class="%(input_class)s" placeholder="%(placeholder)s" %(value)s name="%(name)s" />
        </div>''' % kwargs

    @contextmanager
    def distances(self, holderid, funcname=None, idx=0):
        _ = self.session._
        label = self.popover(
            _('Distance function'),
            _('distance_info'),
            placement='right', write=False)
        choices = DISTANCES.keys()[:]
        name = '__distance_%s' % idx
        if idx == 0:
            self.w(u'''<div class="form-group">''')
            self.w(u'''<label class="col-sm-4 control-label required" for="%s">%s</label>''' % (name, label))
            self.w(u'<div class="col-sm-8">''')
            self.w(u'<div class="input-group">')
            self.w(u'<select class="form-control" tabindex="13">')
            default = 'Levenshtein'
            for val, choice in zip(choices, choices):
                if default == choice:
                    self.w(u'<option value="%s" selected="selected">%s</option>'
                           % (val, _(choice) if choice else choice))
                else:
                    self.w(u'<option value="%s">%s</option>' % (val,
                                                                _(choice) if choice else choice))
            self.w(u'</select>')
            self.w(u'''<a href="javascript:$.noop()" onclick="cw.cubes.nazca.addNewOption($(this), 'distance', '%(holderid)s')"data-distance="%(idx)s" class="btn btn-default js-nazca-add-distance input-group-addon" title="%(add-title)s"><span class="glyphicon glyphicon-plus"></span></a>''' % {'add-title': _('add a distance'), 'idx': idx, 'holderid': holderid})
            self.w(u'</div>')
            self.w(u'</div>')
            self.w(u'</div>')
            self.w(u'<ol id="%s" class="options-holder"></ol>' % holderid)
        else:
            self.w(u'<div class="panel panel-default panel-distance">')
            self.w(u'<div class="panel-heading">')
            # self.w(u'<label class="col-sm-2 sr-only control-label" for="%s">%s</label>' % (name, 'selected distance'))
            self.w(u'<input name="%s__funcname" type="hidden" value="%s" />' % (name, funcname))
            self.w(u'<div class="input-group">')
            self.w(u'<div>%s</div>' % _('Distance function: "%s"') % _(funcname))
            self.w(u'''<a href="javascript:$.noop()" onclick="cw.cubes.nazca.removeOption($(this), 'distance')" data-distance="%(idx)s" class="btn btn-default js-nazca-remove-distance input-group-addon" title="%(remove-title)s"><span class="glyphicon glyphicon-minus"></span></a>''' % {'remove-title': _('remove this distance'), 'idx': idx, 'holderid': holderid})
            self.w(u'</div>') # end input-group
            self.w(u'</div>') # end panel-heading
            self.w(u'<div class="panel-body">')
            self.w(u'<div class="form-group col-sm-12">')
            self.source_target_weigthing_options(name)
            self.w(u'</div>')
            # options
            getattr(self, '%s_options' % DISTANCES[funcname])(name)
            self.w(u'</div>') # end panel-body
            self.w(u'</div>') # end panel

    @contextmanager
    def normalization(self, holderid, funcname=None, idx=0):
        _ = self.session._
        label = self.popover(_('Normalization'),
                             _('normalization_info'),
                             placement='right',
                             write=False)
        choices = NORMALIZERS.keys()[:]
        if funcname:
            choices.remove('')
        name = '__normalize_%s' % idx
        if idx == 0:
            self.w(u'''<div class="form-group">''')
            self.w(u'''<label class="col-sm-4 control-label" for="%s">%s</label>''' % (name, label))
            self.w(u'<div class="col-sm-8">''')
            self.w(u'<div class="input-group">')
            self.w(u'<select class="form-control" tabindex="13">')
            default = ''
            for val, choice in zip(choices, choices):
                if default == choice:
                    self.w(u'<option value="%s" selected="selected">%s</option>'
                           % (val, _(choice) if choice else choice))
                else:
                    self.w(u'<option value="%s">%s</option>' % (val,
                                                                _(choice) if choice else choice))
            self.w(u'</select>')
            self.w(u'''<a href="javascript:$.noop()" onclick="cw.cubes.nazca.addNewOption($(this), 'normalization', '%(holderid)s')"data-normalization="%(idx)s" class="btn btn-default js-nazca-add-normalization input-group-addon" title="%(add-title)s"><span class="glyphicon glyphicon-plus"></span></a>''' % {'add-title': _('add a normalization'), 'idx': idx, 'holderid': holderid})
            self.w(u'</div>')
            self.w(u'</div>')
            self.w(u'</div>')
            self.w(u'<ol id="%s" class="options-holder"></ol>' % holderid)
        else:
            self.w(u'<div class="panel panel-default panel-normalization">')
            self.w(u'<div class="panel-heading">')
            self.w(u'<div class="input-group">')
            self.w(u'<input name="%s__funcname" type="hidden" value="%s" />' % (name, funcname))
            self.w(u'<div>%s</div>' % _('Normalization function: "%s"') % _(funcname))
            self.w(u'''<a href="javascript:$.noop()" onclick="cw.cubes.nazca.removeOption($(this), 'normalization')" data-normalization="%(idx)s" class="btn btn-default js-nazca-remove-normalization input-group-addon" title="%(remove-title)s"><span class="glyphicon glyphicon-minus"></span></a>''' % {'remove-title': _('remove this normalization'), 'idx': idx, 'holderid': holderid})
            self.w(u'</div>') # end input-group
            self.w(u'</div>') # end panel-heading
            self.w(u'<div class="panel-body">')
            # attributes
            self.w(u'<div class="form-group col-sm-12">')
            self.source_target_options(name, castfunc='intlist')
            self.w(u'</div>')
            getattr(self, '%s_options' % NORMALIZERS[funcname])(name)
            self.w(u'</div>') # end panel-body
            self.w(u'</div>') # end panel

    def write(self, html):
        self.w(html)

    @contextmanager
    def fieldset(self, legend):
        _ = self.session._
        self.w(u'<fieldset>')
        self.w(u'<legend>%s</legend>' % _(legend))
        yield
        self.w(u'</fieldset>')

    def hide(self):
        self.w(u'<div style="display:none;">')

    def unhide(self):
        self.w(u'</div>')

    def requestgroup(self, args):
        _ = self.session._
        self.selector(label=_('Request type'),
                      choices=((_('sparql'), 'sparql'), (_('csv file'), 'csv')), # u'rql'
                       name=u'__%stype' % args['type'],
                      default=args.get('language'))
        args['request-title'] = _('request')

        self.w(u'''
           <div class="form-group group-%(type)squery">
               <label class="col-sm-2 control-label required" for="__%(type)sreq">%(request-title)s</label>
               <div class="col-sm-10">
               <textarea id="__%(type)sreq" cols="60" class="form-control" name="__%(type)sreq" onkeyup="autogrow(this)" rows="5" tabindex="12">
%(req)s
               </textarea>
               </div>
           </div>''' % args)
        self.w(u'''
           <div id="group-%(type)sfile" class="form-group">
               <label class="col-sm-2 control-label required" for="__%(type)sfile">%(title)s file</label>
               <div class="col-sm-10">
                   <input type="file" name="__%(type)sfile"/>
               </div>
           </div>''' % args)

        self.w(u'''
           <div class="group-%(type)squery form-group">
               <label class="col-sm-2 control-label required" for="__%(type)ssource">
               ''' % args)
        self.popover(_('Source'),
                     _('source_params_info'),
                     'right')
        self.w(u'''</label>
               <div class="col-sm-10">
                   <input id="__%(type)ssource" type="text" maxlength="100" class="form-control"
                    name="__%(type)ssource" size="45" tabindex="14" placeholder="%(source)s" value="%(source)s" />
               </div>
           </div>
           <div class="form-group">
               <label class="col-sm-2 control-label" for="__%(type)sindexes">''' % args)
        self.popover(_('Indexes'), _('indexes_info'), 'right')
        self.w(u'''</label>
               <div class="col-sm-10">
                   <input id="__%(type)sindexes" type="text" maxlength="100" class="form-control"
                   name="__%(type)sindexes" size="45" tabindex="15" placeholder="%(indexes)s"  value="%(indexes)s"/>
               </div>
           </div>''' % args)

    def ngram_options(self, name):
        #  ngram_size=2, depth=2
        _ = self.session._
        self.w(u'''<div class="col-sm-12">
           %(ngram_size)s  %(depth)s
         </div>''' % {'ngram_size': self.add_input_option(**{'label':_('Ngram size'),
                                                             'placeholder':'2',
                                                             'value':'2',
                                                             'input_class': 'integer',
                                                             'name':'%s_ngram_size:int' % name}),
                      'depth': self.add_input_option(**{'label':_('Depth'),
                                                        'placeholder':'2',
                                                        'value':'2',
                                                        'input_class': 'integer',
                                                        'name':'%s_depth:int' % name}),
                      })
        self.w(u'</div>')

    def kdtree_options(self, name):
        # threshold=0.1
        _ = self.session._
        self.w(u'<div class="col-sm-12">%s</div>' %
               self.add_input_option(**{'label':_('Threshold'),
                                        'placeholder':'0.1',
                                        'value':'0.1',
                                        'input_class': 'integer',
                                        'name':'%s_threshold:float' % name}))

    def minhashing_options(self, name):
        # threshold=0.1, kwordsgram=1, siglen=200
        _ = self.session._
        self.w(u'''<div class="col-sm-12">
           %(threshold)s  %(kwordsgram)s  %(siglen)s
         </div>''' % {'threshold': self.add_input_option(**{'label':_('Threshold'),
                                                            'placeholder':'0.1',
                                                            'value':'0.1',
                                                            'input_class': 'form-control integer',
                                                            'name':'%s_threshold:float' % name}),
                      'kwordsgram': self.add_input_option(**{'label':_('Kwordsgram'),
                                                             'placeholder':'1',
                                                             'value': '1',
                                                             'input_class': 'integer',
                                                             'name':'%s_kwordsgram:int' % name}),
                      'siglen': self.add_input_option(**{'label':_('Siglen'),
                                                         'placeholder':'200',
                                                         'value': '200',
                                                         'input_class': 'integer',
                                                         'name':'%s_siglen:int' % name})
                      })

    def kmeans_options(self, name):
        # n_clusters=None
        _ = self.session._
        self.w(u'<div class="col-sm-12">%s</div>' %
               self.add_input_option(**{'label': _('Number of clusters'),
                                        'placeholder':'1',
                                        'input_class': 'integer',
                                        'name':'%s_n_clusters:int' % name}))

    def levenshtein_options(self, name):
        # tokenizer=None
        return u''
        #_ = self.session._
        # self.w('''<div class="col-sm-12">%s</div>''' %
        #        self.add_input_option(**{'name': '%s_tokenizer' % name,
        #                                 'label': _('Tockenizer'),
        #                                 'input_class': 'integer',
        #                                 'placeholder':'tokenizer',
        #                                 }))

    def geographical_options(self, name):
        # in_radians=False, planet_radius=6371009,  units='m
        _ = self.session._
        self.w(u'''<div class="col-sm-12">
          %(in_radians)s %(planet_radius)s %(units)s
          <div>''' % {'in_radians': self.add_checkbox_option(**{'name':'%s_in_radians:bool' % name,
                                                                'label':_('In radians')}),
                      'planet_radius': self.add_input_option(**{'label':_('Planet raduis'),
                                                                'placeholder':'6371009',
                                                                'value':'6371009',
                                                                'input_class': 'integer',
                                                                'name':'%s_planet_radius:float' % name}),
                      'units': self.add_input_option(**{'label':_('Units'),
                                                        'placeholder':'m',
                                                        'value':'m',
                                                        'input_class': 'integer',
                                                        'name':'%s_units' % name })})

    def soundex_options(self, name):
        # language='french', tokenizer=None
        _ = self.session._
        self.w(u'''<div class="col-sm-12">
           %(language)s
           </div>''' % {'tokenizer': self.add_input_option(**{'placeholder':'tokenizer',
                                                              'colidx':6,
                                                              'name': '%s_tokenizer' % name,
                                                              'label':_('Tockenizer')}),
                        'language': self.add_input_option(**{'placeholder':'french',
                                                             'colidx':6,
                                                             'name':'%s_language' % name,
                                                             'value':'french',
                                                             'label':_('Language')})
                        })

    def euclidean_options(self, name):
        print 'euclidean_options'

    def exact_match_options(self, name):
        print 'euclidean_options'

    def unicode_options(self, name):
        _ = self.session._
        self.w(u'<div class="col-sm-12">')
        self.w(u'''<div class="col-sm-4">
           <label class="control-label" for="%(name)s">%(label)s</label>
          <textarea class="form-control" placeholder="%(placeholder)s" name="%(name)s" />
        </div>''' % {'name':'%s_substitute' % name,
                     'label':_('Substitute'),
                     'placeholder':''})
        self.w(u'</div>')

    def simplify_options(self, name):
        _ = self.session._
        self.w(u'<div class="col-sm-12">')
        self.w(u'''<div class="col-sm-8">
          <label class="control-label" for="%(name)s">%(label)s</label>
          <textarea class="form-control" placeholder="%(placeholder)s" name="%(name)s" />
        </div>''' % {'placeholder':'word, word, word',
                     'name':'%s_lemmas:stringlist' % name,
                     'label':_('Lemmas')})
        self.w(self.add_checkbox_option(**{'name': '%s_remove_stopwords:bool' % name,
                                           'label':_('Remove stopwords')}))
        self.w(u'</div>')

    def regexp_options(self, name):
        _ = self.session._
        self.w(u'<div class="col-sm-12">')
        self.w(u'''<div class="col-sm-4">
           <label class="control-label" for="%(name)s">%(label)s</label>
           <textarea class="form-control" placeholder="%(placeholder)s" name="%(name)s" />
           </div>''' % {'name':'%s_regexp' % name,
                        'label':_('Regexp'),
                        'placeholder':''})
        self.w(u'''<div class="col-sm-4">
           <label class="control-label" for="%(name)s">%(label)s</label>
           <textarea class="form-control" placeholder="%(placeholder)s" name="%(name)s" />
           </div>''' % {'name':'%s_output' % name,
                        'label':_('Output'),
                        'placeholder':''})
        self.w(u'</div>')


###############################################################################
### VIEWS #####################################################################
###############################################################################
class NazcaView(ManageView):
    __regid__ = 'nazca'
    title = _('Nazca alignment')

    def build_refset(self, defvalues, builder):
        _ = self._cw._
        builder.requestgroup({'type': u'align',
                              'title': _('Align'),
                              'source': defvalues.get('__alignsource', u'http://rdf.insee.fr/sparql'),
                              'indexes': defvalues.get('__alignindexes', u'?commune, ?nom, ?popTotale'),
                              'language': defvalues.get('__aligntype', 'sparql'),
                              'file': defvalues.get('__alignfile'),
                              'req': defvalues.get('__alignreq',
                                                   u'PREFIX idemo:<http://rdf.insee.fr/def/demo#> '
                                                   u'PREFIX igeo:<http://rdf.insee.fr/def/geo#> '
                                                   u'PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> '
                                                   u'SELECT ?commune ?nom ?popTotale WHERE { '
                                                   u'?commune igeo:nom ?nom . ?commune idemo:population '
                                                   u'?popLeg . ?commune rdf:type igeo:Commune . ?popLeg '
                                                   u'idemo:populationTotale ?popTotale . FILTER (?popTotale >= 10000) }')
                              })

    def build_targetset(self, defvalues, builder):
        _ = self._cw._
        builder.requestgroup({'type': u'target',
                              'title': _('Target'),
                              'source': defvalues.get('__targetsource',
                                                      u'http://dbpedia.inria.fr/sparql'),
                              'indexes': defvalues.get('__targetindexes', '?ville, ?name,?population'),
                              'language': defvalues.get('__targettype', 'sparql'),
                              'file': defvalues.get('__targetfile'),
                              'req': defvalues.get('__targetreq',
                                                   u'prefix db-owl: <http://dbpedia.org/ontology/> '
                                                   u'prefix db-prop: <http://fr.dbpedia.org/property/> '
                                                   u'select ?ville, ?name, ?population where { '
                                                   u'?ville db-owl:country <http://fr.dbpedia.org/resource/France> . '
                                                   u'?ville rdf:type db-owl:PopulatedPlace . ?ville db-owl:populationTotal '
                                                   u'?population . ?ville foaf:name ?name . FILTER (?population > 10000) }')
                              })


    def call(self, rset=None, **kwargs):
        _ = self._cw._
        self._cw.add_onload("""$('a[rel=popover]').popover({'html':true});
                               $('#__aligntype').change(function() {
                                    cw.cubes.nazca.typeChange('align');
                                });
                               $('#__targettype').change(function() {
                                    cw.cubes.nazca.typeChange('target');
                                });
                                cw.cubes.nazca.typeChange('align');
                                cw.cubes.nazca.typeChange('target');
                            """)
        self.w(u'<h1>%s</h1>' % _('Nazca alignment'))
        self.w(u'''<div class="alert alert-info">%s
                <button type="button" class="close"  data-dismiss="alert" aria-hidden="true">&times;</button>
                </div>''' % _('alignment_info'))
        # Create the form builder
        builder = NazcaFormBuilder(self.w, self._cw)
        defvalues = self._cw.form
        if defvalues.get('__alignfile'):
            __, self._cw.session.data['__alignfile'] = defvalues.get('__alignfile')
        if defvalues.get('__targetfile'):
            __, self._cw.session.data['__targetfile'] = defvalues.get('__targetfile')
        defvalues.setdefault('step', '0')
        if 'results' in self._cw.session.data:
            del self._cw.session.data['results']
        if defvalues['step'] == '0':
            defvalues.update(kwargs.get('formvalues', {}))
        # Create the form
        with builder.form({'action': '#' if defvalues['step'] == '0' else
                                     self._cw.build_url('nazca-results'),
                           'submit': _('Next step')}):
            if defvalues['step'] == '1':
                builder.hide()
            with builder.fieldset(_('Refset builder')):
                self.build_refset(defvalues, builder)
            with builder.fieldset(_('Targetset builder')):
                self.build_targetset(defvalues, builder)
            if defvalues['step'] == '1':
                builder.unhide()
                for _type in ('__alignindexes', '__targetindexes'):
                    defvalues[_type] = parseindexes(defvalues.get(_type) or '0, 0')
                zipindexes = zip(defvalues['__alignindexes'],
                                 defvalues['__targetindexes'])
                if len(defvalues['__alignindexes']) != len(defvalues['__targetindexes']):
                    raise ValueError('aligne indexes length must be equal to target indexes')

                with builder.fieldset(_('Distances')):
                    builder.distances('distance-list')
                with builder.fieldset(_('Blockings')):
                    builder.blockings('blocking-list')
                with builder.fieldset(_('Normalization')):
                    builder.normalization('normalization-list')
                with builder.fieldset(_('Alignment')):
                    builder.write(u"""
                    <div class="form-group">
                    <label class="col-sm-2 control-label" for="__threshold">
                    """)
                    builder.popover(u'Threshold',
                                    _('threshold_info'),
                             placement='right')
                    builder.write(u"""</label>
                       <div class="col-sm-10">
                           <input id="__threshold" type="text" maxlength="100"  class="form-control"
                            name="__threshold" size="45" tabindex="14" value="%s"/>
                       </div>
                   </div>""" % defvalues.get('__threshold', 240.4))
                #     builder.write(u"""
                # <div class="form-group">
                #  <div class="col-sm-10">
                #    <div class="checkbox">
                #        <label for="__keepall">
                #            <input id="__keepall" type="checkbox" name="__keepall" value="keepall" />
                #        """)
                #     builder.popover(u'Keep not aligned results',
                #                    _('keepall_info'),
                #                     placement='right')
                #     builder.write(u"""
                #            </label>
                #    </div>
                #   </div>
                # </div>""")
                    builder.write(u"""
                   <div class="form-group">
                       <label  class="col-sm-2 control-label" for="__alignname">
                       """)
                    builder.popover(_('Alignment Name'),
                                    _('alignment name_info'),
                                    # u'Name of the alignment',
                                placement='right')
                    builder.write(u"""</label>
                       <div class="col-sm-10">
                           <input id="__alignname"  type="text" maxlength="100" class="form-control"
                            name="__alignname" size="45" tabindex="14"/>
                       </div>
                   </div>""")
