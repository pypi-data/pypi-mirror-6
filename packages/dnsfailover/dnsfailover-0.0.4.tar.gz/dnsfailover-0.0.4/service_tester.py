#!/usr/bin/env python
#####################################################
# This script updates dynamic dns zones according   #
# to node health which allows dns failover to occur #
#####################################################
import os,sys,subprocess, traceback, socket
import ConfigParser, random
import dns.resolver, dns.update, dns.tsigkeyring
from subprocess import Popen, PIPE

#################################################################
# Parse the configuration file into a dictionary of dictionaries
def read_config(config_file):
  print "Parsing configuration file at [%s]" % config_file
  config_options = {}
  config = ConfigParser.RawConfigParser()
  try:
    config.read(config_file)
    for record in config.sections():
      config_options[record] = {}
      for item in ['zone', 'nodes', 'dns_update_host', 'failover_type', 'key', 'check_script']:
        config_options[record][item] = config.get(record, item)

    for zone in config_options:
      config_options[record]['nodes'] = config_options[record]['nodes'].split(',')
  except:
    print "Error parsing configuration file [%s]"  % config_file
    print traceback.print_exc()
    sys.exit(1)
  return config_options


##########################################
# Actually perform the dns update attempt
def update_dns(zone, record, dns_update_host, new_ip, key):
  record = record.split('.')[0]             # we use just the non-fqdn record, not the full record.
  print "Updating zone [%s] record [%s] on dns host [%s] with new ip [%s]" % (zone, record, dns_update_host, new_ip)
  keyring = dns.tsigkeyring.from_text({zone : key})
  update = dns.update.Update(zone, keyring = keyring, keyname = zone, keyalgorithm = 'hmac-sha512')
  update.replace(record, 60, 'A', new_ip)
  response = dns.query.tcp(update, dns_update_host)
  sys.exit(0)


#############################################################
# See if an update is needed, and if so, call out to do this
def check_dns(record, zone, failover_type, key, good_hosts, dns_update_server):

  resolver_obj = dns.resolver.Resolver(configure=False)
  resolver_obj.nameservers = [dns_update_server]

  try:
    records = resolver_obj.query(record, 'A')
  except:
    print "Error when attempting to resolve [%s]"  % (record)
    print traceback.print_exc()
    sys.exit(1)

  if len(records) > 1:
    print 'More than one A record returned for record [%s]; I\'m scared ! - not proceeding with an update' % record
    sys.exit(1)

  current_record = str(records[0])

  print "Record in DNS before: %s" % current_record

  random_server = random.choice(good_hosts)
  print "Random server, if needed for update: %s" % random_server

  if failover_type == 'prio' and good_hosts[0] != current_record:
    print 'prio update'
    update_dns(zone, record, dns_update_server, good_hosts[0], key)

  elif failover_type == 'sticky' and current_record not in good_hosts:
    print 'sticky update'
    update_dns(zone, record, dns_update_server, good_hosts[0], key)

  elif failover_type == 'random' and current_record != random_server:
    print 'random update'
    update_dns(zone, record, dns_update_server, random_server, key)

  else:
    print 'DNS update is not needed.'
    sys.exit(0)


###########################################
# Check each node against the check_script
def check_nodes(config):
  for record_name, record_items in config.iteritems():
    record_items['good_nodes'] = []

    # Check each host against the check script
    for node in record_items['nodes']:
      node = node.rstrip()      # remove the newline on the last entry
      try:
        node_name = socket.gethostbyaddr(node)[0]
      except:
        print "Could not get hostname of ip [%s]"  % node
        print traceback.print_exc()
        sys.exit(1)

      p = Popen([record_items['check_script'], node_name], stdout=PIPE)    # FixMe: check script exists, and check permissions are root:root 750
      output = p.communicate()[0]
      return_code = p.returncode

      if (return_code == 0):
        record_items['good_nodes'].append(node)

    # If we've got nodes that pass the check script, see if we need to make dns alterations
    if len(record_items['good_nodes']) > 0:
      check_dns(record_name, record_items['zone'], record_items['failover_type'], record_items['key'], record_items['good_nodes'], record_items['dns_update_host'])
    else:
      print "Oh noes ! - No good nodes for record [%s] in zone [%s]" % (record_name, record_items['zone'])
      # ToDo: log syslog message here


###############
### MAIN () ###
###############
if len(sys.argv) >= 2:
  config_file = sys.argv[1]
else:
  config_file = '/etc/failover_list'

config = read_config(config_file)
check_nodes(config)
