# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from urlparse import urlparse
import logging

from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.component import getUtility
import transaction

from Acquisition import aq_base
from zExceptions import NotFound
from five.intid.site import aq_iter

from Products.SilvaDocument.interfaces import IDocumentVersion
from Products.SilvaDocument.transform.base import Context
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.SilvaFind.interfaces import IPathCriterionField
from Products.Silva.ExtensionRegistry import extensionRegistry

from silva.core.interfaces import ISilvaObject, IVersionedContent
from silva.core.references.interfaces import IReferenceService
from silva.core.services.interfaces import IContainerPolicyService
from silva.core.services.interfaces import IMemberService
from silva.core.upgrade.upgrade import BaseUpgrader, content_path
from silva.core.upgrade.upgrader.upgrade_220 import UpdateIndexerUpgrader
from silva.core.services.interfaces import ICataloging

logger = logging.getLogger('silva.core.upgrade')


#-----------------------------------------------------------------------------
# 2.2.0 to 2.3.0b1
#-----------------------------------------------------------------------------

VERSION_B1='2.3b1'
VERSION_B2='2.3b2'
VERSION_FINAL='2.3'


class RootUpgrader(BaseUpgrader):

    def upgrade(self, root):
        installed_ids = root.objectIds()

        # add service_references
        factory = root.manage_addProduct['silva.core.references']

        def install_ref_service():
            factory.manage_addReferenceService('service_references')

        if 'service_references' not in installed_ids:
            install_ref_service()
        elif not IReferenceService.providedBy(root.service_references):
            root.manage_delObjects(['service_references'])
            install_ref_service()

        reg = root.service_view_registry
        reg.unregister('add', 'Silva Ghost Folder')
        reg.unregister('add', 'Silva Ghost')
        reg.unregister('edit', 'Silva Link')
        reg.unregister('preview', 'Silva Agenda Item Version')
        reg.unregister('preview', 'Silva Article Version')
        reg.unregister('preview', 'Silva Ghost Version')
        reg.unregister('public', 'Silva Agenda Item')
        reg.unregister('public', 'Silva Article')
        reg.unregister('public', 'Silva Ghost Version')
        reg.unregister('public', 'Silva Ghost')

        # remove un-needed Silva Document services
        for service in ['service_editor',
                        'service_editorsupport',
                        'service_old_codesource_charset',
                        'service_widgets',
                        'service_doc_editor',
                        'service_doc_viewer',
                        'service_field_editor',
                        'service_field_viewer',
                        'service_nlist_editor',
                        'service_nlist_viewer',
                        'service_widgets',
                        'service_sub_editor',
                        'service_sub_viewer',
                        'service_news_sub_viewer',
                        'service_news_sub_editor',
                        'service_table_editor',
                        'service_table_viewer']:
            try:
                root.manage_delObjects([service])
            except:
                logger.warn("failed to remove %s" % service)
        transaction.commit()
        return root


root_upgrader = RootUpgrader(VERSION_B1, 'Silva Root')


def split_path(path, context, root=None):
    """Split path, remove . components, be sure there is enough parts
    in the context path to get all .. working.
    """
    if root is None:
        root = context.getPhysicalRoot()
    parts = path.split('/')
    if len(parts) and not parts[0]:
        context = root
    parts = filter(lambda x: x != '', parts)
    context_parts = filter(lambda x: x != '', list(context.getPhysicalPath()))
    root_parts = filter(lambda x: x != '', list(root.getPhysicalPath()))
    assert len(context_parts) >= len(root_parts)
    if len(root_parts):
        context_parts = context_parts[len(root_parts):]
    while parts:
        if parts[0] == '.':
            parts = parts[1:]
        elif parts[0] == '..':
            if len(context_parts):
                context_parts = context_parts[:-1]
                parts = parts[1:]
            else:
                raise KeyError(path)
        else:
            break
    return context_parts + parts, root


def build_reference(context, target, node):
    """Create a new reference to the given target and store it on the
    node.
    """
    reference_name, reference = context.new_reference()
    reference.set_target(target)
    node.setAttribute('reference', reference_name)


