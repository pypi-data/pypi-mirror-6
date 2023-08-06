from pysnmp.entity.rfc3413.oneliner import cmdgen

class SNMPError(Exception): pass


def get_variable(udp_host, udp_port, community, mib, variable, default=None):
    cmdGen = cmdgen.CommandGenerator()
    
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        cmdgen.CommunityData(community),
        cmdgen.UdpTransportTarget((udp_host, udp_port)),
        cmdgen.MibVariable(mib, variable, default),
        lookupNames=True, lookupValues=True
    )
    
    # Check for errors and print out results
    if errorIndication:
        raise SNMPError(errorIndication)
    if errorStatus:
        raise SNMPError(errorStatus)

    return [(name.prettyPrint(), val.prettyPrint()) for name, val in varBinds]
