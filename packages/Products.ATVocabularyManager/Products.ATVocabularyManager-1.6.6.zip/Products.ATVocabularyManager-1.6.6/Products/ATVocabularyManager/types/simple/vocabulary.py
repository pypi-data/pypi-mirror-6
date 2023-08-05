# File: vocabulary.py
"""\
A vocabulary is a container for key/value pairs. This SimpleVocabulary can
contain every object, that implements IVocabularyTerm.

RCS-ID $Id: SimpleVocabulary.py 3219 2004-10-29 00:49:03Z zworkb $
"""
# Copyright (c) 2004-2006 by BlueDynamics Alliance - Klein & Partner KEG, Austria
#
# BSD-like licence, see LICENCE.txt
#
__author__ = 'Jens Klein <jens@bluedynamics.com>'
__docformat__ = 'plaintext'

import csv
from StringIO import StringIO
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError
from Products.ATVocabularyManager.config import *
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone.public import *
    from Products.LinguaPlone.interfaces import ILinguaPloneProductLayer
else:
    from Products.Archetypes.atapi import *
    ILinguaPloneProductLayer = None

try:
    from plone.browserlayer.utils import registered_layers
except ImportError:
    registered_layers = lambda: []   # returns empty list

from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IVocabulary
from Products.Archetypes.utils import make_uuid
from Products.Archetypes.utils import DisplayList
from Products.Archetypes.utils import OrderedDict
from Products.Archetypes import PloneMessageFactory as PMF

from Products.ATVocabularyManager.config import PROJECTNAME
from Products.ATVocabularyManager import messageFactory as _ 

