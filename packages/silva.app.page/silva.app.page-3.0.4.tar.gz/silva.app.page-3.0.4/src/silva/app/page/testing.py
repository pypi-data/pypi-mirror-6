# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from silva.core.contentlayout.testing import SilvaContentLayoutLayer
import silva.app.page
import transaction


class SilvaPageLayer(SilvaContentLayoutLayer):
    default_packages = SilvaContentLayoutLayer.default_packages + [
        'silva.core.editor',
        'silva.app.news',
        'silva.app.page',
        ]

    def _install_application(self, app):
        super(SilvaPageLayer, self)._install_application(app)
        app.root.service_extensions.install('silva.core.contentlayout')
        app.root.service_extensions.install('silva.app.news')
        app.root.service_extensions.install('silva.app.page')
        transaction.commit()

FunctionalLayer = SilvaPageLayer(silva.app.page)
