#!/usr/bin/env python

kube_description= \
"""
Emulator demo
"""
kube_instruction= \
"""
Not instructions yet
"""

#
# Standard geni-lib/portal libraries
#
import geni.portal as portal
import geni.rspec.pg as PG
import geni.rspec.emulab as elab
import geni.rspec.igext as IG
import geni.urn as URN



#
# PhantomNet extensions.
#
import geni.rspec.emulab.pnext as PN

#
# Globals
#
class GLOBALS(object):
    OAI_DS = "urn:publicid:IDN+emulab.net:phantomnet+ltdataset+oai-develop"
    OAI_SIM_DS = "urn:publicid:IDN+emulab.net:phantomnet+dataset+PhantomNet:oai"
    UE_IMG  = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:ANDROID444-STD")
    ADB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU14-64-PNTOOLS")
    OAI_EPC_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU16-64-OAIEPC")
    OAI_ENB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:OAI-Real-Hardware.enb1")
    OAI_SIM_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU14-64-OAI")
    OAI_SRS_EPC = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:srsEPC-OAICN")
    OAI_CONF_SCRIPT = "/usr/bin/sudo /local/repository/bin/config_oai.pl"
    MSIMG = "urn:publicid:IDN+emulab.net+image+PhantomNet:mobilestream-v1"

def connectOAI_DS(node):
    # Create remote read-write clone dataset object bound to OAI dataset
    bs = rspec.RemoteBlockstore("ds-%s" % node.name, "/opt/oai")
    bs.dataset = GLOBALS.OAI_DS
    bs.Site('EPC')
    bs.rwclone = True
    # Create link from node to OAI dataset rw clone
    node_if = node.addInterface("dsif_%s" % node.name)
    bslink = rspec.Link("dslink_%s" % node.name)
    bslink.addInterface(node_if)
    bslink.addInterface(bs.interface)
    bslink.vlan_tagging = True
    bslink.best_effort = True  

#
# This geni-lib script is designed to run in the PhantomNet Portal.
#
pc = portal.Context()

#
# Profile parameters.
#

pc.defineParameter("computeNodeCount", "Number of slave/compute nodes",
                   portal.ParameterType.INTEGER, 1)
pc.defineParameter("EPC", "EPC implementation",
                   portal.ParameterType.STRING,"OAI",[("OAI","Open Air Inrterface"),("srsLTE","srsLTE"), ("MobileStream", "MobileStream"), ("NextEPC", "NextEPC"), ("free5GC", "free5GC"), ("Open5GS", "Open5GS")])
pc.defineParameter("Hardware", "EPC hardware",
                   portal.ParameterType.STRING,"d430",[("d430","d430"),("d710","d710"), ("d820", "d820"), ("pc3000", "pc3000")])
pc.defineParameter("multi", "Multiplexer (True or False)",
                   portal.ParameterType.BOOLEAN, True)
pc.defineParameter("cores", "Number of cores",
                   portal.ParameterType.STRING,"4",[("4","4"),("8","8"), ("12", "12"), ("16", "16"), ("20", "20")],
                   longDescription="Number of cores of each Nervion node.",
                   advanced=True)
pc.defineParameter("ram", "RAM size",
                   portal.ParameterType.STRING,"4",[("4","4"),("8","8"), ("12", "12"), ("16", "16"), ("20", "20"), ("24", "24"), ("32", "32")],
                   longDescription="RAM size (GB)",
                   advanced=True)


params = pc.bindParameters()

#
# Give the library a chance to return nice JSON-formatted exception(s) and/or
# warnings; this might sys.exit().
#
pc.verifyParameters()

rspec = PG.Request()
epc = rspec.RawPC("epc")
epc.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
epc.addService(PG.Execute(shell="sh", command="/usr/bin/sudo /local/repository/scripts/open5gs.sh"))
epc.hardware_type = params.Hardware
epc.Site('EPC')
    

tour = IG.Tour()
tour.Description(IG.Tour.TEXT,kube_description)
tour.Instructions(IG.Tour.MARKDOWN,kube_instruction)
rspec.addTour(tour)


netmask="255.255.255.0"

epclink = rspec.Link("s1-lan")
iface = epc.addInterface()
iface.addAddress(PG.IPv4Address("192.168.4.80", netmask))
epclink.addInterface(iface)

#slave_ifaces = []
for i in range(0,params.computeNodeCount):
    kube_s = rspec.XenVM('ran'+str(i))
    kube_s.cores = 12
    kube_s.ram = 1024 * 8
    kube_s.routable_control_ip = True
    kube_s.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
    kube_s.Site('RAN')
    iface = kube_s.addInterface()
    iface.addAddress(PG.IPv4Address("192.168.4." + str(i+81), netmask))
    epclink.addInterface(iface)
    kube_s.addService(PG.Execute(shell="bash", command="/local/repository/scripts/ueransim.sh " + "imsi-20893" + "{:010d}".format((i*20) + 1) + " " + "192.168.4." + str(i+81)))



epclink.link_multiplexing = True
epclink.vlan_tagging = True
epclink.best_effort = True



#
# Print and go!
#
pc.printRequestRSpec(rspec)
