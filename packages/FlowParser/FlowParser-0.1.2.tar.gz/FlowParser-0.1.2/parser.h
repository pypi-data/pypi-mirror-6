#ifndef PARSER_H
#define	PARSER_H

#include <netinet/in.h>
#include <pthread.h>
#include <stdio.h>
#include <pcap.h>

#include "main_structs.h"
#include "khash/khash.h"
#include "khash/klist.h"
#include "khash/kvec.h"
#include "sniff.h"
#include "stride.h"
#include "packer.h"
#include "chunk_alloc.h"

#define do_nothing(x)

STRIDE_FIELD(id, u_short, 0) //ip id
STRIDE_FIELD(ttl, u_int8_t, 0) //ip ttl
STRIDE_FIELD(len, u_short, 0) //ip length
STRIDE_FIELD(flags, u_int8_t, 0) //tcp flags
STRIDE_FIELD(seq, tcp_seq_t, 0) //tcp seq
STRIDE_FIELD(ack, tcp_seq_t, 0) //tcp ack
STRIDE_FIELD(win, u_short, 0) //tcp win

#define FSHIFT 11 // fixed-point precision
#define FIXED_1 (1 << FSHIFT) // 1 in fixed point
#define FIXED_ALPHA (0.35 * FIXED_1) // 0.35 in fixed point
#define FIXED_1_ALPHA (0.65 * FIXED_1) // 1 - 0.35 in fixed point

// different ways flow ids can be sorted
#define SORTED_NONE 0
#define SORTED_PKTS 1
#define SORTED_BYTES 2
#define SORTED_PPS 3
#define SORTED_BPS 4

struct flow {
    struct uint_seq timestamps;
    uint64_t last_rx_time;
    uint64_t first_rx_time;
    uint64_t expiry_time;
    pthread_mutex_t mutex;
    struct flow_info info;

    uint32_t pkts_this_period;
    uint32_t pkts_last_period;
    uint64_t avg_pkts_per_period;

    uint32_t bytes_this_period;
    uint32_t bytes_last_period;
    uint64_t avg_bytes_per_period;

    stride_field(id) id;
    stride_field(len) len;
    stride_field(ttl) ttl;
};

struct udp_flow {
    struct flow flow;
};

struct tcp_flow {
    struct flow flow;

    stride_field(flags) flags;
    stride_field(seq) seq;
    stride_field(ack) ack;
    stride_field(win) win;
};

struct flow_tuple {
    struct flow_id *flow_id;
    struct flow *flow;
};

#define TUPLE_LT_PPS(a, b) ((a).flow->avg_pkts_per_period <\
        (b).flow->avg_pkts_per_period)
#define TUPLE_LT_BPS(a, b) ((a).flow->avg_bytes_per_period <\
         (b).flow->avg_bytes_per_period)
#define TUPLE_LT_PKTS(a, b) ((a).flow->info.size_pkts < (b).flow->info.size_pkts)
#define TUPLE_LT_BYTES(a, b) ((a).flow->info.size_bytes < (b).flow->info.size_bytes)

struct tcp_chunk {
    struct flow_id id;
    struct tcp_flow flow;
};

struct udp_chunk {
    struct flow_id id;
    struct udp_flow flow;
};

CHUNK_ALLOC(tcp_chunks, struct tcp_chunk, 10000)
CHUNK_ALLOC(udp_chunks, struct udp_chunk, 10000)

KLIST_INIT(32, struct flow_tuple *, do_nothing)

khint_t flow_id_hash(const struct flow_id *id);
int flow_id_equal(const struct flow_id *f1, const struct flow_id *f2);

KHASH_INIT(32, struct flow_id *, struct flow *, 1, flow_id_hash, flow_id_equal)

enum thread_status {
    NOT_STARTED,
    RUNNING,
    BEING_KILLED,
    KILLED
};

struct parser_base {
    khash_t(32) *flows_table;
    int debug_level;
    uint64_t flow_timeout;
    uint64_t tcp_afterfin_timeout;

