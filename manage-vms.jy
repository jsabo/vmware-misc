#!/usr/bin/env jython

# TO DO
# list resource pools
# list datastores
# list virtual networks
# license esx
# Install VMware tools in Guest
# Other host operations

# import vijava and friends
from java.net import URL
from optparse import OptionParser, OptionGroup, SUPPRESS_HELP
from com.vmware.vim25 import VirtualMachineCapability
from com.vmware.vim25 import VirtualMachineConfigInfo
from com.vmware.vim25 import VirtualMachineConfigSpec
from com.vmware.vim25 import VirtualMachineFileInfo
from com.vmware.vim25 import VirtualDeviceConfigSpec
from com.vmware.vim25 import VirtualDeviceConfigSpecOperation
from com.vmware.vim25 import VirtualDeviceConfigSpecFileOperation
from com.vmware.vim25 import VirtualLsiLogicController
from com.vmware.vim25 import VirtualSCSISharing
from com.vmware.vim25 import VirtualDisk
from com.vmware.vim25 import VirtualDiskFlatVer2BackingInfo
from com.vmware.vim25 import VirtualPCNet32
from com.vmware.vim25 import VirtualEthernetCardNetworkBackingInfo
from com.vmware.vim25 import Description
from com.vmware.vim25 import OptionValue
from com.vmware.vim25.mo import Folder
from com.vmware.vim25.mo import InventoryNavigator
from com.vmware.vim25.mo import ManagedEntity
from com.vmware.vim25.mo import ServiceInstance
from com.vmware.vim25.mo import VirtualMachine

def getServiceInstance(svr,user,passwd,skipSSL):
    """ 
    Connect to ESX and return service instance
    """
    url = URL("https://%s/sdk" % svr)
    si = ServiceInstance(url,user,passwd,skipSSL)
    return si

def listVm(vm):
    if "PowerOnVM_Task" in vm.getDisabledMethod():
        state = "ON"
    else:
        state = "OFF"
    FORMAT = '%-22s %-36s %-36s %-3s %-10s %-20s %-4s'
    print FORMAT % ('VM Name', 'UUID', 'OS Full Name', 'CPU', 'MEM', 'Annotation', 'Power')
    print FORMAT % ('=' * 22, '=' * 36, '=' * 36, '=' * 3, '=' * 10, '=' * 20, '=' * 4) 
    print FORMAT % (vm.getName(),vm.getConfig().uuid,vm.getConfig().getGuestFullName(),
                    vm.getConfig().hardware.numCPU,vm.getConfig().hardware.memoryMB,
                    vm.getConfig().annotation,state)
                    
def listVms(vms):
    """
    Print virtual machines registered in the inventory
    """
    FORMAT = '%-22s %-36s %-36s %-3s %-10s %-20s %-4s'
    print FORMAT % ('VM Name', 'UUID', 'OS Full Name', 'CPU', 'MEM', 'Annotation', 'Power')
    print FORMAT % ('=' * 22, '=' * 36, '=' * 36, '=' * 3, '=' * 10, '=' * 20, '=' * 4)
    for vm in vms:
        if "PowerOnVM_Task" in vm.getDisabledMethod():
            state = "ON"
        else:
            state = "OFF"
        print FORMAT % (vm.getName(),vm.getConfig().uuid,vm.getConfig().getGuestFullName(),
                        vm.getConfig().hardware.numCPU,vm.getConfig().hardware.memoryMB,
                        vm.getConfig().annotation,state)

def createScsiSpec(scsiBusKey):
    """
    Define a virtual scsi ctrl spec
    """
    scsiSpec = VirtualDeviceConfigSpec()
    scsiSpec.setOperation(VirtualDeviceConfigSpecOperation.add)
    scsiCtrl = VirtualLsiLogicController()
    scsiCtrl.setKey(scsiBusKey)
    scsiCtrl.setBusNumber(0)
    scsiCtrl.setSharedBus(VirtualSCSISharing.noSharing)
    scsiSpec.setDevice(scsiCtrl)

    return scsiSpec

