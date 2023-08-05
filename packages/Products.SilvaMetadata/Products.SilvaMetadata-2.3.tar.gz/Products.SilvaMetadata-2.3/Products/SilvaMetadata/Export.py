"""
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

# Python
from StringIO import StringIO
from cgi import escape
from types import IntType, FloatType, ListType

# Zope
from zope.interface import implements


from interfaces import IMetadataSetExporter
from Element import MetadataElement
from XMLType import serialize
from utils import make_lookup

class MetadataSetExporter(object):
    """
    for exporting a metadata set definition
    """
    implements(IMetadataSetExporter)

    def __init__(self, set):
        self.set = set

    def __call__(self, out=None):

        ext_out = 1
        if out is None:
            ext_out = 0
            out = StringIO()

        print >> out, '<?xml version="1.0"?>\n\n'
        print >> out, '<metadata_set id="%s" ns_uri="%s" ns_prefix="%s">' % (
            self.set.getId(),
            self.set.metadata_uri,
            self.set.metadata_prefix
            )

        title = escape(self.set.getTitle(), 1)
        description = escape(self.set.getDescription(), 1)
        minimalrole = escape(self.set.getMinimalRole(), 1)
        category = escape(self.set.getCategory(), 1)
        i18n_domain = escape(self.set.get_i18n_domain(), 1)

        out.write('<title>%s</title>\n' % (title))
        out.write('<category>%s</category>\n' % (category))
        out.write('<description>%s</description>\n' % (description))
        out.write('<i18n_domain>%s</i18n_domain>\n' % (i18n_domain))
        out.write('<minimalrole>%s</minimalrole>\n' % (minimalrole))

        for e in self.set.getElements():

            print >> out, '  <metadata_element id="%s">' % e.getId()
            print >> out, '   <index_type>%s</index_type>' % e.index_type
            print >> out, '   <index_p>%d</index_p>' % e.index_p
            print >> out, '   <metadata_in_catalog_p>%d</metadata_in_catalog_p>' % e.metadata_in_catalog_p
            print >> out, '   <field_type>%s</field_type>' % e.field_type
            print >> out, '   <acquire_p>%d</acquire_p>' % e.acquire_p
            print >> out, '   <read_only_p>%d</read_only_p>' % e.read_only_p

            g = e.read_guard

            print >> out, '   <read_guard>'
            print >> out, '     <roles>%s</roles>' % g.getRolesText()
            print >> out, '     <permissions>%s</permissions>' \
                          % g.getPermissionsText()
            print >> out, '     <expr>%s</expr>' % g.getExprText()
            print >> out, '   </read_guard>'

            g = e.write_guard
            print >> out, '   <write_guard>'
            print >> out, '     <roles>%s</roles>' % g.getRolesText()
            print >> out, '     <permissions>%s</permissions>' \
                          % g.getPermissionsText()
            print >> out, '     <expr>%s</expr>' % g.getExprText()
            print >> out, '   </write_guard>'

            f = e.field

            print >> out, '   <field_values>'

            for k, v in f.values.items():
                if v is None:
                    continue
                if isinstance(v, IntType):
                    out.write('        ' \
                              '<value key="%s" type="%s" value="%d" />\n'
                               % (k, 'int', v))
                elif isinstance(v, FloatType):
                    out.write('        ' \
                              '<value key="%s" type="%s" value="%d" />\n'
                              % (k, 'float', v))
                elif isinstance(v, ListType):
                    out.write('        ' \
                              '<value key="%s" type="%s" value="%s" />\n'
                              % (k, 'list', escape(str(v), 1)))
                else:
                    out.write('        ' \
                              '<value key="%s" type="str" value="%s" />\n'
                              % (k, escape(str(v), 1)))

            print >> out, '   </field_values>'

            print >> out, '   <field_tales>'
            for k,v in f.tales.items():
                if v is None:
                    continue
                # FIXME: we get to the actual "source" for the TALESMethod by
                # getting its _text
                # Needs a different way of retrieving this value?
                out.write('     <value key="%s">%s</value>\n'
                          % (k, escape(getattr(v, '_text', ''), 1)))
            print >> out, '   </field_tales>'

            print >> out, '   <field_messages>'
            for message_key in f.get_error_names():
                message_text = f.get_error_message(
                    message_key, want_message_id=False)
                out.write('     <message name="%s">%s</message>\n' % (
                    escape(message_key, 1), escape(message_text, 1)))

            print >> out, '   </field_messages>'

            print >> out, '   <index_args>'
            for k,v in e.index_constructor_args.items():
                out.write('     <value key="%s">%s</value>\n'
                          % (k, escape(str(v), 1)))
            print >> out, '   </index_args>'

            print >> out, '  </metadata_element>'



        print >> out, '</metadata_set>'

        if ext_out:
            return out

        return out.getvalue()

class ObjectMetadataExporter(object):
    """
    for exporting the metadata of an object, returns
    an xml fragement.

    XXX encoding issues
    XXX file/image binary metadata issues
    """

    def __init__(self, binding, sets):
        self.binding = binding
        self.sets = sets

    def __call__(self, out=None):

        external_out = not not out

        if out is None:
            out = StringIO()

        out.write('<metadata \n')

        for set in self.sets:
            out.write('    xmlns:%s="%s"\n'
                      % (set.metadata_prefix, set.metadata_uri))
        out.write('      >')

        for set in self.sets:
            sid = set.getId()
            prefix = set.metadata_prefix
            check = make_lookup(set.objectIds(MetadataElement.meta_type))
            data = self.binding._getData(sid)

            for k,v in data.items():
                # with updates its possible that certain annotation data
                # is no longer part of the metadata set, so we filter it out.
                if not check(k):
                    continue

                out.write(u'      <%s:%s>%s</%s:%s>\n'
                          % (prefix, k, serialize(v), prefix, k))

        out.write('</metadata>\n')

        if external_out:
            return None

        return out.getvalue()
