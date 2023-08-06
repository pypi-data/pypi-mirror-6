#include <string.h>
#include <stdio.h>
#include <arpa/inet.h>
#include <inttypes.h>
#include <syslog.h>
#include "khash/ksort.h"

#include "parser.h"
#include "logging.h"
#include "sniff.h"

KSORT_INIT(by_pps, struct flow_tuple, TUPLE_LT_PPS)
KSORT_INIT(by_bps, struct flow_tuple, TUPLE_LT_BPS)
KSORT_INIT(by_pkts, struct flow_tuple, TUPLE_LT_PKTS)
KSORT_INIT(by_bytes, struct flow_tuple, TUPLE_LT_BYTES)

void init_parser(struct parser_base *p) {
    memset(p, 0, sizeof (struct parser_base));

    p->flows_table = kh_init(32);
    chunk_base_init(tcp_chunks, &p->tcp_chunks);
    chunk_base_init(udp_chunks, &p->udp_chunks);

    pthread_rwlock_init(&p->flows_table_lock, NULL);
    pthread_mutex_init(&p->thread_status_mutex, NULL);

    p->debug_level = LOG_ERR;
    p->flow_timeout = 15 * 60 * (uint64_t) SEC;
    p->tcp_afterfin_timeout = 30 * (uint64_t) SEC;
    
    p->collector_status = NOT_STARTED;
    p->dumper_status = NOT_STARTED;
    p->sniffer_status = NOT_STARTED;
}

void close_parser(struct parser_base *p) {
    if (p->flows_table) {
        int flows_remaining = p->flows_table->size;

        if (flows_remaining > 0) {
            WARN(p, "Closing parser with non-empty flow table %d", flows_remaining);
        }

        clear_flows(p);
        kh_destroy(32, p->flows_table);
        
        chunk_base_close(tcp_chunks, &p->tcp_chunks);
        chunk_base_close(udp_chunks, &p->udp_chunks);
        
        p->flows_table = NULL;
    } else {
        INFO(p, "Flow table already closed");
    }
}

void kill_parser(struct parser_base *p, int dealloc_parser) {
    p->to_kill = 1;
    
    close_sniff(p);
    close_collector(p);
    close_dumper(p);
    
    if (dealloc_parser) {
        close_parser(p);
    }
    
    if (p->after_kill_callback) {
        p->after_kill_callback(p);
        p->after_kill_callback = NULL;
    }
}

khint_t flow_id_hash(const struct flow_id *id) {
    uint32_t s = id->src.s_addr;
    uint32_t d = id->dest.s_addr;

    khint_t result = 17;
    result = 37 * result + s;
    result = 37 * result + d;
    result = 37 * result + (khint_t) id->sport;
    result = 37 * result + (khint_t) id->dport;
    result = 37 * result + (khint_t) id->flow_type;

    return result;
}

int flow_id_equal(const struct flow_id *f1, const struct flow_id *f2) {
    return f1->sport == f2->sport && f1->dport == f2->dport &&
            ntohl(f1->src.s_addr) == ntohl(f2->src.s_addr) &&
            ntohl(f1->dest.s_addr) == ntohl(f2->dest.s_addr) &&
            f1->flow_type == f2->flow_type;
}

void free_tcp_chunk(struct parser_base *p, struct flow_id *id,
        struct tcp_flow *flow) {
    close_stride_field(id, &flow->flow.id);
    close_stride_field(len, &flow->flow.len);
    close_stride_field(ttl, &flow->flow.ttl);

    close_stride_field(ack, &flow->ack);
    close_stride_field(flags, &flow->flags);
    close_stride_field(win, &flow->win);
    close_stride_field(seq, &flow->seq);

    packer_destroy(&flow->flow.timestamps);

    chunk_dealloc(tcp_chunks, &p->tcp_chunks, (struct tcp_chunk *) id);

    p->tcp_flows_inmem--;
    p->flow_ids_inmem--;
}

void free_udp_chunk(struct parser_base *p, struct flow_id *id,
        struct udp_flow *flow) {
    close_stride_field(id, &flow->flow.id);
    close_stride_field(len, &flow->flow.len);
    close_stride_field(ttl, &flow->flow.ttl);

    packer_destroy(&flow->flow.timestamps);

    chunk_dealloc(udp_chunks, &p->udp_chunks, (struct udp_chunk *) id);

    p->udp_flows_inmem--;
    p->flow_ids_inmem--;
}