class SimpleVocabulary(OrderedBaseFolder):

    implements(IVocabulary)

    security = ClassSecurityInfo()
    meta_type = 'SimpleVocabulary'

    schema = BaseFolderSchema.copy() + Schema((
        StringField('id',
                    required = 1, ## Still actually required, but
                    ## the widget will supply the missing value
                    ## on non-submits
                    mode = "rw",
                    accessor = "getId",
                    mutator = "setId",
                    default = '',
                    widget = StringWidget(
                        label=_("label_vocab_name",
                                default=u"Vocabulary Name"),
                        description=_("help_vocab_name",
                                      default=u"Should not contain spaces, underscores or mixed case."),
                        size=50,
                        ),
                    ),

        TextField('description',
                  default = '',
                  required = 0,
                  searchable = 0,
                  accessor = "Description",
                  storage = MetadataStorage(),
                  widget = TextAreaWidget(label=PMF("label_description",
                                                    default=u"Description"),
                                          description=PMF("help_description",
                                                          default=u"Enter a brief description"),
                                          rows = 5,
                                          ),
                  ),

        StringField("sortMethod",
                    default = SORT_METHOD_LEXICO_VALUES,
                    required = 0, # smooth upgrades from 1.0.0-beta2
                    searchable = 0,
                    widget = SelectionWidget(
                        label = _("label_sort_method",
                                  default=u"Sort method"),
                        description = _("help_sort_method",
                                        default=u"Sort method used for displaying vocabulary terms"),
                    ),
                    vocabulary = VOCABULARY_SORT_ORDERS,
        ),
    ))

    def isLinguaPloneInstalled(self):
        """ checks if LinguaPlone is installed """
        return ILinguaPloneProductLayer in registered_layers() \
               or self.portal_quickinstaller.isProductInstalled('LinguaPlone')

    # Methods from Interface IVocabulary
    def getDisplayList(self, instance):
        """Returns a object of class DisplayList as defined in Products.Archetypes.utils.

        The instance of the content class is given as parameter.
        The list is sorted accordingly to the sortMethod chosen.
        """
        dl = DisplayList()
        vdict = self.getVocabularyDict(instance)
        for key in self.getSortedKeys(instance):
            dl.add(key, vdict[key])
        return dl

    def getVocabularyLines(self, instance=None):
        """Returns a List of Key-Value tuples.
        The list is sorted accordingly to the sortMethod chosen.
        """
        termlist = []
        vdict = self.getVocabularyDict(instance)

        for key in self.getSortedKeys():
            termlist.append((key, vdict[key]))
        return termlist

    def getVocabularyDict(self, instance=None):
        """Returns a vocabulary dictionary as defined in the interface
        """

        if self.isLinguaPloneInstalled():
            # if lp is installed
            # obtain language and return translated dict
            try:
                # we use the language of instance for this dictionary
                lang = instance.getLanguage()
            except AttributeError:
                # we retrieve the current language
                langtool = getToolByName(self, 'portal_languages')
                lang = langtool.getPreferredLanguage()
            return self._getTranslatedVocabularyDict(lang)
        else:
            # just return all terms
            vdict = OrderedDict()
            for obj in self.contentValues():
                vdict[obj.getTermKey()] = obj.getTermValue()
            return vdict

    def _getTranslatedVocabularyDict(self, lang):
        vdict = OrderedDict()
        for obj in self.contentValues():
            # we only use the canonical objects
            if obj.isCanonical():
                vdict[obj.getTermKey()] = obj.getTermValue(lang)
        return vdict

    def isFlat(self):
        """ returns true for a flat vocabulary """
        return 1

    def showLeafsOnly(self):
        """ indicates if only leafs should be shown """
        return 1

    # some supporting methods

    def getSortedKeys(self, instance=None):
        """ returns a list of keys sorted accordingly to the

        selected sort method (may be unsorted if method = no sort)
        """
        sortMethod = self.getSortMethod()
        context = self
        if self.isLinguaPloneInstalled() and instance:
            lang_instance = instance.getLanguage()
            langtool = getToolByName(self, 'portal_languages')
            lang_canonical = langtool.getPreferredLanguage()
            context = context.getTranslation(lang_instance)

        keys = [term.getVocabularyKey() for term in context.contentValues()]

        if not hasattr(self, 'sortMethod'):
            # smooth upgrade from previous releases
            return keys

        if sortMethod == SORT_METHOD_LEXICO_KEYS:
            keys.sort()
            return keys

        if sortMethod == SORT_METHOD_LEXICO_VALUES:
            # returns keys sorted by lexicogarphic order of VALUES
            terms = context.contentValues()
            terms.sort(lambda x, y: cmp(x.getVocabularyValue(), y.getVocabularyValue()))
            return [term.getVocabularyKey() for term in terms]

        if sortMethod == SORT_METHOD_FOLDER_ORDER:
            try:
                contentListing = getMultiAdapter((context, context.REQUEST), name=u'folderListing')()
            except ComponentLookupError:
                # still Plone 3 compatible
                contentListing = context.getFolderContents()
            return [term.getObject().getVocabularyKey() for term in contentListing]

        # fallback
        return keys

    security.declareProtected(AddPortalContent, 'addTerm')
    def addTerm(self, key, value, language=None, termtype=DEFAULT_VOCABULARY_ITEM,
                silentignore=False, **kwargs):
        """ add a new key/value pair to the container

            termtype is the portal_type of the term

            language is for future use with LinguaPlone

            with silentignore duplicate keys are silently skipped

            returns True if addition worked
        """

        if self.getVocabularyDict().has_key(key):
            if silentignore:
                return False
            raise KeyError, 'key %s already exist in vocabulary %s ' % (key, self.title_or_id())

        allowed = [fti.content_meta_type for fti in self.allowedContentTypes()]
        if not termtype in allowed:
            if termtype == DEFAULT_VOCABULARY_ITEM and len(allowed)==1:
                termtype=allowed[0].meta_type
            else:
                raise ValueError, 'type %s is not allowed as vocabularyterm in this context' % termtype


        self.invokeFactory(termtype, key)
        self[key].setTitle(value)
        return True

    security.declareProtected(AddPortalContent, 'importCSV')
    def importCSV(self, csvdata,
                  termtype=DEFAULT_VOCABULARY_ITEM,
                  titlerow=False,
                  silentignore=False):
        """ imports given csv data as the given vocabularytype

            csv is a string or a file-like object in the style:

                "Data 1.1", "Data 1.2"
                "Data 2.1", "Data 2.2"
                "Data 3.1", "Data 3.2"

            vocabularytype is the terms portal-type, like SimpleVocabularyTerm
            which is also the default.

            It uses column 1 as key=id and column 2 as value=title.

            If titlerow is True the first line will be skipped.
        """

        qi = getToolByName(self, 'portal_quickinstaller')
        lp = qi.isProductInstalled('LinguaPlone')

        if type(csvdata) == type(''):
            csvdata = StringIO(csvdata)

        csvreader = csv.reader(csvdata)
        languages = []
        for row in csvreader:

            if titlerow:

                # If LinguaPlone is installed, it's assumed the title row is
                # used to define language columns
                if lp:
                    for n in range(1, len(row)):
                        languages.append(row[n])

                titlerow = False

            else:
                value = unicode(row[1], IMPORT_ENCODING)
                key = row[0] or make_uuid(value)
                self.addTerm(key, value, termtype=termtype, silentignore=silentignore)

                if len(languages) > 0:
                    self[key].setLanguage(languages[0])
                    if len(row) > 2:
                        for col in range(2, len(row)):
                            self[key].addTranslation(languages[col-1], title=row[col])


registerType(SimpleVocabulary, PROJECTNAME)
# end of class SimpleVocabulary
