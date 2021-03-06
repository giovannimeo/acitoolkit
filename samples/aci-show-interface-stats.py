#!/usr/bin/env python
# Copyright (c) 2014 Cisco Systems
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
"""
Simple application that logs on to the APIC and displays all
of the Interfaces.
"""
import sys
import acitoolkit.acitoolkit as ACI
from acisampleslib import get_login_info

# Take login credentials from the command line if provided
# Otherwise, take them from your environment variables file ~/.profile
description = 'Simple application that logs on to the APIC and displays stats for all of the Interfaces.'
parser = get_login_info(description)
parser.add_argument('-i', '--interface',
                    type=str, 
                    help='Specify a particular interface node/pod/module/port e.g. 1/201/1/21')
parser.add_argument('-e', '--epoch', type=int,
                    default = 0,
                    help='Show a particular epoch (default=0)')
parser.add_argument('-g', '--granularity', type=str,
                    default = '5min',
                    help='Show a particular granularity (default="5min")')
parser.add_argument('-f', '--full', action="store_true",
                    help='Show full statistics - only available if interface is specified')
args = parser.parse_args()

# Login to APIC
session = ACI.Session(args.url, args.login, args.password)
resp = session.login()
if not resp.ok:
    print '%% Could not login to APIC'
    sys.exit(0)

def show_stats_short() :
    
    # setup template and display header information
    template = "{0:17} {1:12} {2:12} {3:16} {4:16} {5:16} {6:16}"
    print 'Granularity:',args.granularity, 'Epoch:',args.epoch
    print template.format("   INTERFACE  ", "TOT RX PACKETS", "TOT TX PACKETS", "RX PKTs/Sec", "TX PKTs/Sec", "RX BYTES/Sec", "TX BYTES/Sec")
    print template.format("--------------", "------------ ", "------------ ", "---------------",
                          "---------------", "---------------", "---------------")
    template = "{0:17} {1:12,} {2:12,} {3:16,.2f} {4:16,.2f} {5:16,.2f} {6:16,.2f}"
    
    for interface in sorted(interfaces):
        interface.stats.get()
        
        rec = []
        for (counterFamily, counterName) in [('ingrTotal','pktsAvg'),('egrTotal','pktsAvg'),
                                ('ingrTotal','pktsRateAvg'),('egrTotal','pktsRateAvg'),
                                ('ingrTotal','bytesRateAvg'),('egrTotal','bytesRateAvg')] :
            
            rec.append(interface.stats.retrieve(counterFamily,args.granularity,args.epoch,counterName))
            
        print template.format(interface.name, *rec)
        
def show_stats_long() :
    print 'Interface {0}/{1}/{2}/{3}  Granularity:{4} Epoch:{5}'.format(pod,node,module,port,args.granularity, args.epoch)
    stats = interfaces[0].stats.get()
    for statsFamily in sorted(stats) :
        print statsFamily
        if args.granularity in stats[statsFamily] :
            if args.epoch in stats[statsFamily][args.granularity] :
                for counter in sorted(stats[statsFamily][args.granularity][args.epoch]) :
                    print '    {0:>16}: {1}'.format(counter, stats[statsFamily][args.granularity][args.epoch][counter])
        

# Download all of the interfaces and get their stats
# and display the stats

if args.interface :
    (pod, node, module, port) = args.interface.split('/')
    interfaces = ACI.Interface.get(session, pod, node, module, port)
else :
    interfaces = ACI.Interface.get(session)

if not args.full or not args.interface :
    show_stats_short()
else :
    show_stats_long()
    


    