static struct tcp_chunk *new_tcp_chunk(struct parser_base *p,
        const struct flow_id *original_id) {
    struct tcp_chunk *chunk;
    chunk = chunk_alloc(tcp_chunks, &p->tcp_chunks);
    memset(chunk, 0, sizeof (struct tcp_chunk));
    chunk->flow.flow.expiry_time = UINT64_MAX;

    chunk->flow.flow.info.flow_state = FLOW_STATE_EMPTY;
    pthread_mutex_init(&chunk->flow.flow.mutex, NULL);

    init_stride_field(id, &chunk->flow.flow.id);
    init_stride_field(len, &chunk->flow.flow.len);
    init_stride_field(ttl, &chunk->flow.flow.ttl);

    init_stride_field(ack, &chunk->flow.ack);
    init_stride_field(flags, &chunk->flow.flags);
    init_stride_field(win, &chunk->flow.win);
    init_stride_field(seq, &chunk->flow.seq);

    packer_init(&chunk->flow.flow.timestamps);
    memcpy(&chunk->id, original_id, sizeof (struct flow_id));

    p->tcp_flows_inmem++;
    p->flow_ids_inmem++;

    return chunk;
}

static struct udp_chunk *new_udp_chunk(struct parser_base *p,
        const struct flow_id *original_id) {
    struct udp_chunk *chunk;
    chunk = chunk_alloc(udp_chunks, &p->udp_chunks);
    memset(chunk, 0, sizeof (struct udp_chunk));
    chunk->flow.flow.expiry_time = UINT64_MAX;

    chunk->flow.flow.info.flow_state = FLOW_STATE_EMPTY;
    pthread_mutex_init(&chunk->flow.flow.mutex, NULL);

    init_stride_field(id, &chunk->flow.flow.id);
    init_stride_field(len, &chunk->flow.flow.len);
    init_stride_field(ttl, &chunk->flow.flow.ttl);

    packer_init(&chunk->flow.flow.timestamps);
    memcpy(&chunk->id, original_id, sizeof (struct flow_id));

    p->udp_flows_inmem++;
    p->flow_ids_inmem++;

    return chunk;
}

void clear_flows(struct parser_base *p) {
    khiter_t i;
    struct flow *flow;
    struct flow_id *id;

    for (i = kh_begin(p->flows_table);
            i != kh_end(p->flows_table); i++) {
        if (kh_exist(p->flows_table, i)) {
            flow = kh_value(p->flows_table, i);
            id = kh_key(p->flows_table, i);

            if (id->flow_type == FLOW_TYPE_TCP) {
                free_tcp_chunk(p, id, (struct tcp_flow *) flow);
            } else if (id->flow_type == FLOW_TYPE_UDP) {
                free_udp_chunk(p, id, (struct udp_flow *) flow);
            } else {
                ERROR(p, "Bad flow id on free - corrupted memory");
            }

            kh_del(32, p->flows_table, i);
        }
    }
}

void find_flow_and_id(const struct parser_base *p, const struct flow_id *id,
        struct flow_tuple *tuple) {
    int is_missing;    
    khiter_t k;

    k = kh_get(32, p->flows_table, id);
    is_missing = (k == kh_end(p->flows_table));
    
    if (is_missing) {
        tuple->flow = NULL;
        tuple->flow_id = NULL;
    } else {
        tuple->flow = kh_value(p->flows_table, k);
        tuple->flow_id = kh_key(p->flows_table, k);
    }
}

/**
 * Given a table finds a flow. If the flow is not there it IS NOT created. 
 * The flow id that this function is called with should be temporary 
 * (i.e. allocated, populated by the caller and freed by the caller after return)
 * 
 * @param table a table that maps struct flow_id* to struct flow*
 * @param id the flow id
 * @return the flow on success, NULL on failure
 */
static struct flow *find_flow(const kh_32_t *table, const struct flow_id *id) {
    khiter_t k;
    int is_missing;
    struct flow *flow = NULL;

