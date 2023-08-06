#ifndef FPARSER_PYTHON_H
#define	FPARSER_PYTHON_H

#include <Python.h>
#include "stride.h"
#include "parser.h"

struct fparser_tcp_flow {
    PyObject_HEAD;
    const struct flow_id *id;
    struct tcp_flow *flow;
    uint32_t i;
    uint64_t timestamp;    
    struct fparser *fparser;

    struct packer_iterator packer_it;
    iterator(id) id_it;
    iterator(ttl) ttl_it;
    iterator(len) len_it;
    iterator(flags) flags_it;
    iterator(seq) seq_it;
    iterator(ack) ack_it;
    iterator(win) win_it;
};

struct fparser_udp_flow {
    PyObject_HEAD;
    const struct flow_id *id;
    struct udp_flow *flow;
    uint32_t i;
    uint64_t timestamp;    
    struct fparser *fparser;

    struct packer_iterator packer_it;
    iterator(id) id_it;
    iterator(ttl) ttl_it;
    iterator(len) len_it;
};

KHASH_INIT(tcp_in_python, struct flow_id *, struct fparser_tcp_flow *, 
        1, flow_id_hash, flow_id_equal)
KHASH_INIT(udp_in_python, struct flow_id *, struct fparser_udp_flow *, 
        1, flow_id_hash, flow_id_equal)

struct fparser {
    PyObject_HEAD;
    struct parser_base *parser;
    PyObject *tcp_flow_callback;
    PyObject *udp_flow_callback;
    khash_t(tcp_in_python) *tcp_cache_table;
    khash_t(udp_in_python) *udp_cache_table;
    PyObject *after_kill_callback;
};

struct fparser_flow_iter {
    PyObject_HEAD;
    struct fparser *fparser;
    kvec_t(struct flow_tuple) flows;
    size_t curr_pos;    
};

extern PyObject *FlowParserError;

extern PyTypeObject fparser_tcp_flow_type;
extern PyTypeObject fparser_udp_flow_type;

#endif	/* FPARSER_PYTHON_H */