def createDiskSpec(datastoreName,scsiBusKey,diskSizeKB,diskMode):
    """
    Define a virtual disk spec
    """
    diskSpec = VirtualDeviceConfigSpec()
    diskSpec.setOperation(VirtualDeviceConfigSpecOperation.add)
    diskSpec.setFileOperation(VirtualDeviceConfigSpecFileOperation.create)
    vd = VirtualDisk()
    vd.setCapacityInKB(diskSizeKB)
    diskSpec.setDevice(vd)
    vd.setKey(0)
    vd.setUnitNumber(0)
    vd.setControllerKey(scsiBusKey)
    diskfileBacking = VirtualDiskFlatVer2BackingInfo()
    fileName = "["+datastoreName+"]"
    diskfileBacking.setFileName(fileName)
    diskfileBacking.setDiskMode(diskMode)
    diskfileBacking.setThinProvisioned(True)
    vd.setBacking(diskfileBacking)

    return diskSpec

def createNicSpec(netName,nicName):
    """
    Define a virtual nic spec
    """
    nicSpec = VirtualDeviceConfigSpec()
    nicSpec.setOperation(VirtualDeviceConfigSpecOperation.add)
    nic = VirtualPCNet32()
    nicBacking = VirtualEthernetCardNetworkBackingInfo()
    nicBacking.setDeviceName(netName)
    info = Description()
    info.setLabel(nicName)
    info.setSummary(netName)
    nic.setDeviceInfo(info)
    # type: "generated", "manual", assigned" by VC
    nic.setAddressType("generated")
    nic.setBacking(nicBacking)
    nic.setKey(0)
    nicSpec.setDevice(nic)

    return nicSpec

def createVmSpec(name,cpuCount,memorySizeMB,guestOsId,annotation,scsiSpec,diskSpec,nicSpec,datastoreName):
    """
    Create virtual machine from specs
    """
    # Create vm spec
    vmSpec = VirtualMachineConfigSpec()
    vmSpec.setName(name)
    vmSpec.setNumCPUs(cpuCount)
    vmSpec.setMemoryMB(memorySizeMB)
    vmSpec.setGuestId(guestOsId)
    vmSpec.setAnnotation(annotation)
    bootOrder = OptionValue()
    bootOrder.setKey("bios.bootDeviceClasses")
    bootOrder.setValue("allow:net,cd,hd")
    vmSpec.extraConfig = [bootOrder]
    vmSpec.setDeviceChange([scsiSpec,diskSpec,nicSpec])

    # Create file info for the vmx file
    vmfi = VirtualMachineFileInfo()
    vmfi.setVmPathName("["+datastoreName+"]")
    vmSpec.setFiles(vmfi)

    return vmSpec

def deleteVm(vm):
    """
    Delete given virtual machine
    """
    vmname = vm.getName()
    if "PowerOnVM_Task" in vm.getDisabledMethod():
        powerOffVm(vm)
        
    task = vm.destroy_Task()
    if task.waitForMe() == "success":
        print "%s has been deleted" % (vmname)
    else:
        print "%s could not be deleted" % (vmname)

def powerOnVm(vm):
    """ 
    Power on virtual machine
    """
    if "PowerOnVM_Task" in vm.getDisabledMethod():
        print "%s is already powered ON" % vm.getName()
    else:
        task = vm.powerOnVM_Task(None)
        if task.waitForMe() == "success":
            print "%s is being powered ON" % vm.getName()
        else:
            print "%s could not be powered ON" % vm.getName()

def powerOffVm(vm):
    """
    Power off virtual machine
    """
    if "PowerOffVM_Task" in vm.getDisabledMethod():
        print "%s is already powered OFF" % vm.getName()
    else:
        task = vm.powerOffVM_Task()
        if task.waitForMe() == "success":
            print "%s is being powered OFF" % vm.getName()
        else:
            print "%s could not be powered OFF" % vm.getName()

def resetVm(vm):
    """
    Reset virtual machine power
    """
    if "ResetVM_Task" in vm.getDisabledMethod():
        print "%s can not be reset" % vm.getName()
    else:
        task = vm.resetVM_Task()
        if task.waitForMe() == "success":
            print "%s is being reset" % vm.getName()
        else:
            print "%s could not be reset" % vm.getName()

def powerOnAllVms(vms):
    """
    Power on all virtual machines in a given sequence
    """
    for vm in vms:
        powerOnVm(vm)

def powerOffAllVms(vms):
    """
    Power off all virtual machines in a given sequence
    """
    for vm in vms:
        powerOffVm(vm)

def resetAllVms(vms):
    """
    Reset virtual machine power and return success
    """
    for vm in vms:
        resetVm(vm)