    if (kh_size(table) == 0) {
        return flow;
    }

    k = kh_get(32, table, id);
    is_missing = (k == kh_end(table));

    if (!is_missing) {
        flow = kh_value(table, k);
    }

    return flow;
}

/**
 * Given a table finds (or creates) a flow. If the flow is not there it 
 * IS created. Note that this function may modify the table and a write lock on 
 * it must be acquired before calling the function. Unlike the find function 
 * this one needs to be given a reference to the parser context, because 
 * it may allocate new flow/flow id. The flow id that this function is called 
 * with should be temporary (i.e. allocated, populated by the caller and freed 
 * by the caller after return)
 * 
 * @param p the parser context
 * @param table a table that maps struct flow_id* to struct flow*
 * @param id the flow id
 * @return the flow on success, NULL on failure
 */
static struct flow *get_flow(struct parser_base *p, kh_32_t *table,
        const struct flow_id *id) {
    khiter_t k;
    int is_missing, ret;
    struct flow_id *flow_id;
    struct flow *flow = NULL;
    struct tcp_chunk *tcp_chunk = NULL;
    struct udp_chunk *udp_chunk = NULL;

    k = kh_get(32, table, id);
    is_missing = (k == kh_end(table));

    if (is_missing) {
        if (id->flow_type == FLOW_TYPE_TCP) {
            tcp_chunk = new_tcp_chunk(p, id);
            flow_id = &tcp_chunk->id;
            flow = (struct flow *) &tcp_chunk->flow;
        } else if (id->flow_type == FLOW_TYPE_UDP) {
            udp_chunk = new_udp_chunk(p, id);
            flow_id = &udp_chunk->id;
            flow = (struct flow *) &udp_chunk->flow;
        } else {
            ERROR(p, "Bad flow id in get_flow");
            return NULL;
        }

        k = kh_put(32, table, flow_id, &ret);
        if (ret == -1) {
            ERROR(p, "Unable to add new flow");
            if (id->flow_type == FLOW_TYPE_TCP) {
                free_tcp_chunk(p, &tcp_chunk->id, &tcp_chunk->flow);
            } else {
                free_udp_chunk(p, &udp_chunk->id, &udp_chunk->flow);
            }
            return NULL;
        }

        kh_value(table, k) = flow;
    } else {
        flow = kh_value(table, k);
    }

    return flow;
}

/**
 * Returns a new flow if needed, or an old flow if one exists. This function 
 * will first try to get the flow from the primary table. If it is there it is 
 * returned. If it is not there and the table is not used a new flow is added 
 * to it. If the table is locked a new flow is created in the shadow table. 
 * This function handles all the necessary locking. 
 * 
 * @param p the parser context
 * @param id the flow id
 * @return a new flow or an existing flow
 */
struct flow *lookup_flow(struct parser_base *p,
        const struct flow_id *id) {
    struct flow *flow = NULL;
    int ret;
    
    /* Initially we will only get a read lock as it is more likely 
     * that we won't need to construct a new flow (there are a lot more 
     * packets than flows) */
    if ((ret = pthread_rwlock_rdlock(&p->flows_table_lock)) != 0) {
        ERROR(p, "Unable to acquire read lock on flow table %s", strerror(ret));
        return NULL;
    }
    DEBUG(p, "Acquired read lock on flows table");

    flow = find_flow(p->flows_table, id);
    if (flow == NULL) {
        /* The flow is not in the primary table. We will need to get a write lock. */

        if (pthread_rwlock_unlock(&p->flows_table_lock) != 0) {
            ERROR(p, "Unable to release read lock on flows table");
            return NULL;
        }
        DEBUG(p, "Released read lock on flows table");

        ret = pthread_rwlock_wrlock(&p->flows_table_lock);
        if (ret == 0) {
            DEBUG(p, "Acquired write lock on flows table");
            
            /* We managed to get a write lock on the primary table. Now we 
             * call get_flow to create/get a new flow. Note that it is 
             * possible that the table has changed and the flow has already 
             * been added since we released the read lock and got the write 
             * one. In this case get_flow will return the old one. */

            if ((flow = get_flow(p, p->flows_table, id)) == NULL) {
                ERROR(p, "Something massively bad happened");
            }

            if (pthread_rwlock_unlock(&p->flows_table_lock) != 0) {
                ERROR(p, "Unable to release write lock on flows table");
                return NULL;
            }
            DEBUG(p, "Released write lock on flows table");
        } else {
            ERROR(p, "Unable to lock the flows table");
            return NULL;
        }
    } else {
        /* The flow is in the primary table. */

        if (pthread_rwlock_unlock(&p->flows_table_lock) != 0) {
            ERROR(p, "Unable to release read lock on flows table");
            return NULL;
        }
        DEBUG(p, "Released read lock on flows table");
    }
    
    return flow;
}

