#ifndef FPARSER_DOCSTRING_H
#define	FPARSER_DOCSTRING_H

#ifdef	__cplusplus
extern "C" {
#endif


#define FP_FLOW_ID_SRC "The source IP address of the flow"
#define FP_FLOW_ID_DEST "The destination IP address of the flow"
#define FP_FLOW_ID_SPORT "The source port of the transport header of the flow"
#define FP_FLOW_ID_DPORT "The dest port of the transport header of the flow"
#define FP_FLOW_ID_TYPE "One of FLOW_TYPE_TCP or FLOW_TYPE_UDP"

#define FP_METHOD_STOP "Terminates the parser."\
    " After this method is called the parser objcet cannot be used anymore."\
    " Offline parsers terminate automatically when the source has been depleted"
#define FP_METHOD_SET_TCP_CB "Registers/changes the TCP flow offload callback."\
    " The provided callable will be called when a TCP flow terminates."\
    "\n\n:param callable callback: a callable that takes a single argument - the TCP flow"
#define FP_METHOD_SET_UDP_CB "Registers/changes the UDP flow offload callback."\
    " The provided callable will be called when a UDP flow terminates."\
    "\n\n:param callable callback: a callable that takes a single argument - the UDP flow"
#define FP_METHOD_FIND_TCP "Finds an active TCP flow"\
    "\n\n:param str src_ip: the source IP address"\
    "\n:param int sport: the source port"
    
#define FP_DOCSTRING "FlowParser - easy and quick IP netowrk flow sniffing and reconstruction for Python"


#ifdef	__cplusplus
}
#endif

#endif

