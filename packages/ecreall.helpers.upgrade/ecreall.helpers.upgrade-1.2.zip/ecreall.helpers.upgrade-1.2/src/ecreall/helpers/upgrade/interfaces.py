from zope.interface import Interface


class IUpgradeTool(Interface):
    """ utilities on portal setup to pass upgrade steps """

    def refreshResources():
        """ recook all resources (css, js, kss) """

    def runUpgradeSteps(steps):
        """
        @param steps : tuple of pairs (product, version)
        pass upgrade steps of products

        ex: self.passUpgradeSteps((("alter.my.product", "1.0.2"),
                                   ("alter.your.product", "2.5.4")))
        """

    def runUpgradeStep(profile, destination):
        """
        pass step of product profile towards destination
        ex: self.passUpgradeStep("alter.my.product", "1.0.2")
        self.passUpgradeStep("alter.my.product", 12)
        """

    def runProfile(profile, purge_old=False):
        """Run all steps of a profile
        @param profile : migration profile package + ":" profile name
                         or default profile
        ex: self.runProfile("conf.site.common.upgrades:v1_3_0")
            self.runProfile("conf.site.common")
        """

    def runImportStep(profile, importstep):
        """Run one import step of a profile
        """

    def installProduct(product):
        """
        install product
        """

    def uninstallProduct(product):
        """
        uninstall product
        """

    def reinstallProduct(product):
        """
        reinstall product
        """

    def runUpgradeProfile(profile):
        """
        run an upgrade profile
        """

    def migrateContent(portal_types, method, catalogs=('portal_catalog',),
                       query=None, nofail=True, stop_at_count=0):
        """ apply method on portal_types contents of catalogs
        portal_types can be the name of one or further portal_types,
        or one or further Interfaces wich the content types to migrate implements
        """

    def migrateRoleMappings(portal_types,
                            catalogs=('portal_catalog',), reindex=False,
                            commit=False, stop_at_count=0):
        """ update security mappings on objets after workflow definitions changed
        portal_types can be the name of one or further portal_types,
        or one or further Interfaces wich the content types to migrate implements"""

    def reindexContents(portal_types, indexes=(), query=None, nofail=True,
                        commit=False, stop_at_count=0):
        """Reindex all contents of selected types
        portal_types can be the name of one or further portal_types,
        or one or further Interfaces wich the content types to reindex implements
        """

    def refreshResources():
        """Refresh all resource registries
        """

    def updateIndexes(index_tuples, catalogs=('portal_catalog',), reindex=True):
        """
        add and/or reindex indexes of catalogs
        @param index_tuples list of tuples [(index, index_type)]
        """

    def addMetadata(metadata, catalogs=('portal_catalog',)):
        """Add columns in catalog schema
        """