void populate_parser_info(struct parser_base *p,
        struct parser_info *info) {
    khiter_t i;
    struct flow *flow;
    struct tcp_flow *tcp_flow;
    struct flow_id *id;

    size_t ip_id_stride = 0, ip_id_fields = 0;
    size_t ip_len_stride = 0, ip_len_fields = 0;
    size_t ip_ttl_stride = 0, ip_ttl_fields = 0;
    size_t tcp_seq_stride = 0, tcp_seq_fields = 0;
    size_t tcp_ack_stride = 0, tcp_ack_fields = 0;
    size_t tcp_win_stride = 0, tcp_win_fields = 0;
    size_t tcp_flags_stride = 0, tcp_flags_fields = 0;

    info->avg_pkts_per_sec = (float) ((double) p->avg_pkts_per_second /
            (double) FIXED_1);
    info->time_spent_collecting = p->time_spent_collecting;
    info->flows_collected = p->flows_collected;

    info->tcp_flows = p->tcp_flows_inmem;
    info->udp_flows = p->udp_flows_inmem;

    info->tcp_pkts = 0;
    info->udp_pkts = 0;

    for (i = kh_begin(p->flows_table);
            i != kh_end(p->flows_table); i++) {
        if (kh_exist(p->flows_table, i)) {
            flow = kh_value(p->flows_table, i);
            id = kh_key(p->flows_table, i);

            get_size(id, &flow->id, &ip_id_fields, &ip_id_stride);
            get_size(ttl, &flow->ttl, &ip_ttl_fields, &ip_ttl_stride);
            get_size(len, &flow->len, &ip_len_fields, &ip_len_stride);

            if (id->flow_type == FLOW_TYPE_TCP) {
                tcp_flow = (struct tcp_flow *) flow;

                get_size(seq, &tcp_flow->seq, &tcp_seq_fields, &tcp_seq_stride);
                get_size(ack, &tcp_flow->ack, &tcp_ack_fields, &tcp_ack_stride);
                get_size(flags, &tcp_flow->flags, &tcp_flags_fields,
                        &tcp_flags_stride);
                get_size(win, &tcp_flow->win, &tcp_win_fields, &tcp_win_stride);

                info->tcp_pkts += flow->info.size_pkts;
            } else if (id->flow_type == FLOW_TYPE_UDP) {
                info->udp_pkts += flow->info.size_pkts;
            } else {
                ERROR(p, "Bad flow id. Memory corrupted.");
            }
        }
    }

    info->ip_id_fields = ip_id_fields;
    info->ip_id_stride = ip_id_stride;
    info->ip_ttl_fields = ip_ttl_fields;
    info->ip_ttl_stride = ip_ttl_stride;
    info->ip_len_fields = ip_len_fields;
    info->ip_len_stride = ip_len_stride;
    info->tcp_seq_fields = tcp_seq_fields;
    info->tcp_seq_stride = tcp_seq_stride;
    info->tcp_ack_fields = tcp_ack_fields;
    info->tcp_ack_stride = tcp_ack_stride;
    info->tcp_win_fields = tcp_win_fields;
    info->tcp_win_stride = tcp_win_stride;
    info->tcp_flags_fields = tcp_flags_fields;
    info->tcp_flags_stride = tcp_flags_stride;
}