def getDatacenters(si):
    """
    Return a list of datacenter managed objects
    """
    dcList = InventoryNavigator(si.getRootFolder()).searchManagedEntities("Datacenter")
    return dcList

def getResourcePools(si):
    """
    Return a list of resource pool managed objects
    """
    rpList = InventoryNavigator(si.getRootFolder()).searchManagedEntities("ResourcePool")
    return rpList

def getAllVms(si):
    """
    Return a list of all virtual machines in the inventory
    """
    vmList = InventoryNavigator(si.getRootFolder()).searchManagedEntities("VirtualMachine")
    return vmList

def getVmByName(si,vmname):
    """
    Return virtual machine with a given name
    """
    vmList = []
    for vm in getAllVms(si):
        if vmname == vm.getName():
            vmList.append(vm)

    if len(vmList) > 1:
        print "Multiple virtual machines named %s.  Please lookup by UUID." % vmname
        return None
    else:
        return vmList[0]

def getVmByUUID(si,vmuuid):
    """
    Return virtual machine with a given uuid
    """
    for vm in getAllVms(si):
        if vmuuid == vm.getConfig().uuid:
            return vm
    return None

def getCommandLineOpts():
    """
    Parses command line options

    @returns: 3-tuple of (parser, options, args)
    """
    parser     = OptionParser(version="%prog 1.0", description='Manage VMWare ESX',
                              prog='manage-esx')
    infoGroup  = OptionGroup(parser=parser, title='Information',
                             description='Look up information on registered virtual machines')
    vmGroup    = OptionGroup(parser=parser, title='Manage Virtual Machines',
                             description='Create and delete virtual machines')
    powerGroup = OptionGroup(parser=parser, title='Manage Power Settings',
                             description='Control virtual machine power states')
    hostGroup  = OptionGroup(parser=parser, title='Manage Host Settings',
                             description='Control host configuration settings')

    parser.add_option('-s', '--server', dest='server', action='store',
                      help='VMware ESX server')
    parser.add_option('-u', '--username', dest='username', action='store',
                      help='VMware ESX user account name')
    parser.add_option('-p', '--password', dest='password', action='store',
                      help='VMware ESX user account password')
    parser.add_option('-S', '--skip-ssl', dest='skipSSL', action='store_false',
                      help='Skip SSL certificate checks')
    parser.set_defaults(skipSSL=True)
    
    parser.add_option_group(infoGroup)
    parser.add_option_group(vmGroup)
    parser.add_option_group(hostGroup)

    infoGroup.add_option('-q', '--query', dest='query', action='store_true',
                         help='Query VMware ESX server inventory information')
    infoGroup.add_option('-a', '--all', dest='all', action='store_true',
                         help='Select all')
    infoGroup.add_option('-n', '--name', dest='name', action='store',
                         help='Select by name')
    infoGroup.add_option('-U', '--uuid', dest='uuid', action='store',
                         help='Select by uuid')

    vmGroup.add_option('-D', '--delete', dest='delete', action='store_true',
                       help='Delete a virtual machine')
    vmGroup.add_option('-C', '--create', dest='create', action='store_true',
                       help='Create a virtual machine')

    vmGroup.add_option('--cpuCount', dest='cpuCount', action='store', type="int", help="Number of virtual CPU's (default: 2)")
    parser.set_defaults(cpuCount=2)
    vmGroup.add_option('--memorySizeMB', dest='memorySizeMB', action='store', type="int", help='Amount of RAM in MB (default: 2048)')
    parser.set_defaults(memorySizeMB=2048)
    vmGroup.add_option('--guestOsId', dest='guestOsId', action='store', help='Guest OS short name rhel5_64Guest, freebsd64Guest, solaris10_64Guest (default: rhel5_64Guest)')
    parser.set_defaults(guestOsId='rhel5_64Guest')
    vmGroup.add_option('--notes', dest='annotation', action='store', help='Virtual Machine annotations (default: blank)')
    parser.set_defaults(annotation='')
    vmGroup.add_option('--scsiBusKey', dest='scsiBusKey', action='store', type="int", help='Scsi Bus ID (default: 0)')
    parser.set_defaults(scsiBusKey=0)
    vmGroup.add_option('--diskSizeKB', dest='diskSizeKB', action='store', type="int", help='Amount of disk space in KB (default: 31457280)')
    parser.set_defaults(diskSizeKB=31457280)
    vmGroup.add_option('--diskMode', dest='diskMode', action='store', help='Disk mode (default: persistent)')
    parser.set_defaults(diskMode='persistent')
    vmGroup.add_option('--netName', dest='netName', action='store', help='Network name (default: VM Network)')
    parser.set_defaults(netName='VM Network')
    vmGroup.add_option('--nicName', dest='nicName', action='store', help='Network interface name (default: Network Adapter 1)')
    parser.set_defaults(nicName='Network Adapter 1')
    vmGroup.add_option('--datastoreName', dest='datastoreName', action='store', help='Datastore name (default: Storage1)')
    parser.set_defaults(datastoreName='Storage1')

    vmGroup.add_option('-P', '--power', dest='power', action='store', help='Toggle power. Possible settings are on, off, reset')

    options, args = parser.parse_args()
    
    return parser, options, args

