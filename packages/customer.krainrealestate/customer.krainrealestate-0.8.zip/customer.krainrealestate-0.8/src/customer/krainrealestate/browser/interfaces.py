# -*- coding: utf-8 -*-
"""Interface definitions."""

# zope imports
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IKrainRealestate(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IKrainViewlets(Interface):
    """Marker Interface for the customer specific Viewlets"""

class IAgentFolder(Interface):
    """Marker Interface to identify AgentFolders"""