int handle_tcp_pkt_longarg(struct parser_base *p,
        struct tcp_flow *flow, u_short ip_total_len,
        u_short ip_id, u_char ip_ttl, u_int tcp_seq, u_int tcp_ack,
        u_char tcp_flags, u_short tcp_win, uint64_t timestamp) {
    struct sniff_ip ip_hdr;
    struct sniff_tcp tcp_hdr;

    ip_hdr.ip_len = ip_total_len;
    ip_hdr.ip_id = ip_id;
    ip_hdr.ip_ttl = ip_ttl;
    tcp_hdr.th_seq = tcp_seq;
    tcp_hdr.th_win = tcp_win;
    tcp_hdr.th_flags = tcp_flags;
    tcp_hdr.th_ack = tcp_ack;

    return handle_tcp_pkt(p, flow, &ip_hdr, &tcp_hdr, timestamp);
}

static inline int unlock_flow_mutex(struct parser_base *p, struct flow *flow) {
    if (pthread_mutex_unlock(&flow->mutex) != 0) {
        ERROR(p, "Unable to unlock flow mutex.");
        return -1;
    }

    return 0;
}

/**
 * Adds a new TCP packet to the parser. This function accepts libpcap-style 
 * structs and handles locking/unlocking the flow. 
 * 
 * @param p the parser context
 * @param flow the flow that the packet is to be added to
 * @param ip_hdr pcap-style IP header
 * @param tcp_hdr pcap-style TCP header
 * @param timestamp timestamp of when the packet was received
 * @return 0 on success, -1 on failure
 */
int handle_tcp_pkt(struct parser_base *p,
        struct tcp_flow *tcp_flow, const struct sniff_ip *ip_hdr,
        const struct sniff_tcp *tcp_hdr, uint64_t timestamp) {
    struct flow *flow = &tcp_flow->flow;
    struct flow_info *info = &flow->info;
    uint64_t offset;

    if (pthread_mutex_lock(&flow->mutex) != 0) {
        ERROR(p, "Unable to lock flow mutex.");
        return -1;
    }

    if (info->flow_state & FLOW_STATE_PASSIVE_TIMED_OUT) {
        ERROR(p, "Got packet for flow that is being flushed. Packet lost.");
        unlock_flow_mutex(p, flow);
        return -1;
    }

    if (info->size_pkts == 0) {
        info->flow_state |= FLOW_STATE_ACTIVE;
        flow->first_rx_time = timestamp;
        flow->last_rx_time = timestamp;
    }

    if (timestamp < flow->last_rx_time) {
        ERROR(p, "Bad timestamp new: %" PRIu64 " old: %" PRIu64, timestamp,
                flow->last_rx_time);
        unlock_flow_mutex(p, flow);
        return -1;
    }

    offset = timestamp - flow->last_rx_time;
    if (offset > UINT32_MAX) {
        ERROR(p, "Stale flow - got packet with offset %" PRIu64, offset);
        unlock_flow_mutex(p, flow);
        return -1;
    }

    // some bookkeeping
    p->pkts_this_second++;
    p->last_rx_time = timestamp;
    flow->last_rx_time = timestamp;
    flow->expiry_time = timestamp + p->flow_timeout;
    flow->pkts_this_period++;
    flow->bytes_this_period += ntohs(ip_hdr->ip_len);

    // first add the timestamp offset
    if (packer_append(&flow->timestamps, (uint32_t) offset) < 0) {
        ERROR(p, "Offset too large to pack %" PRIu64, offset);
        unlock_flow_mutex(p, flow);
        return -1;
    }

    // set fin_seen if the TCP flag is set
    if (tcp_hdr->th_flags & TH_FIN) {
        flow->expiry_time = timestamp + p->tcp_afterfin_timeout;
    }

    add_val(id, &flow->id, ntohs(ip_hdr->ip_id));
    add_val(ttl, &flow->ttl, ip_hdr->ip_ttl);
    add_val(len, &flow->len, ntohs(ip_hdr->ip_len));

    add_val(ack, &tcp_flow->ack, ntohl(tcp_hdr->th_ack));
    add_val(seq, &tcp_flow->seq, ntohl(tcp_hdr->th_seq));
    add_val(win, &tcp_flow->win, ntohs(tcp_hdr->th_win));
    add_val(flags, &tcp_flow->flags, tcp_hdr->th_flags);

    info->size_pkts++;
    info->size_bytes += ntohs(ip_hdr->ip_len);
    return unlock_flow_mutex(p, flow);
}

