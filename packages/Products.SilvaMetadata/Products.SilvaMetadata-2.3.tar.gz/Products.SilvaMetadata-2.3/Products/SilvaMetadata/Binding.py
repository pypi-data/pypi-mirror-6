"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
# Python
from UserDict import UserDict

# Zope
from Acquisition import Implicit, aq_base, aq_parent

from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides
from zope.publisher.interfaces.http import IHTTPRequest

# Formulator
from Products.Formulator.Errors import FormValidationError


from zExceptions import Unauthorized
from ZODB.PersistentMapping import PersistentMapping

from Exceptions import NotFound
from Export import ObjectMetadataExporter
from Index import getIndexNamesFor
import Initialize as BindingInitialize
from Namespace import BindingRunTime
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass # Zope 2.12

from silva.core.services.interfaces import ICataloging


#################################
### runtime bind data keys
AcquireRuntime = 'acquire_runtime'
ObjectDelegate = 'object_delegate'
MutationTrigger = 'mutation_trigger'

#################################
### Acquired Metadata Prefix Encoding
MetadataAqPrefix = 'metadataAq'
MetadataAqVarPrefix = '_VarName_'

_marker = []


class Data(UserDict):
    """
    We use this as to escape some vagaries with the zope security policy
    when using the __getitem__ interface of the binding
    """
    __roles__ = None
    __allow_access_to_unprotected_subobjects__ = 1