def resolve_path(url, content_path, context, obj_type=u'link'):
    """Resolve path to an object or report an error.
    """
    scheme, netloc, path, parameters, query, fragment = urlparse(url)
    if scheme:
        # This is a remote URL
        logger.debug(u'found a remote link %s' % url)
        return None, None
    if not path:
        # This is to an anchor in the document, nothing else
        return None, fragment
    try:
        cleaned_path, path_root = split_path(path, context)
        target = path_root.unrestrictedTraverse(cleaned_path)
    except (AttributeError, KeyError, NotFound, TypeError):
        # Try again using Silva Root as /
        try:
            cleaned_path, path_root = split_path(
                path, context, context.get_root())
            target = path_root.unrestrictedTraverse(cleaned_path)
        except (AttributeError, KeyError, NotFound, TypeError):
            logger.error(u'broken %s %s in %s' % (obj_type, url, content_path))
            return None, fragment
    if not ISilvaObject.providedBy(target):
        logger.error(
            u'%s %s did not resolve to a Silva content in %s' % (
                obj_type, path, content_path))
        return None, fragment
    try:
        [o for o in aq_iter(target, error=RuntimeError)]
        return target, fragment
    except RuntimeError:
        logger.error(u'invalid target %s %s in %s' %(
                obj_type, path, content_path))
        return None, fragment


class DocumentUpgrader(BaseUpgrader):
    """We rewrite here document links and images in order to use
    references where ever it is possible.
    """

    def upgrade(self, obj):
        if IDocumentVersion.providedBy(obj):
            context = Context(obj, None)
            dom = obj.content.documentElement
            self.__upgrade_links(obj, context, dom)
            self.__upgrade_images(obj, context, dom)
        return obj

    def __upgrade_links(self, version, context, dom):
        links = dom.getElementsByTagName('link')
        version_path = content_path(version)
        if links:
            logger.info(u'upgrading links in: %s', version_path)
        for link in links:
            if link.hasAttribute('reference'):
                # Already migrated
                continue
            path = link.getAttribute('url')
            # Look for object
            target, fragment = resolve_path(path, version_path, context.model)
            if fragment:
                link.setAttribute('anchor', fragment)
                link.removeAttribute('url')
            if target is None:
                continue
            build_reference(context, target, link)
            if not fragment:
                link.removeAttribute('url')

    def __upgrade_images(self, version, context, dom):
        images = dom.getElementsByTagName('image')
        version_path = content_path(version)

        def make_link(image, target, title='', window_target='', fragment=''):
            """Create a link, replace the image with it and set the
            image as child of the link.
            """
            link = dom.createElement('link')
            if not isinstance(target, basestring):
                build_reference(context, target, link)
            else:
                link.setAttribute('url', target)
            if fragment:
                link.setAttribute('anchor', fragment)
            if title:
                link.setAttribute('title', title)
            if window_target:
                link.setAttribute('target', window_target)
            parent = image.parentNode
            parent.replaceChild(link, image)
            link.appendChild(image)
            return link

        if images:
            logger.info('upgrading images in: %s', version_path)
        for image in images:
            if image.hasAttribute('reference'):
                # Already a reference
                continue
            path = image.getAttribute('path')
            target, fragment = resolve_path(
                path, version_path, context.model, 'image')
            if target is not None:
                # If the image target is found it is changed to a
                # reference. However if it is not, we still want to
                # process the other aspect of the image tag migration
                # so just don't do continue here.
                build_reference(context, target, image)
                image.removeAttribute('path')
                image.removeAttribute('rewritten_path')
            # Collect link title/target
            title = ''
            if image.hasAttribute('title'):
                title = image.getAttribute('title')
                image.removeAttribute('title')
            window_target = ''
            if image.hasAttribute('target'):
                window_target = image.getAttribute('target')
                image.removeAttribute('target')
            link_set = False
            # Check for a link
            if image.hasAttribute('link'):
                link = image.getAttribute('link')
                if link:
                    link_target, fragment = resolve_path(
                        link, version_path, context.model)
                    if link_target is not None:
                        make_link(
                            image, link_target, title, window_target, fragment)
                    elif fragment:
                        make_link(image, '', title, window_target, fragment)
                    else:
                        make_link(image, link, title, window_target)
                    link_set = True
                image.removeAttribute('link')
            # Check for a link to high resolution version of the image
            if image.hasAttribute('link_to_hires'):
                link = image.getAttribute('link_to_hires')
                if link == '1' and link_set is False:
                    make_link(image, target, title, window_target)
                    link_set = True
                image.removeAttribute('link_to_hires')
            # Save the image title (aka alt) to its new name
            if image.hasAttribute('image_title'):
                title = image.getAttribute('image_title')
                image.removeAttribute('image_title')
                image.setAttribute('title', title)


class ArticleUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        for version in obj.objectValues():
            if IDocumentVersion.providedBy(version):
                if not isinstance(version.content, ParsedXML):
                    logger.info('upgrade xmlattribute for %s' %
                                "/".join(version.getPhysicalPath()))
                    parsed_xml = version.content._content
                    version.content = parsed_xml
        return obj


class GhostUpgrader(BaseUpgrader):

    def validate(self, obj):
        return hasattr(obj, '_content_path')

    def upgrade(self, obj):
        target_path = obj._content_path
        if target_path:
            target = obj.get_root().unrestrictedTraverse(
                target_path, None)
            if target is not None:
                logger.info('upgrade reference object for Ghost @%s' %
                            "/".join(obj.getPhysicalPath()))
                obj.set_haunted(target)
            else:
                logger.warn(
                    'Ghost at %s point to a non existing object at %s' %
                    ("/".join(obj.getPhysicalPath()), target_path,))
            del obj._content_path
        return obj


class VersionedContentUpgrader(BaseUpgrader):
    """Remove cache_data from versioned content as this is not used anymore.
    """

    def validate(self, obj):
        return IVersionedContent.providedBy(obj)

    def upgrade(self, obj):
        if hasattr(aq_base(obj), '_cached_checked'):
            del obj._cached_checked
        if hasattr(aq_base(obj), '_cached_data'):
            del obj._cached_data
        return obj


class LinkVersionUpgrader(BaseUpgrader):
    """ replace relative links with references
    """

    def validate(self, version):
        return (not version.__dict__.has_key('_relative') and
                not self.__is_absolute_url(version._url))

    def upgrade(self, version):
        link_path = content_path(version)
        target, fragment = resolve_path(
            version._url, link_path, version.get_container())

        if target:
            logger.info('upgrade link %s' % link_path)
            version.set_relative(True)
            version.set_target(target)
            version._url = u''
        else:
            logger.warn('cannot find target for link %s to %s' %
                        (link_path, version._url,))
        return version

    def __is_absolute_url(self, url):
        purl = urlparse(url)
        return bool(purl.netloc)


class SilvaFindUpgrader(BaseUpgrader):

    def validate(self, obj):
        return True

    def upgrade(self, obj):
        service = getUtility(IReferenceService)
        fields = obj.service_find.getSearchSchema().getFields()
        fields = filter(lambda x: IPathCriterionField.providedBy(x), fields)
        root = obj.get_root()
        root_path = root.getPhysicalPath()
        for field in fields:
            field_name = field.getName()
            if obj.searchValues.has_key(field_name):
                value = obj.searchValues[field_name]
                if value:
                    path = value.split('/')
                    if tuple(path[:len(root_path)]) == root_path:
                        traverse_path = path[len(root_path):]
                        target = root.unrestrictedTraverse(traverse_path, None)
                        if target:
                            ref = service.new_reference(
                                obj, name=unicode(field_name))
                            ref.set_target(target)
                            logger.info('reference created for field %s of '
                                        'silva find at %s' %
                                        (field_name,
                                         "/".join(obj.getPhysicalPath())))
                        else:
                            logger.warn('silva find target at %s '
                                        'not found' % value)
                    else:
                        logger.warn('silva find target at %s '
                                    'outside of silva root' % value)
                del obj.searchValues[field_name]
        return obj


link_upgrader = LinkVersionUpgrader(VERSION_B1, 'Silva Link Version')

document_upgrader = DocumentUpgrader(
    VERSION_B1, 'Silva Document Version')
cache_upgrader = VersionedContentUpgrader(
    VERSION_B1, ['Silva Ghost', 'Silva Link', 'Silva Document'])

article_upgrader_agenda = ArticleUpgrader(
    VERSION_B1, ['Silva Agenda Item', 'Silva Article'])
article_cache_upgrader = VersionedContentUpgrader(
    VERSION_B1, ['Silva Article', 'Silva Agenda Item'])
document_upgrader_agenda = DocumentUpgrader(
    VERSION_B1, ["Silva Agenda Item Version", "Silva Article Version"], 1000)

