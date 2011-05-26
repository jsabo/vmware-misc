#!/usr/bin/env python

# VMware ESX(i) hardware health monitoring via CIM

# Health Monitoring via CIM blog series
# http://blogs.vmware.com/esxi/2010/04/hardware-health-monitoring-via-cim.html

# VMware CIM SMASH/Server Management API Reference
# http://www.vmware.com/support/developer/cim-sdk/4.0/smash/apirefdoc/

# First import the various python modules we'll need 
import pywbem
import os
import sys
from optparse import OptionParser

# Dictionary to cache class metadata
classData = {}
def friendlyValue(client, instance, propertyName):
   global classData

   # Start out with a default empty string, in case we don't have a mapping
   mapping = ''

   if instance.classname not in classData:
      # Fetch the class metadata if we don't already have it in the cache
      classData[instance.classname] = client.GetClass(instance.classname, IncludeQualifiers=True)

   myClass = classData[instance.classname]

   # Now scan through the qualifiers to look for ValueMap/Values sets
   qualifiers = myClass.properties[propertyName].qualifiers
   if 'ValueMap' in qualifiers.keys() and 'Values' in qualifiers.keys():
      vals = qualifiers['Values'].value
      valmap = qualifiers['ValueMap'].value
      value = instance[propertyName]
      # Find the matching value and convert to the friendly string
      for i in range(0,len(valmap)-1):
         if str(valmap[i]) == str(value):
             mapping = ' ('+vals[i]+')'
             break

   return mapping

# Clear system event log
def doClearSEL(client, selInstance):
   # Invoke method operates on "object paths" not instances
   selPath = selInstance.path
   try:
      print 'Clearing SEL for %s' % (selPath['InstanceID'])
      (retval, outparams) = client.InvokeMethod('ClearLog', selPath)
      retval = 0
      if retval == 0:
         print 'Completed'
      elif retval == 1:
         print 'Not supported'
      else:
         print 'Error: ' + retval
   except pywbem.CIMError, arg:
      print 'Exception: ' + arg[1]

# Display an instance
def printInstance(client, instance):
   print instance.classname
   for propertyName in sorted(instance.keys()):
      if instance[propertyName] is None:
         # skip over null properties
         continue
      print '%30s = %s%s' % (propertyName, instance[propertyName],
                              friendlyValue(client, instance, propertyName))

# Get namespaces
def getNamespaces(options):
   client = pywbem.WBEMConnection('https://'+options.server,
                                  (options.username, options.password),
                                  'root/interop')
   list = client.EnumerateInstances('CIM_Namespace', PropertyList=['Name'])
   return set(map(lambda x: x['Name'], list))

# Simple function to dump out asset information
def dumpAssetInformation(server, username, password, clearSEL):
   client = pywbem.WBEMConnection('https://'+options.server,
                                  (options.username, options.password),
                                  'root/cimv2')
   if clearSEL == True:
      for instance in client.EnumerateInstances('CIM_RecordLog'):
         printInstance(client, instance)
         doClearSEL(client, instance)
   else:
      list = []
      for classname in ['CIM_RecordLog', 'CIM_LogRecord', 'CIM_StorageVolume', 'CIM_EthernetPort']:
         list.extend(client.EnumerateInstances(classname))
      if len(list) == 0:
         print 'Error: Unable to locate any instances'
      else:
         for instance in list:
            printInstance(client, instance)

if __name__ == '__main__':
   # Some command line argument parsing gorp to make the script a little more
   # user friendly.
   usage = '''Usage: %prog [options]

      This program will dump some basic asset information from an ESX host
      specified by the -s option.'''
   parser = OptionParser(usage=usage)
   parser.add_option('-s', '--server', dest='server',
                     help='Specify the server to connect to')
   parser.add_option('-u', '--username', dest='username',
                     help='Username (default is root)')
   parser.add_option('-p', '--password', dest='password',
                     help='Password (default is blank)')
   parser.add_option('-n', '--namespace', dest='namespace', default='root/cimv2',
                     help='Which namespace to access (default is root/cimv2)')
   parser.add_option('-N', '--namspaceonly', dest='namespaceonly', action='store_true',
                     help='Dump the list of namespaces on this system',
                     default=False)
   parser.add_option('-c', '--clearSEL', dest='clearSEL',
                     help='Clear the IPMI SEL', default=False, action='store_true')

   (options, args) = parser.parse_args()
   if options.server is None:
      print 'You must specify a server to connect to.  Use --help for usage'
      sys.exit(1)
   if options.username is None:
      options.username = 'root'
   if options.password is None:
      options.password = ''

   if options.namespaceonly is True:
      for namespace in getNamespaces(options):
         print '%s' % namespace
      sys.exit(0)

   client = pywbem.WBEMConnection('https://'+options.server,
                                  (options.username, options.password),
                                  options.namespace)

   dumpAssetInformation(options.server, options.username, options.password, options.clearSEL)
