# -*- coding: utf-8 -*-
###
# (C) Copyright (2012-2016) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###

from pprint import pprint

from config_loader import try_load_from_file
from hpOneView.exceptions import HPOneViewException
from hpOneView.oneview_client import OneViewClient

config = {
    "ip": "",
    "credentials": {
        "userName": "administrator",
        "password": ""
    }
}

options = {
    "name": "OneViewSDK Test Ethernet Network",
    "vlanId": 200,
    "ethernetNetworkType": "Tagged",
    "purpose": "General",
    "smartLink": False,
    "privateNetwork": False,
    "connectionTemplateUri": None,
}

options_bulk = {
    "vlanIdRange": "1-5,7",
    "purpose": "General",
    "namePrefix": "TestNetwork",
    "smartLink": False,
    "privateNetwork": False,
    "bandwidth": {
        "maximumBandwidth": 10000,
        "typicalBandwidth": 2000
    },
    "type": "bulk-ethernet-network"
}

# To run the get by id and get associated uplink group examples you must define an ethernet network id
ethernet_network_id = ''

# Try load config from a file (if there is a config file)
config = try_load_from_file(config)

oneview_client = OneViewClient(config)

# Create an ethernet Network
print("\nCreate an ethernet network")
ethernet_network = oneview_client.ethernet_networks.create(options)
print("Created ethernet-network '{name}' successfully.\n   uri = '{uri}'" .format(**ethernet_network))

# Find recently created network by name
print("\nFind recently created network by name")
ethernet_network = oneview_client.ethernet_networks.get_by(
    'name', 'OneViewSDK Test Ethernet Network')[0]
print("Found ethernet-network by name: '{name}'.\n   uri = '{uri}'" .format(**ethernet_network))

# Update purpose recently created network
print("\nUpdate the purpose attribute from the recently created network")
ethernet_network['purpose'] = 'Management'
ethernet_network = oneview_client.ethernet_networks.update(ethernet_network)
print("Updated ethernet-network '{name}' successfully.\n   uri = '{uri}'\n   with attribute ['purpose': {purpose}]"
      .format(**ethernet_network))

# Get all, with defaults
print("\nGet all ethernet-networks")
ethernet_nets = oneview_client.ethernet_networks.get_all()
for net in ethernet_nets:
    print("   '{name}' at uri: '{uri}'".format(**net))

# Create bulk ethernet networks
print("\nCreate bulk ethernet networks")
ethernet_nets_bulk = oneview_client.ethernet_networks.create_bulk(options_bulk)
pprint(ethernet_nets_bulk)

# Filter by name
print("\nGet all ethernet-networks filtering by name")
ethernet_nets_filtered = oneview_client.ethernet_networks.get_all(
    filter="\"'name'='OneViewSDK Test Ethernet Network'\"")
for net in ethernet_nets_filtered:
    print("   '{name}' at uri: '{uri}'".format(**net))

# Get all sorting by name descending
print("\nGet all ethernet-networks sorting by name")
ethernet_nets_sorted = oneview_client.ethernet_networks.get_all(sort='name:descending')
for net in ethernet_nets_sorted:
    print("   '{name}' at uri: '{uri}'".format(**net))

# Get the first 10 records
print("\nGet the first ten ethernet-networks")
ethernet_nets_limited = oneview_client.ethernet_networks.get_all(0, 10)
for net in ethernet_nets_limited:
    print("   '{name}' at uri: '{uri}'".format(**net))

# Get by Id
try:
    print("\nGet an ethernet-network by id")
    ethernet_nets_byid = oneview_client.ethernet_networks.get(ethernet_network_id)
    pprint(ethernet_nets_byid)
except HPOneViewException as e:
    print(e.msg['message'])

# Get by Uri
print("\nGet an ethernet-network by uri")
ethernet_nets_by_uri = oneview_client.ethernet_networks.get(
    ethernet_network['uri'])
pprint(ethernet_nets_by_uri)

# Get URIs of associated profiles
print("\nGet associated profiles uri(s)")
associated_profiles = oneview_client.ethernet_networks.get_associated_profiles(ethernet_network_id)
pprint(associated_profiles)

# Get URIs of uplink port group
print("\nGet uplink port group uri(s)")
uplink_group_uris = oneview_client.ethernet_networks.get_associated_uplink_groups(ethernet_network_id)
pprint(uplink_group_uris)

# Get the associated uplink set resources
print("\nGet uplink port group uri(s)")
uplink_groups = []
for uri in uplink_group_uris:
    uplink_groups.append(oneview_client.uplink_sets.get(uri))
pprint(uplink_groups)


# Delete bulk ethernet networks
print("\nDelete bulk ethernet networks")
for net in ethernet_nets_bulk:
    oneview_client.ethernet_networks.delete(net)
print("   Done.")

# Delete the created network
print("\nDelete the ethernet network")
oneview_client.ethernet_networks.delete(ethernet_network)
print("Successfully deleted ethernet-network")
