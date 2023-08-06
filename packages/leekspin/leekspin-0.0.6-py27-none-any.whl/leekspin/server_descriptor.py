# -*- coding: utf-8 -*-

"""Module for creating ``@type [bridge-]server-descriptor``s.

.. authors:: Isis Lovecruft <isis@torproject.org> 0xA3ADB67A2CDB8B35
             Matthew Finkel <sysrqb@torproject.org>
.. licence:: see LICENSE file for licensing details
.. copyright:: (c) 2013-2014 The Tor Project, Inc.
               (c) 2013-2014 Isis Lovecruft
               (c) 2013-2014 Matthew Finkel
"""

from leekspin import torversions


def makeProtocolsLine(version=None):
    """Generate an appropriate [bridge-]server-descriptor 'protocols' line.

    :param str version: One of ``SERVER_VERSIONS``.
    :rtype: str
    :returns: An '@type [bridge-]server-descriptor' 'protocols' line.
    """
    line = ''
    if (version is not None) and torversions.shouldHaveOptPrefix(version):
        line += 'opt '
    line += 'protocols Link 1 2 Circuit 1'
    return line