int handle_udp_pkt_longarg(struct parser_base *parser,
        struct udp_flow *flow, u_short ip_total_len,
        u_short ip_id, u_char ip_ttl, uint64_t timestamp) {
    struct sniff_ip ip_hdr;

    ip_hdr.ip_len = ip_total_len;
    ip_hdr.ip_id = ip_id;
    ip_hdr.ip_ttl = ip_ttl;

    return handle_udp_pkt(parser, flow, &ip_hdr, timestamp);
}

/**
 * Adds a new UDP packet to the parser. This function accepts libpcap-style 
 * structs and handles locking/unlocking the flow. Note that it does not need a 
 * UDP header since sport/dport are part of the flow id and the udp header does 
 * not contain anything else interesting.
 * 
 * @param p the parser context
 * @param flow the flow that the packet is to be added to
 * @param ip_hdr pcap-style IP header
 * @param timestamp timestamp of when the packet was received
 * @return 0 on success, -1 on failure
 */
int handle_udp_pkt(struct parser_base *p,
        struct udp_flow *udp_flow, const struct sniff_ip *ip_hdr,
        uint64_t timestamp) {
    struct flow *flow = &udp_flow->flow;
    struct flow_info *info = &flow->info;
    uint64_t offset;

    if (pthread_mutex_lock(&flow->mutex) != 0) {
        ERROR(p, "Unable to lock flow mutex.");
        return -1;
    }

    if (info->flow_state & FLOW_STATE_PASSIVE_TIMED_OUT) {
        ERROR(p, "Got packet for flow that is being flushed. Packet lost.");
        unlock_flow_mutex(p, flow);
        return -1;
    }

    if (info->size_pkts == 0) {
        info->flow_state |= FLOW_STATE_ACTIVE;
        flow->first_rx_time = timestamp;
        flow->last_rx_time = timestamp;
    }

    if (timestamp < flow->last_rx_time) {
        ERROR(p, "Bad timestamp");
        unlock_flow_mutex(p, flow);
        return -1;
    }

    offset = timestamp - flow->last_rx_time;
    if (offset > UINT32_MAX) {
        ERROR(p, "Stale flow - got packet with offset %" PRIu64, offset);
        info->flow_state |= FLOW_STATE_PASSIVE_TIMED_OUT;

        unlock_flow_mutex(p, flow);
        return -1;
    }

    // some bookkeeping
    p->pkts_this_second++;
    p->last_rx_time = timestamp;
    flow->last_rx_time = timestamp;
    flow->expiry_time = timestamp + p->flow_timeout;
    flow->pkts_this_period++;
    flow->bytes_this_period += ntohs(ip_hdr->ip_len);

    if (packer_append(&flow->timestamps, (uint32_t) offset) < 0) {
        ERROR(p, "Offset too large to pack %" PRIu64, offset);
        unlock_flow_mutex(p, flow);
        return -1;
    }

    add_val(id, &flow->id, ntohs(ip_hdr->ip_id));
    add_val(ttl, &flow->ttl, ip_hdr->ip_ttl);
    add_val(len, &flow->len, ntohs(ip_hdr->ip_len));

    info->size_pkts++;
    info->size_bytes += ntohs(ip_hdr->ip_len);
    return unlock_flow_mutex(p, flow);
}

static inline void reverse(size_t len, struct flow_tuple a[]) {
    struct flow_tuple temp;
    size_t i;
    for (i = 0; i < len / 2; i++) {
        temp = a[i];
        a[i] = a[len - i - 1];
        a[len - i - 1] = temp;
    }
}

void sort_tuples(size_t n, struct flow_tuple *a, uint8_t sort_by) {
    switch (sort_by) {
        case SORTED_NONE:
            return;
        case SORTED_BYTES:
            ks_introsort(by_bytes, n, a);
            break;
        case SORTED_PKTS:
            ks_introsort(by_pkts, n, a);
            break;
        case SORTED_PPS:
            ks_introsort(by_pps, n, a);
            break;
        case SORTED_BPS:
            ks_introsort(by_bps, n, a);
            break;
    }

    reverse(n, a);
}
