#ifndef MAIN_STRUCTS_H
#define	MAIN_STRUCTS_H

#include <netinet/in.h>

#define SEC 1000000
#define UNUSED(expr) do { (void)(expr); } while (0)

#define PKT_UDP 1
#define PKT_TCP 2

#define FLOW_TYPE_UNDEF 0
#define FLOW_TYPE_TCP 1
#define FLOW_TYPE_UDP 2

#define FLOW_STATE_EMPTY 0x0
#define FLOW_STATE_ACTIVE 0x1
#define FLOW_STATE_PASSIVE_TIMED_OUT 0x2
#define FLOW_STATE_ITERATED_OVER 0x4


struct flow_id {
    struct in_addr src;
    u_short sport;
    struct in_addr dest;
    u_short dport;
    uint8_t flow_type; 
};

struct flow_info {       
    uint8_t flow_state;    
    uint32_t size_pkts;
    uint64_t size_bytes;
};

struct parser_info {
    float avg_pkts_per_sec;    
    uint32_t flows_collected;
    
    uint32_t tcp_flows;
    uint32_t udp_flows;
    
    uint32_t tcp_pkts;
    uint32_t udp_pkts;
    
    uint32_t ip_id_fields;
    uint32_t ip_id_stride;
    
    uint32_t ip_ttl_fields;
    uint32_t ip_ttl_stride;
    
    uint32_t ip_len_fields;
    uint32_t ip_len_stride;
    
    uint32_t tcp_seq_fields;
    uint32_t tcp_seq_stride;
    
    uint32_t tcp_ack_fields;
    uint32_t tcp_ack_stride;
    
    uint32_t tcp_win_fields;
    uint32_t tcp_win_stride;
    
    uint32_t tcp_flags_fields;
    uint32_t tcp_flags_stride;    
    
    uint64_t time_spent_collecting;
};

struct sniff_data {
    char source[255];
    char filter[255];
    int snaplen;
    int is_source_file;
    int datalink;
};

struct sniff_info {    
    uint32_t pkts_rx;
    uint32_t pkts_dropped;
    uint32_t pkts_ifdropped;
};

#endif	/* MAIN_STRUCTS_H */

