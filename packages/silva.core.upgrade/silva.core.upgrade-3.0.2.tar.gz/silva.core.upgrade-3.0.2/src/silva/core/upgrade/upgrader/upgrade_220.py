# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging
import os

from ZPublisher.BeforeTraverse import unregisterBeforeTraverse
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.location.interfaces import ISite
from zope.site.hooks import setSite, setHooks
from OFS.SimpleItem import SimpleItem
import ZODB.broken
import zope.interface

try:
    # Old FiveSiteManager. This have been removed in Zope 2.12.
    from Products.Five.site.interfaces import IFiveSiteManager
except ImportError:
    IFiveSiteManager = None

from Acquisition import aq_base

from silva.core import interfaces
from silva.core import conf as silvaconf
from silva.core.services.catalog import CatalogService
from silva.core.services.interfaces import IMetadataService
from silva.core.services.interfaces import IExtensionService
from silva.core.services.interfaces import ICatalogService, IFilesService
from silva.core.upgrade.localsite import setup_intid
from silva.core.upgrade.silvaxml import NAMESPACES_CHANGES
from silva.core.upgrade.upgrade import BaseUpgrader, AnyMetaType, content_path
from silva.core.interfaces import IPostUpgrader

from Products.Silva.File import BlobFile, File
from Products.SilvaExternalSources.interfaces import ICodeSourceService
from Products.Silva.install import configure_metadata

logger = logging.getLogger('silva.core.upgrade')


#-----------------------------------------------------------------------------
# 2.1.0 to 2.2.0a1
#-----------------------------------------------------------------------------

VERSION_A1='2.2a1'


class SilvaFileSystemFile(File):
    silvaconf.baseclass()
    _file = None

    def get_file_fd(self):
        return open(self._file.get_filename(), 'rb')


class ExtFile(SimpleItem):
    meta_type = 'ExtFile'
    filename = ''
    content_type = ''

    def get_filename(self):
        """Return the filename on the filesystem from the file.
        """
        path = [os.environ['EXTFILE_REPOSITORY_PATH']]
        if isinstance(self.filename, list):
            path.extend(self.filename)
        elif self.filename != '':
            path.append(self.filename)
        return os.path.join(*path)

    def get_size(self):
        with open(self.get_filename(), 'rb') as stream:
            stream.seek(0, 2)
            return stream.tell()


class RootUpgrader(BaseUpgrader):

    def upgrade(self, root):
        # If it's a Five site manager disable it first. The annoying
        # part might be that the code might already have been removed
        # from Zope ...
        setattr(root, '__initialization__', True)
        if ISite.providedBy(root):
            sm = root.getSiteManager()
            if ((IFiveSiteManager is not None and
                 IFiveSiteManager.providedBy(sm)) or
                isinstance(sm, ZODB.broken.Broken)):
                setSite(None)
                setHooks()
                unregisterBeforeTraverse(aq_base(root), '__local_site_hook__')
                if hasattr(aq_base(root), '__local_site_hook__'):
                    delattr(aq_base(root), '__local_site_hook__')
                zope.interface.noLongerProvides(root, ISite)
                root.setSiteManager(None)
            else:
                # Cleanup broken utilities
                for registration in list(sm.registeredUtilities()):
                    if isinstance(registration.component, ZODB.broken.Broken):
                        sm.unregisterUtility(
                            registration.component,
                            registration.provided)

        # Activate local site, add an intid service.
        ism = interfaces.ISiteManager(root)
        if not ism.is_site():
            ism.make_site()
        setSite(root)
        setHooks()

        # Delete unused Silva Document service
        for s in ['service_doc_previewer',
                  'service_nlist_previewer',
                  'service_sub_previewer',]:
            if hasattr(root, s):
                root.manage_delObjects([s,])

        # Update service_files settings
        service_files = root.service_files
        if hasattr(aq_base(service_files), '_filesystem_storage_enabled'):
            service_files.storage = BlobFile
            delattr(service_files , '_filesystem_storage_enabled')
        elif service_files.storage is not BlobFile:
            # For the upgrade
            service_files.storage = BlobFile

        # Disable quota verification (but not accounting if this
        # enabled) during the migration, so the file migration can
        # safely happens.
        root.service_extensions._quota_verify = False
        return root


root_upgrader = RootUpgrader(VERSION_A1, 'Silva Root')

class RootPostUpgrader(BaseUpgrader):
    implements(IPostUpgrader)

    def upgrade(self, root):
        # Rest quota verification if this was enabled.
        root.service_extensions._quota_verify = root.service_extensions._quota_enabled
        return root

root_post_upgrader = RootPostUpgrader(VERSION_A1, 'Silva Root')



#-----------------------------------------------------------------------------
# 2.2.0a1 to 2.2.0a2
#-----------------------------------------------------------------------------


VERSION_A2='2.2a2'