def main():

    parser, options, args = getCommandLineOpts()

    # Check command line options
    if options.server is None:
        parser.error("You must provide a server")
    if options.username is None:
        parser.error("You must provide a username")
    if options.password is None:
        parser.error("You must provide a password")
    if options.name and options.uuid:
        parser.error("You must not lookup by name and uuid together")
    if options.name and options.all:
        parser.error("You must not lookup by name and all together")
    if options.uuid and options.all:
        parser.error("You must not lookup by uuid and all together")
    if options.query and options.power:
        parser.error("You must not do queries and power operations together")
    if options.query and options.create:
        parser.error("You must not do queries and create operations together")
    if options.power and options.create:
        parser.error("You must not do power and create operations together")
    
    # Get esx service instance
    si = getServiceInstance(options.server,options.username,options.password,
                            options.skipSSL)

    # List all the VMs
    if options.query and options.all:
        vms = getAllVms(si)
        if vms:
            listVms(vms)
    # List VM by name
    elif options.query and options.name:
        vm = getVmByName(si,options.name)
        if vm:
            listVm(vm)
    # List VM by uuid
    elif options.query and options.uuid:
        vm = getVmByUUID(si,options.uuid)
        if vm:
            listVm(vm)
    # Toggle virtual machine power
    elif options.name and options.power or options.uuid and options.power:
        if options.name:
            vm = getVmByName(si,options.name)
            if vm:
                if options.power.upper() == "RESET":
                    resetVm(vm)
                elif options.power.upper() == "OFF":
                    powerOffVm(vm)
                elif options.power.upper() == "ON":
                    powerOnVm(vm)
        elif options.uuid:
            vm = getVmByUUID(si,options.uuid)
            if vm:
                if options.power.upper() == "RESET":
                    resetVm(vm)
                elif options.power.upper() == "OFF":
                    powerOffVm(vm)
                elif options.power.upper() == "ON":
                    powerOnVm(vm)
    # Toggle power for all vms
    elif options.all and options.power:
        vms = getAllVms(si)
        if vms:
            if options.power.upper() == "RESET":
                resetAllVms(vms)
            elif options.power.upper() == "OFF":
                powerOffAllVms(vms)
            elif options.power.upper() == "ON":
                powerOnAllVms(vms)
    # Delete VMs
    elif options.name and options.delete or options.uuid and options.delete:
        if options.name:
            vm = getVmByName(si,options.name)
            if vm:
                deleteVm(vm)
        elif options.uuid:
            vm = getVmByUUID(si,options.uuid)
            if vm:
                deleteVm(vm)
    # Create VM
    elif options.create:
        resourcePool = getResourcePools(si)[0]
        datacenter = getDatacenters(si)[0]
        vmFolder = datacenter.getVmFolder()
        # Create virtual devices
        scsiSpec = createScsiSpec(options.scsiBusKey)
        diskSpec = createDiskSpec(options.datastoreName,options.scsiBusKey,options.diskSizeKB,options.diskMode)
        nicSpec = createNicSpec(options.netName,options.nicName)
        vmSpec = createVmSpec(options.name,options.cpuCount,options.memorySizeMB,options.guestOsId,options.annotation,scsiSpec,diskSpec,nicSpec,options.datastoreName)
        # Call the createVM_Task method on the vm folder
        task = vmFolder.createVM_Task(vmSpec, resourcePool, None)
        if task.waitForMe() == "success":
            print "%s is being created" % vm.getName()
        else:
            print "%s was not created" % vm.getName()

    si.getServerConnection().logout()

if __name__ == "__main__":
    main()