    pthread_rwlock_t flows_table_lock;
    pthread_mutex_t thread_status_mutex;

    pthread_t collector;
    pthread_t dumper;
    pthread_t sniffer;

    enum thread_status collector_status;
    enum thread_status dumper_status;
    enum thread_status sniffer_status;
    int to_kill;

    uint32_t tcp_flows_inmem;
    uint32_t udp_flows_inmem;
    uint32_t flow_ids_inmem;

    uint64_t last_rx_time;
    uint32_t pkts_this_second;
    uint32_t pkts_last_second;
    uint64_t avg_pkts_per_second; // in fixed-point

    kvec_t(struct flow_id *) collector_list;
    uint64_t time_spent_collecting;
    uint32_t flows_collected;

    klist_t(32) *dump_queue;
    pthread_mutex_t dump_queue_mutex;
    pthread_cond_t dump_queue_has_items;
    int dumper_to_kill; /* cannot use the global one - need to make sure the 
                        * dumper thread only dies after the last collection has 
                        * been fully completed */

    struct sniff_data sniffer_data;
    pcap_t *sniffer_handle;

    void *user;
    void (*after_kill_callback)(struct parser_base *p);

    chunk_base(tcp_chunks) tcp_chunks;
    chunk_base(udp_chunks) udp_chunks;
};

int handle_tcp_pkt_longarg(struct parser_base *parser,
        struct tcp_flow *flow, u_short ip_total_len,
        u_short ip_id, u_char ip_ttl, u_int tcp_seq, u_int tcp_ack,
        u_char tcp_flags, u_short tcp_win, uint64_t timestamp);
int handle_tcp_pkt(struct parser_base *parser,
        struct tcp_flow *flow, const struct sniff_ip *ip_hdr,
        const struct sniff_tcp *tcp_hdr, uint64_t timestamp);
int handle_udp_pkt_longarg(struct parser_base *parser,
        struct udp_flow *flow, u_short ip_total_len,
        u_short ip_id, u_char ip_ttl, uint64_t timestamp);
int handle_udp_pkt(struct parser_base *parser,
        struct udp_flow *flow, const struct sniff_ip *ip_hdr,
        uint64_t timestamp);

void find_flow_and_id(const struct parser_base *p, const struct flow_id *id,
        struct flow_tuple *tuple);
struct flow *lookup_flow(struct parser_base *p, const struct flow_id *id);
void free_tcp_chunk(struct parser_base *p, struct flow_id *id,
        struct tcp_flow *flow);
void free_udp_chunk(struct parser_base *p, struct flow_id *id,
        struct udp_flow *flow);
void kill_parser(struct parser_base *parser, int dealloc_parser);
void populate_parser_info(struct parser_base *parser, struct parser_info *info);
void sort_tuples(size_t n, struct flow_tuple *a, uint8_t sort_by);

void init_parser(struct parser_base *parser);
void close_parser(struct parser_base *parser);
void clear_flows(struct parser_base *parser);

int init_dumper(struct parser_base *parser);
int close_dumper(struct parser_base *parser);
void enqueue_flow_for_dumping(struct parser_base *parser,
        struct flow_id *id, struct flow *flow);
size_t get_dump_queue_size(struct parser_base *parser);

int init_collector(struct parser_base *parser);
int close_collector(struct parser_base *parser);

int init_sniff(struct parser_base *parser, struct sniff_data *init_data);
int close_sniff(struct parser_base *parser);
void populate_sniff_info(struct parser_base *parser, struct sniff_info *info);

void offload_tcp_flow(struct parser_base *parser, struct flow_id *id,
        struct tcp_flow *flow);
void offload_udp_flow(struct parser_base *parser, struct flow_id *id,
        struct udp_flow *flow);

int main_table_rlock_get(struct parser_base *parser);
int main_table_rlock_release(struct parser_base *parser);
int main_table_wlock_get(struct parser_base *parser);
int main_table_wlock_release(struct parser_base *parser);

#endif	/* PARSER_H */