class AllowedAddablesUpgrader(BaseUpgrader):
    """Convert allowed addable attributes on containers.
    """

    tags = {'pre',}

    def validate(self, obj):
        return interfaces.IContainer.providedBy(obj)

    def upgrade(self, obj):
        clean_obj = aq_base(obj)
        if hasattr(clean_obj,'_addables_allowed_in_publication'):
            clean_obj._addables_allowed_in_container = \
                clean_obj._addables_allowed_in_publication
            del clean_obj._addables_allowed_in_publication
        elif not hasattr(clean_obj, '_addables_allowed_in_container'):
            clean_obj._addables_allowed_in_container = None
        return obj


allowed_addables_upgrader = AllowedAddablesUpgrader(VERSION_A2, AnyMetaType)

#-----------------------------------------------------------------------------
# 2.2.0a2 to 2.2.0b1
#-----------------------------------------------------------------------------

VERSION_B1='2.2b1'

class SecondRootUpgrader(BaseUpgrader):
    """Change standard_error_message to default_standard_error_message.
    """

    def upgrade(self, root):
        # Register service_files and others
        sm = root.getSiteManager()
        sm.registerUtility(root.service_files, IFilesService)
        if hasattr(aq_base(root), 'service_codesources'):
            # We should have it however ...
            sm.registerUtility(
                root.service_codesources, ICodeSourceService)

        # Register service extensions.
        sm.registerUtility(root.service_extensions, IExtensionService)

        # Update metadata service
        metadata = root.service_metadata
        sm.registerUtility(metadata, IMetadataService)

        # Update the catalog
        setup_intid(root)
        catalog = root.service_catalog
        catalog.__class__ = CatalogService
        sm.registerUtility(catalog, ICatalogService)
        indexes = catalog._catalog.indexes
        for key, index in indexes.items():
            if index.__class__.__name__ == 'ProxyIndex':
                del indexes[key]
        catalog._catalog.indexes = indexes
        # We reinitialize the metadata sets to recreate indexes
        for mset in metadata.collection.objectValues():
            for melt in mset.objectValues():
                if ('doc_attr' in melt.index_constructor_args and
                    melt.index_constructor_args['doc_attr'] == 'proxy_value'):
                    del melt.index_constructor_args['doc_attr']
                if melt.index_type == 'TextIndex':
                    melt.index_type = 'ZCTextIndex'
                    melt.index_constructor_args.update(
                        {'index_type': 'Cosine Measure',
                         'lexicon_id': 'silva_lexicon'})
            mset.initialized = 0
            mset.initialize()

        if hasattr(aq_base(root), 'service_annotations'):
            root.manage_delObjects(['service_annotations'])

        # Be sure the metadata are configured to be able to install the missing products.
        configure_metadata(root.service_metadata, None)
        # Setup the cs_toc and cs_citation CS's.
        service_ext = root.service_extensions
        if not service_ext.is_installed('SilvaExternalSources'):
            service_ext.install('SilvaExternalSources')
        else:
            service_ext.refresh('SilvaExternalSources')
        if root._getOb('cs_toc', None) is None:
            toc = root.service_codesources.get_installable_source(
                'cs_toc')
            toc.install(root)
        if root._getOb('cs_citation', None) is None:
            cit = root.service_codesources.get_installable_source(
                'cs_citation')
            cit.install(root)

        return root

second_root_upgrader = SecondRootUpgrader(VERSION_B1, 'Silva Root', 50)


class MetadataSetUpgrader(BaseUpgrader):
    """Update the namespaces of existing metadata sets NOTE: this
    'may' not be needed, since I think the metadata sets _are_
    reinstalled during the refresh, but we do it here for good measure.
    """

    def upgrade(self, obj):
        sm = obj.service_metadata
        sets = sm.getCollection().getMetadataSets()
        for s in sets:
            prefix,uri = s.getNamespace()
            if NAMESPACES_CHANGES.has_key(uri):
                s.setNamespace(NAMESPACES_CHANGES[uri], prefix)
        return obj


metadata_set_upgrader = MetadataSetUpgrader(VERSION_B1, 'Silva Root', 40)


class MetadataUpgrader(BaseUpgrader):
    """Migrate metadata information.
    """

    tags = {'pre',}

    def validate(self, content):
        if not (interfaces.ISilvaObject.providedBy(content) or
                interfaces.IVersion.providedBy(content)):
            return False
        annotations = getattr(aq_base(content), '_portal_annotations_', None)
        return annotations is not None

    def upgrade(self, content):
        logger.info('Upgrading metadata for: %s.', content_path(content))
        new_annotations = IAnnotations(aq_base(content))
        old_annotations = getattr(aq_base(content), '_portal_annotations_')
        for key in old_annotations.keys():
            old_data = old_annotations[key]
            # if it is metadata, we have to update the namespaces
            # as well inside the data, they will go directly in
            # the annotation
            if key == 'http://www.infrae.com/xml/metadata':
                for old_key in old_data.keys():
                    if old_key in NAMESPACES_CHANGES:
                        new_key = NAMESPACES_CHANGES[old_key]
                    else:
                        new_key = old_key
                    new_annotations[new_key] = old_data[old_key]
            else:
                new_annotations[key] = old_data

        # remove old annotations
        del aq_base(content)._portal_annotations_
        return content


metadata_upgrader = MetadataUpgrader(VERSION_B1, AnyMetaType)
