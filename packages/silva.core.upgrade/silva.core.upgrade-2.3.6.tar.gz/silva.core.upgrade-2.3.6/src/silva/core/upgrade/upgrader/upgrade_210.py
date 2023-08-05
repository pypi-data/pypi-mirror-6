# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# silva imports
from silva.core.interfaces import ISilvaObject, IRoot
from silva.core.upgrade.upgrade import BaseUpgrader

import logging

logger = logging.getLogger('silva.core.upgrade')

#-----------------------------------------------------------------------------
# 2.0.0 to 2.1.0
#-----------------------------------------------------------------------------

VERSION='2.1'

class AutoTOCUpgrader(BaseUpgrader):

    def upgrade(self, autotoc):
        logger.info('Upgrading AutoTOC: %s' % autotoc.get_title_or_id())
        if not hasattr(autotoc,'_local_types'):
            autotoc._local_types = ['Silva Document', 'Silva Publication',
                                 'Silva Folder']
        if not hasattr(autotoc, '_toc_depth'):
            autotoc._toc_depth = -1
        if not hasattr(autotoc, '_display_desc_flag'):
            autotoc._display_desc_flag = False
        if not hasattr(autotoc, '_sort_order'):
            autotoc._sort_order = "silva"
        if not hasattr(autotoc, '_show_icon'):
            autotoc._show_icon = False
        autotoc.index_object()
        return autotoc


AutoTOCUpgrader = AutoTOCUpgrader(VERSION, 'Silva AutoTOC')


class DocumentUpgrader(BaseUpgrader):
    """Upgrade.
    """

    def upgrade(self, obj):
        obj._clean_cache()
        return obj


DocumentUpgrader = DocumentUpgrader(VERSION, 'Silva Document')


class CleanRolesUpgrader(BaseUpgrader):
    """Calls sec_clean_roles on each ISilvaObject to remove any stale
    username->rolemappings (bug #100561)"""

    def upgrade(self, obj):
         if IRoot.providedBy(obj):
             logger.info("Cleaning Stale Role Mappings: this may take some time")
         if ISilvaObject.providedBy(obj):
             obj.sec_clean_roles()
         return obj


## taking this upgrader out, until we can fix sec_clean_roles to
## get around the get_valid_userids OverFlowError issue.
##cleanRolesUpgrader = CleanRolesUpgrader(VERSION, AnyMetaType)
