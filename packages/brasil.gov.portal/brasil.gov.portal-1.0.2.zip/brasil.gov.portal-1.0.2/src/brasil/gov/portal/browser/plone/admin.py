# -*- coding:utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl.Permissions import view as View
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.browser.admin import AddPloneSite as AddPloneSiteView
from Products.CMFPlone.browser.admin import Overview as OverviewView
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.interfaces import IPloneSiteRoot


class Overview(OverviewView):

    def sites(self, root=None):
        if root is None:
            root = self.context

        result = []
        secman = getSecurityManager()
        for obj in root.values():
            if IPloneSiteRoot.providedBy(obj):
                if secman.checkPermission(View, obj):
                    result.append(obj)
            elif obj.getId() in getattr(root, '_mount_points', {}):
                result.extend(self.sites(root=obj))
        return result

    def outdated(self, obj):
        mig = obj.get('portal_migration', None)
        if mig is not None:
            return mig.needUpgrading()
        return False

    def can_manage(self):
        secman = getSecurityManager()
        return secman.checkPermission(ManagePortal, self.context)

    def upgrade_url(self, site, can_manage=None):
        if can_manage is None:
            can_manage = self.can_manage()
        if can_manage:
            return site.absolute_url() + '/@@plone-upgrade'
        else:
            return self.context.absolute_url() + '/@@plone-root-login'


class AddPloneSite(AddPloneSiteView):

    def __call__(self):
        context = self.context
        form = self.request.form
        submitted = form.get('form.submitted', False)
        if submitted:
            extension_ids = form.get('extension_ids', ())
            # Criamos com conteúdo inicial
            extension_ids.insert(0, 'brasil.gov.portal:default')
            extension_ids.insert(1, 'brasil.gov.portal:initcontent')
            site_id = form.get('site_id', 'Plone')
            title_1 = form.get('title_1', '')
            title_2 = form.get('title_2', '')
            title = '%s %s' % (title_1, title_2)
            site = addPloneSite(
                context, site_id,
                title=title,
                description=form.get('description', ''),
                profile_id=form.get('profile_id', _DEFAULT_PROFILE),
                extension_ids=form.get('extension_ids', ()),
                setup_content=False,
                default_language='pt-br',
            )
            site.manage_changeProperties(title=title)
            site.manage_changeProperties(title_1=title_1)
            site.manage_changeProperties(title_2=title_2)
            site.manage_changeProperties(orgao=form.get('orgao', ''))
            self.request.response.redirect(site.absolute_url())

        return self.index()
