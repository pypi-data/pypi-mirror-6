# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core.contentlayout.testing import SilvaContentLayoutLayer
import silva.app.mediacontent
import transaction


class SilvaMediaContentLayer(SilvaContentLayoutLayer):
    default_packages = SilvaContentLayoutLayer.default_packages + [
        'silva.app.mediacontent',
        'silva.core.editor',
        ]

    def _install_application(self, app):
        super(SilvaMediaContentLayer, self)._install_application(app)
        app.root.service_extensions.install('silva.app.mediacontent')
        transaction.commit()

FunctionalLayer = SilvaMediaContentLayer(silva.app.mediacontent)
