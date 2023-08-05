"""
Tests for the SilvaMetada.

$Id: test_Metadata.py,v 1.22 2005/09/14 23:10:16 clemens Exp $
"""

from unittest import TestSuite, makeSuite

from zope.component import getUtility

from Products.Formulator import StandardFields
from Products.Formulator.TALESField import TALESMethod
from Products.SilvaMetadata.interfaces import IMetadataService

from Products.Silva.tests import SilvaTestCase


SET_ID = 'ut_md'


def setupContentTreeSilva(self, container):

    zoo = self.add_folder(container, 'zoo', "Zoo Folder")
    self.add_folder(zoo, 'mammals', "Zoo Mammals")
    zoo = self.add_folder(zoo, 'reptiles', "Zoo Reptiles")
    return zoo


def setupMetadataSet(context):
    mtool = getUtility(IMetadataService)
    collection = mtool.getCollection()
    collection.addMetadataSet(SET_ID,
                              'tmd',
                              'http://www.example.com/xml/test_md')
    set = collection.getMetadataSet(SET_ID)
    set.addMetadataElement('Title',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1)
    set.addMetadataElement('Description',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1)
    element = set.getElement('Description')
    element.field._edit({'required':0})
    element.editElementPolicy(acquire_p = 1)
    return set


def setupMetadataMapping(context):
    mtool = getUtility(IMetadataService)
    mapping = mtool.getTypeMapping()
    mapping.setDefaultChain('ut_md')
    mtool.addTypesMapping(
        ('Silva Folder', ), ('ut_md', 'silva-extra'))


