# Copyright (c) Siemens AG, 2013
#
# This file is part of MANTIS.  MANTIS is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either version 2
# of the License, or(at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import sys

import pprint

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from dingos.models import InfoObjectType, InfoObjectNaming

from dingos.management.commands.dingos_manage_naming_schemas import Command as ManageCommand


schema_list = [
    [
        "RegistryItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ServiceItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ProcessItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "UrlHistoryItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "DriverItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Handle",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "FileItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "FilterModule",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "TIPIndicator",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "TimeSpan",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ArpStateTypes",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Issue",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "BatchResult",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "NetworkInfo",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "FileAttributes",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ServiceMode",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "DataFormat",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Section",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ModuleDefinition",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "IpInfo",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ArrayOfDataFormat",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Module",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Trigger",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "PrefetchItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "HookItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "RouteEntryItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "MemorySection",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ParameterValue",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "UserItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "SubsystemType",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ModuleResult",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "RegistryHiveItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "HashItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "FileDownloadHistoryItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "TIPResult",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ScriptCommand",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "VolumeItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Link",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "OrderSpec",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "DnsEntryItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "StreamItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ResourceInfoItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ServiceStatus",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ArpEntryItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "VersionInfoItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ParameterDefinition",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "DiskItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "VolumeFileSystemFlags",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "EventLogItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "SystemRestoreItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "SIDTypes",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "TaskAction",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ModuleItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "CookieHistoryItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "FormHistoryItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "TimelineItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "TIPItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "RouteTypes",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Resource",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "PortItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "StringMatchItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "TaskItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Identity",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "VolumeTypeEnum",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "PersistenceItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ArpCacheTypes",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "SystemInfoItem",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "PartitionInfo",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "Script",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[fact_count_equal_2?][term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0]",
            "[term_of_fact_num_0] [value_of_fact_num_1] [value_of_fact_num_0] ...([fact_count] facts)"
        ]
    ],
    [
        "ioc",
        "ioc",
        "http://schemas.mandiant.com/2010/ioc",
        [
            "[short_description]"
        ]
    ]
]
manage_command = ManageCommand()

pp = pprint.PrettyPrinter(indent=2)

class Command(ManageCommand):
    """

    """
    args = ''
    help = 'Set standard naming schema for InfoObjects from OpenIOC import'

    option_list = BaseCommand.option_list

    def __init__(self, *args, **kwargs):
        kwargs['schemas'] = schema_list
        super(Command,self).__init__(*args,**kwargs)


    def handle(self, *args, **options):
        options['input_list'] = self.schemas
        #manage_command.handle(*args,**options)
        super(Command,self).handle(*args,**options)