ghost_upgrader = GhostUpgrader(
    VERSION_B1, ["Silva Ghost Version", "Silva Ghost Folder"])
indexer_upgrader = UpdateIndexerUpgrader(
    VERSION_B1, "Silva Indexer")
silva_find_upgrader = SilvaFindUpgrader(VERSION_B1, "Silva Find")


class SecondRootUpgrader(BaseUpgrader):

    def upgrade(self, root):
        # Upgrader Silva Views.
        reg = root.service_view_registry
        reg.unregister('add', 'Five Content')
        reg.unregister('add', 'Silva Agenda Filter')
        reg.unregister('add', 'Silva Agenda Item')
        reg.unregister('add', 'Silva Agenda Viewer')
        reg.unregister('add', 'Silva Article')
        reg.unregister('add', 'Silva AutoTOC')
        reg.unregister('add', 'Silva CSV Source')
        reg.unregister('add', 'Silva Folder')
        reg.unregister('add', 'Silva Forum Comment')
        reg.unregister('add', 'Silva Forum Topic')
        reg.unregister('add', 'Silva Forum')
        reg.unregister('add', 'Silva Group')
        reg.unregister('add', 'Silva IP Group')
        reg.unregister('add', 'Silva Link')
        reg.unregister('add', 'Silva News Category Filter')
        reg.unregister('add', 'Silva News Filter')
        reg.unregister('add', 'Silva News Publication')
        reg.unregister('add', 'Silva News Viewer')
        reg.unregister('add', 'Silva Publication')
        reg.unregister('add', 'Silva RSS Aggregator')
        reg.unregister('add', 'Silva Virtual Group')
        reg.unregister('edit', 'Silva Agenda Viewer')
        reg.unregister('edit', 'Silva AutoTOC')
        reg.unregister('edit', 'Silva Find')
        reg.unregister('edit', 'Silva Forum Comment')
        reg.unregister('edit', 'Silva Forum Topic')
        reg.unregister('edit', 'Silva Forum')
        reg.unregister('edit', 'Silva Group')
        reg.unregister('edit', 'Silva IP Group')
        reg.unregister('edit', 'Silva Indexer')
        reg.unregister('edit', 'Silva News Viewer')
        reg.unregister('edit', 'Silva RSS Aggregator')
        reg.unregister('edit', 'Silva Simple Member')
        reg.unregister('edit', 'Silva Virtual Group')
        reg.unregister('preview', 'Silva Image')
        reg.unregister('preview', 'Silva Folder')
        reg.unregister('preview', 'Silva Ghost Folder')
        reg.unregister('preview', 'Silva Publication')
        reg.unregister('preview', 'Silva Root')
        reg.unregister('public', 'Silva Link Version')
        reg.unregister('public', 'Silva CSV Source')
        reg.unregister('public', 'Silva File')
        reg.unregister('public', 'Silva Folder')
        reg.unregister('public', 'Silva Ghost Folder')
        reg.unregister('public', 'Silva Image')
        reg.unregister('public', 'Silva Publication')
        reg.unregister('public', 'Silva Root')

        # Clean service views:
        for directory_id in ['SilvaFind', 'SilvaForum']:
            if directory_id in root.service_views.objectIds():
                root.service_views.manage_delObjects([directory_id])

        # Convert Members folder
        root.manage_renameObject('Members', 'OldMembers')
        root.manage_addProduct['BTreeFolder2'].manage_addBTreeFolder('Members')
        for identifier, member in root.OldMembers.objectItems():
            if identifier not in root.Members.objectIds():
                root.Members._setObject(identifier, aq_base(member))
        root.manage_delObjects(['OldMembers'])

        # Register services
        sm = root.getSiteManager()
        if not IMemberService.providedBy(root.service_members):
            root.manage_delObjects(['service_members'])
            if extensionRegistry.have('silva.pas.base'):
                root.service_extensions.install('silva.pas.base')
            else:
                factory = root.manage_addProduct['Silva']
                factory.manage_addSimpleMemberService()
        else:
            sm.registerUtility(root.service_members, IMemberService)
        container_policy = root.service_containerpolicy
        if hasattr(aq_base(container_policy), '_policies'):
            container_policy._ContainerPolicyRegistry__policies = dict(
                container_policy._policies)
            delattr(container_policy, '_policies')
        sm.registerUtility(
            root.service_containerpolicy, IContainerPolicyService)
        if hasattr(root, 'service_subscriptions'):
            from silva.app.subscriptions.interfaces import ISubscriptionService
            sm.registerUtility(
                root.service_subscriptions, ISubscriptionService)
            template_ids = root.service_subscriptions.objectIds()
            root.service_subscriptions.manage_delObjects(template_ids)
            # This trigger a reconfiguration of the service.
            notify(ObjectCreatedEvent(root.service_subscriptions))
        if hasattr(root, 'service_news'):
            from Products.SilvaNews.interfaces import IServiceNews
            sm.registerUtility(
                root.service_news, IServiceNews)
        if not hasattr(root, 'service_secret'):
            factory = root.manage_addProduct['silva.core.services']
            factory.manage_addSecretService()
        if hasattr(root, 'service_subscriptions_mailhost'):
            root.manage_renameObject(
                'service_subscriptions_mailhost',
                'service_mailhost')
        return root


