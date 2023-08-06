# -*- coding: utf-8 -*-
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("customer.krainrealestate")


def initialize(context):
    from Products.PlonePAS import config
    MEMBER_IMAGE_SCALE = (266, 266)
    config.IMAGE_SCALE_PARAMS['scale'] = MEMBER_IMAGE_SCALE