class MetadataTestCase(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        setupMetadataSet(self.root)
        setupMetadataMapping(self.root)
        setupContentTreeSilva(self, self.root)


class TestMetadataElement(MetadataTestCase):

    def testGetDefault(self):
        pm = getUtility(IMetadataService)
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        element = set.getElement('Title')
        element.field._edit_tales({'default':
                                   TALESMethod('content/getPhysicalPath')})
        zoo = self.root.zoo
        binding = pm.getMetadata(zoo)
        defaults = set.getDefaults(content = zoo)
        self.assertEqual(defaults['Title'],
                         zoo.getPhysicalPath(),
                         "Tales Context Passing Failed")

    def testGetDefaultWithTalesDelegate(self):
        mtool = getUtility(IMetadataService)
        mtoolId = mtool.getId()
        collection = mtool.getCollection()
        set = collection.getMetadataSet(SET_ID)
        zoo = self.root.zoo
        test_value = 'Rabbits4Ever'
        binding = mtool.getMetadata(zoo)
        binding.setValues(SET_ID, {'Title':test_value})
        element = set.getElement('Description')
        # yikes, narly tales expression
        method = "python: content.%s.getMetadata(content).get(" \
                 "'%s', 'Title', no_defaults=1)" % (mtoolId, SET_ID)
        element.field._edit_tales({'default': TALESMethod(method)})
        value = binding.get(SET_ID, 'Description')
        self.assertEqual(value, test_value,
                         "Tales delegate for default didn't work")
        # make sure the right cached value was stored.
        value = binding.get(SET_ID, 'Description')
        self.assertEqual(value, test_value, "Wrong Data Object Cached")
        # test shortcut, too
        self.assertEqual(value,
                         mtool.getMetadataValue(zoo, SET_ID, 'Description'))

    def testAcquisitionInvariant(self):
        # invariant == can't be required and acquired
        from Products.SilvaMetadata.Exceptions import ConfigurationError
        pm = getUtility(IMetadataService)
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        element = set.getElement('Description')
        try:
            element.field._edit({'required':1})
            element.editElementPolicy(acquire_p = 1)
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition/Required Element" \
                                 " Invariant Failed")
        try:
            element.field._edit({'required':0})
            element.editElementPolicy(acquire_p = 1)
            element.field._edit({'required':1})
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition/Required Element" \
                                 " Invariant Failed 2")


class TestAdvancedMetadata(MetadataTestCase):
    """Tests for runtime binding methods"""

    def setupAcquiredMetadata(self):
        zoo = self.root.zoo
        binding = getUtility(IMetadataService).getMetadata(zoo)
        set_id = SET_ID
        binding.setValues(set_id, {'Title':'hello world',
                                   'Description':'cruel place'})

    def testContainmentAcquisitionValue(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mams = zoo.mammals
        z_binding = getUtility(IMetadataService).getMetadata(zoo)
        m_binding = getUtility(IMetadataService).getMetadata(mams)
        set_id = SET_ID
        self.assertEqual(m_binding[set_id]['Description'],
                         z_binding[set_id]['Description'])
        # test shortcut, too
        self.assertEqual(getUtility(IMetadataService).getMetadataValue(mams,set_id,'Description'),
                         getUtility(IMetadataService).getMetadataValue(zoo,set_id,'Description'))
        self.assertNotEqual(m_binding.get(set_id, 'Description', acquire=0),
                            z_binding[set_id]['Description'])

    def testContainmentAcquisitionList(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mams = zoo.mammals
        m_binding = getUtility(IMetadataService).getMetadata(mams)
        z_binding = getUtility(IMetadataService).getMetadata(zoo)
        set_id = SET_ID
        acquired = m_binding.listAcquired()
        # test the contained's list acquired
        self.assertEqual(len(acquired), 1)
        self.assertEqual(acquired[0][1], 'Description')
        # test the container's listacquired
        acquired = z_binding.listAcquired()
        self.assertEqual(len(acquired), 0)
        # special case for
        z_binding.setValues(set_id, {'Title':'', 'Description':''})
        acquired = z_binding.listAcquired()
        self.assertEqual(len(acquired), 0)

    def testObjectDelegation(self):
        from Acquisition import Implicit
        class Delegator(Implicit):
            def __init__(self, name):
                self.name = name
            def __call__(self):
                ob = self.aq_inner.aq_parent
                return getattr(ob, self.name)

        zoo = self.root.zoo
        delegate = Delegator('reptiles')
        zoo.delegate = delegate
        mams = zoo.mammals
        reps = zoo.reptiles
        r_binding = getUtility(IMetadataService).getMetadata(reps)
        m_binding = getUtility(IMetadataService).getMetadata(mams)
        r_binding.setValues(SET_ID,
                            {'Title':'snake food',
                             'Description':'yummy n the tummy'}
                            )
        m_binding.setObjectDelegator('delegate')
        self.assertEqual(
            m_binding[SET_ID]['Title'],
            r_binding[SET_ID]['Title']
            )
        # test shortcut, too
        self.assertEqual('snake food',
                         getUtility(IMetadataService).
                              getMetadataValue(mams, SET_ID, 'Title'))
        m_binding.clearObjectDelegator()
        assert m_binding[SET_ID]['Title'] != r_binding[SET_ID]['Title']

    def testMutationTriggerDelegation(self):
        class MutationTrigger:
            def __init__(self):
                self.called = 0
            def __call__(self):
                self.called += 1

        zoo = self.root.zoo
        mams = zoo.mammals
        m_binding = getUtility(IMetadataService).getMetadata(mams)
        trigger = MutationTrigger()
        zoo.trigger = trigger
        m_binding.setMutationTrigger(SET_ID, 'Title', 'trigger')
        m_binding.setValues(SET_ID, {'Title':'surfin betty',
                                     'Description':'morning pizza'})
        self.assertEqual(trigger.called, 1)
        m_binding.setValues(SET_ID, {'Description':'midnight raid'})
        self.assertEqual(trigger.called, 1)
        m_binding.clearMutationTrigger(SET_ID)
        # props to tennyson
        m_binding.setValues(SET_ID,
                            {'Title':
                             'To strive, to seek, to find, and not to yield'}
                            )
        self.assertEqual(trigger.called, 1)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestMetadataElement))
    suite.addTest(makeSuite(TestAdvancedMetadata))
    return suite


