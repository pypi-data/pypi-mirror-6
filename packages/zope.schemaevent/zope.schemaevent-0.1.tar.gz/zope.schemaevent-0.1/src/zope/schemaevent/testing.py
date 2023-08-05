# -*- coding: utf-8 -*-
import zope.schemaevent
from plone.testing.zca import ZCMLSandbox


ZC_LAYER = ZCMLSandbox(package=zope.schemaevent,
                       filename='configure.zcml')