class MetadataBindAdapter(Implicit):

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, content, sets, read_only=False):
        self.content = content
        self.collection = {}
        self.setnames = []
        self.category_to_setnames = {}
        self.cached_values = {}
        self.read_only=read_only

        for set in sets:
            setid = set.getId()
            self.setnames.append(setid)
            self.collection[setid] = set
            category = set.getCategory()
            setnames = self.category_to_setnames.setdefault(category, [])
            setnames.append(setid)

    #################################
    ### Views
    security.declarePublic('renderXML')
    def renderXML(self, set_id=None, namespace_key=None):
        """
        return an xml serialization of the object's metadata
        """

        if set_id or namespace_key:
            sets = [self._getSet(set_id, namespace_key)]
        else:
            sets = self.collection.values()

        exporter = ObjectMetadataExporter(self, sets)
        return exporter()

    security.declarePublic('renderElementView')
    def renderElementView(self, set_id, element_id):
        element = self.getElement(set_id, element_id)
        data = self._getData(set_id)
        value = data.get(element_id, None)
        return element.renderView(value)

    security.declarePublic('renderElementEdit')
    def renderElementEdit(self, set_id, element_id, REQUEST=None):
        element = self.getElement(set_id, element_id)
        if REQUEST:
            #here we want to render the value from the request
            #(i.e. a save didn't pass validation and the form
            #needs to be preloaded with the previously supplied values)
            #so the value for this element comes from the REQUEST
            value = REQUEST.get(set_id).get(element_id)
        else:
            #if request is false, then we want to render the default/saved
            # value
            value = self._getData(set_id, acquire=0).get(element_id,None)
        return element.renderEdit(value)

    #################################
    ### Validation

    security.declarePublic('validate')
    def validate(self, set_id, data, errors=None):
        """
        validate the data. implicit transforms may be preformed.
        """
        return validateData(self, self.collection[set_id], data, errors)

    security.declarePublic('validateFromRequest')
    def validateFromRequest(self, set_id, REQUEST, errors=None):
        """
        validate from request
        """
        data = REQUEST.form.get(set_id)

        if data is None:
            raise NotFound("Metadata for %s not found" % (
                    str(set_id)))

        return self.validate(set_id, data.copy(), errors)

    #################################
    ### Storage (invokes validation)

    security.declarePublic('setValues')
    def setValues(self, set_id, data, reindex=0):
        """
        data should be a mutable dictionary

        returns a dictionary of errors if any, or none otherwise
        """
        errors = {}
        data = self.validate(set_id, data, errors)

        if errors:
            return errors

        set = self.collection[set_id]
        self._setData(data, set_id=set_id, reindex=reindex)
        return None

    security.declarePublic('setValuesFromRequest')
    def setValuesFromRequest(self, request, reindex=0):
        """Returns a dictionary of errors if any
        """
        all_errors = {}
        ms = self.service_metadata
        context = self._getAnnotatableObject()
        setnames = self.getSetNames()
        for setname in setnames:
            if setname not in request.form:
                continue
            try:
                form = ms.getMetadataForm(context, setname)
                #validate_all expects an httprequest-list object
                #we're giving it a dict, so declare that the dict
                #implements IHTTPRequest. NOTE: this was added
                #to that the referencelookupwindow field could
                #be used as a metadata field...this type of
                #lookupwindow requires an IHTTPRequest in order
                #to validate using the path adapter
                reqform = request.form[setname]
                alsoProvides(reqform,IHTTPRequest)
                result = form.validate_all(reqform)

                # Remove keys from the result that are supposed to be
                # read-only only
                set = self.getSet(setname)
                elements = set.getElements()
                for element in elements:
                    if not element.isEditable(context):
                        try:
                            del result[element.id]
                        except KeyError, e:
                            pass

            except FormValidationError, e:
                all_errors[setname] = errors = {}
                for error in e.errors:
                    errors[error.field_id] = error.error_text
            else:
                self._setData(result, setname, reindex=reindex)
        return all_errors

    #################################
    ### Discovery Introspection // Definition Accessor Interface

    security.declarePublic('getSetNames')
    def getSetNames(self, category=None):
        """Return the ids of the metadata sets available for this
        content type.
        """
        if category is None:
            return tuple(self.setnames)
        setnames = self.category_to_setnames.get(category, [])
        return tuple(setnames)

    security.declarePublic('keys')
    keys = getSetNames

    security.declarePublic('getElementNames')
    def getElementNames(self, set_id, mode=None):
        """Given a set identifier return the ids of the elements
        within the set.
        """
        # XXX
        # if mode is not specified this returns all elements of a set.
        # not all elements visible will be viewable/editable
        set = self.collection[set_id]

        if mode is not None:
            elements = set.getElementsFor(self.content, mode=mode)
        else:
            elements = set.getElements()

        return [e.getId() for e in elements]

    security.declarePublic('getSetNameByURI')
    def getSetNameByURI(self, uri):
        for set in self.collection.values():
            if set.metadata_uri == uri:
                return set.getId()
        raise NotFound(uri)

    security.declarePublic('getSet')
    def getSet(self, set_id):
        """To invoke methods on the set requires permissions on
        the set not the content, whereas binding methods
        merely require permissions on the content.
        """
        return self.collection[set_id]

    security.declarePublic('getElement')
    def getElement(self, set_id, element_id):
        return self.getSet(set_id).getElement(element_id)

    security.declarePublic('isViewable')
    def isViewable(self, set_id, element_id):
        """
        is the element viewable for the content object
        """
        element = self.collection[set_id].getElement(element_id)
        ob = self._getAnnotatableObject()
        return element.isViewable(ob)

    security.declarePublic('isEditable')
    def isEditable(self, set_id, element_id):
        """
        is the element editable for the content object
        """
        element = self.collection[set_id].getElement(element_id)
        ob = self._getAnnotatableObject()
        return element.isEditable(ob)


    security.declarePublic('listAcquired')
    def listAcquired(self):
        """
        compute and return a list of (set_id, element_id)
        values for all metadata which this binding/content
        acquires from above in the containment hiearchy.
        """
        res = []
        ob = self._getAnnotatableObject()

        for s in self.collection.values():
            sid = s.getId()
            data = self._getData(set_id = sid, acquire=0)
            for e in [e for e in s.getElements() if e.isAcquireable()]:
                eid = e.getId()
                if data.has_key(eid) and data[eid]:
                    continue
                name = encodeElement(sid, e.getId())
                try:
                    value = getattr(ob, name)
                except AttributeError:
                    continue
                # filter out any empty metadata fields
                # defined on ourselves to acquire
                if not hasattr(aq_base(ob), name):
                    res.append((sid, eid))

        return res

    #################################
    ### Data Accessor Interface

    security.declarePublic('get')
    def get(self, set_id, element_id=None, acquire=1, no_defaults=0):
        """
        if element_id is specified, only the value of that element is
        returned, otherwise a Data object is returned. Data objects
        implement a mapping interface.

        the acquire flag determines whether or not metadata acquisition
        will be used in retrieving values, acquired values will override
        default values but not values stored on the object.

        the no_defaults flag specifies whether an element's default values
        should be used. default values are only used when there is no
        value stored on the object.

        the use case for no_defaults is whe using tales defaults to defer
        an element's value to another element within the same set. also when
        no_defaults is used not all elements of the set will nesc. be
        in the data object returned only those which were findable.
        """
        data = self._getData(set_id=set_id,
                             acquire=acquire,
                             no_defaults=no_defaults)
        if element_id is not None:
            return data.get(element_id)
        return data

    def __getitem__(self, key):
        if self.collection.has_key(key):
            return self._getData(key)
        raise KeyError(str(key))

    #################################
    ### RunTime Binding Methods

    security.declarePublic('setObjectDelegator')
    def setObjectDelegator(self, method_name):
        """
        we get and set all metadata on a delegated object,
        method should be a callable method on the object
        (acquiring the method is ok) that should take zero
        args, and return an object. if it doesn't return
        an object, we return the default metadata values
        associated (not a good idea).
        """
        assert getattr(self.content, method_name), \
                       "invalid object delegate %s" % method_name

        bind_data = self._getBindData()
        bind_data[ObjectDelegate]=method_name

    security.declarePrivate('getObjectDelegator')
    def getObjectDelegator(self):
        return self._getBindData().get(ObjectDelegate)

    security.declarePublic('clearObjectDelegator')
    def clearObjectDelegator(self):
        bind_data = self._getBindData()
        try:
            del bind_data[ObjectDelegate]
        except KeyError:
            pass
        # invalidate cache
        self.cached_values = {}

        return None

    security.declarePublic('setMutationTrigger')
    def setMutationTrigger(self, set_id, element_id, method_name):
        """
        support for simple events, based on acquired method
        invocation. major use case.. cache invalidation on
        metadata setting.
        """
        assert getattr(self._getAnnotatableObject(), method_name), \
                       "invalid mutation trigger %s" % method_name

        bind_data = self._getBindData()
        tr = bind_data.setdefault(MutationTrigger, {}).setdefault(set_id, {})
        tr[element_id]=method_name

    security.declarePublic('clearMutationTrigger')
    def clearMutationTrigger(self, set_id, element_id=None):
        """
        clear mutation triggers for a particular set or element.

        if element_id is not specified, clear triggers for
        the entire set.
        """

        bind_data = self._getBindData()
        triggers = bind_data[MutationTrigger]

        if element_id is None:
            try:
                del triggers[set_id]
            except KeyError:
                pass
        else:
            try:
                del triggers[set_id][element_id]
            except KeyError:
                pass
        return None

    #################################
    ### Private

    def _getSet(self, set_id=None, namespace_key=None):
        if set_id:
            return self.collection[set_id]
        elif namespace_key:
            return self._getSetByKey(namespace_key)
        else:
            raise NotFound("metadata set not found %s %s"
                           % (set_id, namespace_key))

    def _getBindData(self):
        metadata = IAnnotations(aq_base(self.content))
        bind_data = metadata.get(BindingRunTime)

        if bind_data is None:
            init_handler = BindingInitialize.getHandler(self.content)
            bind_data = metadata.setdefault(BindingRunTime, PersistentMapping())
            if init_handler is not None:
                init_handler(self.content, bind_data)

        return bind_data

    def _getMutationTriggers(self, set_id):
        bind_data = self._getBindData()
        return bind_data.get(MutationTrigger, {}).get(set_id, [])

    def _getAnnotatableObject(self):
        # check for object delegation
        bind_data = self._getBindData()
        object_delegate = bind_data.get(ObjectDelegate)

        # we want to use the content in its original acquisiton
        # context, but because we retrieve it as an attribute
        # it gets wrapped.. content.__of__(binding).__of__(content)
        # so we remove the outer two wrappers to regain the original
        # context
        content = aq_parent(aq_parent(self.content))

        if object_delegate is not None:
            od = getattr(self.content, object_delegate)
            ob = od()
        else:
            ob = content

        return ob

    def _getData(self, set_id=None, namespace_key=None,
                 acquire=1, no_defaults=0):
        """
        find the metadata for the given content object,
        performs runtime binding work as well.

        """

        set = self._getSet(set_id, namespace_key)

        # cache lookup
        data = self.cached_values.get((acquire, set.getId()))
        if data is not None:
            return data

        using_defaults = []
        ob = self._getAnnotatableObject()

        # get the annotation data
        metadata = IAnnotations(aq_base(ob))

        saved_data = metadata.get(set.metadata_uri)
        data = Data()

        sid = set.getId()
        element_ids = self.getElementNames(sid)

        if saved_data is None and no_defaults:
            pass
        elif saved_data is None:
            # use the sets defaults
            defaultvalues = set.getDefaults(content=ob)
            data.update(defaultvalues)
            # record which elements we used default values for
            using_defaults = element_ids
        else:
            # make a copy so we can modify with acq metadata
            data.update(saved_data)

            if not no_defaults:
                # update individual elements with default values
                # if they don't have a saved value.
                for eid in element_ids:
                    if data.has_key(eid):
                        continue
                    defaultvalue = set.getElement(eid).getDefault(content=ob)
                    data[eid] = defaultvalue
                    using_defaults.append(eid)

        # cache metadata
        self.cached_values[ (acquire, set_id) ]=data

        if not acquire:
            return data

        # get the acquired metadata
        hk = data.has_key
        for e in [e for e in set.getElements() if e.isAcquireable()]:
            eid = e.getId()
            if hk(eid) and data[eid] and not eid in using_defaults:
                continue
            aqelname = encodeElement(sid, eid)
            try:
                val = getattr(ob, aqelname)
            except AttributeError:
                continue
            data[eid]=val

        return data

    def _setData(self, data, set_id=None, namespace_key=None, reindex=0):
        if self.read_only:
            return
        set = self._getSet(set_id, namespace_key)
        set_id = set.getId()

        # check for delegates
        ob = self._getAnnotatableObject()

        # filter based on write guard and whether field is readonly
        all_elements = set.getElements()
        all_eids = [e.getId() for e in all_elements]
        elements = [e for e in set.getElementsFor(ob, mode='edit')]
        eids = [e.getId() for e in elements]

        keys = data.keys()

        for k in keys:
            if k in eids:
                continue
            elif k in all_eids:
                raise Unauthorized('Not Allowed to Edit %s in this context' % k)
            else:
                del data[k]

        # fire mutation triggers
        triggers = self._getMutationTriggers(set_id)

        if triggers:
            for k in keys:
                if triggers.has_key(k):
                    try:
                        getattr(ob, triggers[k])()
                    except: # gulp
                        pass

        # update acquireable metadata
        update_list = [e.getId() for e in set.getElements() \
                                 if  e.isAcquireable() and e.getId() in keys]
        sid = set.getId()

        for eid in update_list:
            aqelname = encodeElement(sid, eid)
            value = data[eid]
            if value:
                setattr(ob, aqelname, value)
            else:
                # Try and get rid of encoded attribute on the
                # annotatable object; this will get acquisition
                # of the value working again.
                try:
                    delattr(ob, aqelname)
                except (KeyError, AttributeError), err:
                    pass

        # save in annotations
        metadata = IAnnotations(aq_base(ob))

        if metadata.has_key(set.metadata_uri):
            for key, value in data.items():
                if not (value == '' or value is None):
                    metadata[set.metadata_uri][key] = value
                elif metadata[set.metadata_uri].has_key(key):
                    del metadata[set.metadata_uri][key]
        else:
            metadata[set.metadata_uri] = PersistentMapping({})
            for key, value in data.items():
                if not (value == '' or value is None):
                    metadata[set.metadata_uri][key] = value
                elif metadata[set.metadata_uri].has_key(key):
                    del metadata[set.metadata_uri][key]
        # invalidate the cache version of the set if any
        # we do a check for cached acquired/non-acquired
        if self.cached_values.has_key((0, set_id)):
            del self.cached_values[(0, set_id)]
        if self.cached_values.has_key((1, set_id)):
            del self.cached_values[(1, set_id)]

        # mark both the content and the annotatable object as changed so
        # on txn commit bindings in other objectspaces get invalidated as well
        ob._p_changed = 1
        self.content._p_changed = 1

        # reindex object
        if reindex:
            reindex_elements = [
                e for e in elements
                if (e.getId() in keys) and e.index_p]
            ICataloging(ob).reindex(indexes=getIndexNamesFor(reindex_elements))

    def _getSetByKey(self, namespace_key):
        for s in self.collection.values():
            if s.metadata_uri == namespace_key:
                return s
        raise NotFound(str(namespace_key))

