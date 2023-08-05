"""Calxeda: ipdiscover.py"""


# Copyright (c) 2012-2013, Calxeda Inc.
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# * Neither the name of Calxeda Inc. nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
# THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

from cxmanage_api.cli import get_tftp, get_nodes, get_node_strings, run_command


def ipdiscover_command(args):
    """discover server IP addresses"""
    tftp = get_tftp(args)
    nodes = get_nodes(args, tftp)

    if not args.quiet:
        print 'Getting server-side IP addresses...'

    results, errors = run_command(
        args, nodes, 'get_server_ip', args.interface, args.ipv6, args.aggressive
    )

    if results:
        node_strings = get_node_strings(args, results, justify=True)
        print 'IP addresses (ECME, Server)'
        for node in nodes:
            if node in results:
                print '%s: %s' % (node_strings[node], results[node])
        print

    if not args.quiet and errors:
        print 'Some errors occurred during the command.'

    return len(errors) > 0