class SilvaNewsAgendaItemVersionCleanup(BaseUpgrader):

    def validate(self, content):
        if hasattr(content, '_calendar_date_representation'):
            return True
        return False

    def upgrade(self, content):
        del content._calendar_date_representation
        return content


class SilvaNewsAgendaItemRecurrenceUpgrade(BaseUpgrader):
    def validate(self, content):
        return not hasattr(content, '_recurrence')

    def upgrade(self, content):
        content._end_recurrence_datetime = None
        content._recurrence = None
        return content


class CSVSourceUpgrader(BaseUpgrader):

    def upgrade(self, content):
        from Products.SilvaExternalSources.CSVSource import (
            reset_parameter_form, reset_table_layout)
        reset_parameter_form(content)
        reset_table_layout(content)
        return content


csvsource_upgrader = CSVSourceUpgrader(VERSION_B2, 'Silva CSV Source')
second_root_upgrader = SecondRootUpgrader(VERSION_B2, 'Silva Root')
agenda_item_upgrader = SilvaNewsAgendaItemVersionCleanup(
    VERSION_B2, 'Silva Agenda Item Version')
agenda_item_recurrence_upgrader = SilvaNewsAgendaItemRecurrenceUpgrade(
    VERSION_B2, 'Silva Agenda Item Version')


class ThirdRootUpgrader(BaseUpgrader):

    def upgrade(self, content):
        if '_properties' in content.__dict__:
            del content.__dict__['_properties']
        return content


class SilvaNewsFilterUpgrader(BaseUpgrader):

    def validate(self, content):
        return hasattr(content, '_sources')

    def upgrade(self, content):
        root = content.get_root()
        for source in content._sources:
            try:
                target = root.unrestrictedTraverse(source)
            except StandardError as e:
                logger.error('could not find object %s : %s' % (source, e))
                continue
            if target.meta_type in content._allowed_source_types:
                content.add_source(target)
            else:
                logger.warn('Content type %s is not an allowed source' %
                    target.meta_type)
        del content._sources
        return content


class SilvaNewsViewerUpgrader(BaseUpgrader):

    def validate(self, content):
        return hasattr(content, '_filters')

    def upgrade(self, content):
        root = content.get_root()
        for flt in content._filters:
            try:
                target = root.unrestrictedTraverse(flt)
            except StandardError as e:
                logger.error('could not find object %s : %s' % (flt, e))
                continue
            if target.meta_type in content.filter_meta_types:
                content.add_filter(target)
            else:
                logger.warn('Content type %s is not an allowed filter type' %
                    target.meta_type)
        del content._filters
        return content


third_root_upgrarder = ThirdRootUpgrader(VERSION_FINAL, 'Silva Root')
silvanews_filter_upgrader = SilvaNewsFilterUpgrader(VERSION_FINAL,
    ['Silva News Filter', 'Silva Agenda Filter'])
silvanews_viewer_upgrader = SilvaNewsViewerUpgrader(VERSION_FINAL,
    ['Silva News Viewer', 'Silva Agenda Viewer'])


class ReindexUpgrader(BaseUpgrader):

    def upgrade(self, content):
        ICataloging(content).reindex()
        return content


# 2.3.1
silva_news_reindex = ReindexUpgrader('2.3.1',
    ["Silva News Publication", "Silva Article", "Silva Agenda Item"])