InitializeClass(MetadataBindAdapter)


def validateData(binding, set, data, errors_dict=None):
    # XXX completely formulator specific
    from Products.Formulator.Errors import ValidationError

    # Filter out elements not in the data dict, provided the element is
    # not required or the binding already has a value for this element.
    for e in set.getElements():
        eid = e.getId()
        has_a_value = not not binding.get(set.getId(), eid, acquire=0)
        is_required = e.isRequired()

        if hasattr(aq_base(e.field), 'sub_form'):
            # XXX this is really a datetime hack..
            # Fields with subforms will/might have only their marshalled
            # subform ids stored in the data dict. There really isn't a
            # good way to discover which fields are sub form providers,
            # so we just try to introspect.
            # Get one of the subform field ids, just try one.. unfortunately
            # the presence of a subform has little todo with the fields
            # request encoding. sigh.
            sfid = e.field.sub_form.get_field_ids()[0]
            sfkey = e.field.generate_subfield_key(sfid, validation=1)

            if not data.has_key(sfkey) and (not is_required or has_a_value):
                continue

        elif not data.has_key(eid) and (not is_required or has_a_value):
            continue

        try:
            data[eid] = e.validate(data)
        except ValidationError, exception:
            if errors_dict is not None:
                errors_dict[eid] = exception.error_text
            else:
                raise
    return data

def encodeElement(set_id, element_id):
    """
    after experimenting with various mechanisms for doing
    containment based metadata acquisition, using extension class
    acquisition was found to be the quickest way to do the containment
    lookup. as attributes are stored as opaque objects, the current
    implementation decorates the object heirarchy with encoded variables
    corresponding to the metadata specified as acquired. the encoding
    is used to minimize namespace pollution. acquired metadata is only
    specified in this manner on the source object.
    """
    return MetadataAqPrefix + set_id + MetadataAqVarPrefix + element_id

def decodeVariable(name):
    """ decode an encoded variable name... not used """
    assert name.startswith(MetadataAqPrefix)

    set_id = name[len(MetadataAqPrefix):name.find(MetadataAqVarPrefix)]
    e_id = name[name.find(MetadataAqVarPrefix)+len(MetadataAqVarPrefix):]

    return set_id, e_id

