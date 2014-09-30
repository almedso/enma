# -*- coding: utf-8 -*-
#
# Copyright (c) 2014  Volker Kempert
#
# pylint: disable=I0011, E1103
#
# I0011 - locally disable pylint rules
# E1103 - Instance of a string has no version - pkg_resource specifics
#
"""
@file
Get and display version of a package or packages
"""
import pkg_resources


def get_version(packages=[], include_local=True):
    """
    @brief determine the version of a package or packages
    @param packages List of package names where the version is calculated
           If the list is empty, the only local version is determined based on 
           a potentially existing _version.py file in home of source
    @param include_local Also consider the local version
    @return list of ( package name, version ) tuples 
    """
    versions = []
    if include_local:
        versions = [('internal', get_local_version())]
    if 0 < len(packages):
        for distribution in packages:
            try:
                version = pkg_resources.get_distribution(distribution).version
            except pkg_resources.VersionConflict:
                version = 'version conflict'
            except pkg_resources.ExtractionError:
                version = 'extraction error'
            except pkg_resources.DistributionNotFound:
                version = 'distribution not found'
            except pkg_resources.UnknownExtra:
                version = 'unknown extra'
            versions.append((distribution, version))
    return versions


def get_local_version():
    """
    Pick the version from the local file
    """
    try:
        from _version import __version__
        return __version__
    except ImportError:
        return 'unknown'
