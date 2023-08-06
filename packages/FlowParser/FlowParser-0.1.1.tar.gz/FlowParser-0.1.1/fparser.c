#include <Python.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <netdb.h>
#include "parser.h"
#include "logging.h"
#include "fparser_python.h"

#include "structseq.h"
#include "structmember.h"

PyObject *FlowParserError;
PyMODINIT_FUNC initfparser(void);
static PyObject *fparser_get_flow_iter(PyObject *self, PyObject *args,
        PyObject *kwds);
static struct fparser_tcp_flow *tcp_flow_to_python(struct flow_id *id,
        struct tcp_flow *flow, struct fparser *fparser);
static struct fparser_udp_flow *udp_flow_to_python(struct flow_id *id,
        struct udp_flow *flow, struct fparser *fparser);
static void trigger_on_kill_callback(struct parser_base *p);

static PyTypeObject fparser_flow_id_ntuple_type = {0, 0, 0, 0, 0, 0};
static PyStructSequence_Field flow_id_ntuple_fields[] = {
    {"src", "The source IP address of the flow"},
    {"sport", "The source port of the transport header of the flow"},
    {"dest", "The destination IP address of the flow"},
    {"dport", "The dest port of the transport header of the flow"},
    {"type", "One of FLOW_TYPE_TCP or FLOW_TYPE_UDP"},
    {NULL}
};
static PyStructSequence_Desc flow_id_ntuple_desc = {
    "fparser.FlowId",
    NULL,
    flow_id_ntuple_fields,
    5
};

static PyTypeObject fparser_info_ntuple_type = {0, 0, 0, 0, 0, 0};
static PyStructSequence_Field info_ntuple_fields[] = {
    {"avg_pps", "Average packets per second"},
    {"tcp_flows", "Number of TCP flows"},
    {"udp_flows", "Number of UDP flows"},
    {"tcp_pkts", "Number of TCP pkts"},
    {"udp_pkts", "Number of UDP pkts"},
    {"time_collecting", "Time spent collecting"},
    {"live_captures", "Live capture sessions"},
    {NULL}
};
static PyStructSequence_Desc info_ntuple_desc = {
    "fparser.FparserInfo",
    NULL,
    info_ntuple_fields,
    7
};

static PyTypeObject fparser_cap_info_ntuple_type = {0, 0, 0, 0, 0, 0};
static PyStructSequence_Field cap_info_ntuple_fields[] = {
    {"device", "Device name"},
    {"filter", "BPF filter used"},
    {"snaplen", "Snapshot length"},
    {"captured_pkts", "Number of pkts captured"},
    {"dropped_pkts", "Number of pkts dropped"},
    {"iface_dropped_pkts", "Number of packets dropped at the iface buffer"},
    {NULL}
};
static PyStructSequence_Desc cap_info_ntuple_desc = {
    "fparser.FparserCapInfo",
    NULL,
    cap_info_ntuple_fields,
    6
};

static PyTypeObject fparser_flow_info_ntuple_type = {0, 0, 0, 0, 0, 0};
static PyStructSequence_Field flow_info_ntuple_fields[] = {
    {"size_pkts", "Total number of packets in flow"},
    {"size_bytes", "Total number of bytes in flow including header overhead"},
    {"pps", "Packets per second"},
    {"Bps", "Bytes per second"},
    {"first_rx", "Microseconds since epoch first packet of the flow was seen"},
    {"last_rx", "Microseconds since epoch last packet of the flow was seen"},
    {NULL}
};
static PyStructSequence_Desc flow_info_ntuple_desc = {
    "FlowInfo",
    NULL,
    flow_info_ntuple_fields,
    6
};

static PyObject *fparser_tcp_flow_iter(PyObject *self) {
    Py_INCREF(self);
    return self;
}

static PyObject *fparser_udp_flow_iter(PyObject *self) {
    Py_INCREF(self);
    return self;
}

static PyObject *fparser_flow_iter_iter(PyObject *self) {
    Py_INCREF(self);
    return self;
}

static PyObject *fparser_stop(PyObject *self, PyObject *args) {
    struct fparser *fparser = (struct fparser *) self;
    UNUSED(args);

    Py_BEGIN_ALLOW_THREADS

    kill_parser(fparser->parser);

    Py_END_ALLOW_THREADS

    Py_INCREF(Py_None);
    return Py_None;
}

static void fparser_dealloc(struct fparser *fparser) {
    fparser_stop((PyObject *) fparser, NULL);

    free(fparser->parser);
    kh_destroy(tcp_in_python, fparser->tcp_cache_table);
    kh_destroy(udp_in_python, fparser->udp_cache_table);

    Py_XDECREF(fparser->tcp_flow_callback);
    Py_XDECREF(fparser->udp_flow_callback);
    Py_XDECREF(fparser->after_kill_callback);

    fparser->ob_type->tp_free((PyObject *) fparser);
}

static PyObject *fparser_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    struct fparser *self;
    UNUSED(args);
    UNUSED(kwds);

    struct sniff_data init;
    char *source;
    int flow_timeout = -1;
    int fin_timeout = -1;
    char *filter = NULL;
    int snaplen = 100;
    int log_level = LOG_ERR;
    int is_file = 0;
    PyObject *tcp_callback = NULL;
    PyObject *udp_callback = NULL;
    PyObject *after_kill_callback = NULL;

    static char* argnames[] = {"source", "flow_timeout", "fin_timeout", "filter",
        "snaplen", "log_level", "is_file", "tcp_callback", "udp_callback", "kill_callback", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|iisiiiOOO",
            argnames, &source, &flow_timeout, &fin_timeout,
            &filter, &snaplen, &log_level, &is_file, &tcp_callback,
            &udp_callback, &after_kill_callback)) {
        return NULL;
    }

    if (tcp_callback && !PyCallable_Check(tcp_callback)) {
        PyErr_SetString(PyExc_TypeError, "TCP callback must be callable");
        return NULL;
    }

    if (udp_callback && !PyCallable_Check(udp_callback)) {
        PyErr_SetString(PyExc_TypeError, "TCP callback must be callable");
        return NULL;
    }

    if (after_kill_callback && !PyCallable_Check(after_kill_callback)) {
        PyErr_SetString(PyExc_TypeError, "Kill callback must be callable");
        return NULL;
    }

    init.snaplen = snaplen;
    init.is_source_file = is_file;
    strcpy(init.source, source);

    if (filter == NULL) {
        strcpy(init.filter, "ip");
    } else {
        strcpy(init.filter, filter);
    }

    self = (struct fparser *) type->tp_alloc(type, 0);
    self->parser = malloc(sizeof (struct parser_base));
    self->tcp_flow_callback = NULL;
    self->udp_flow_callback = NULL;

    init_parser(self->parser);
    self->parser->user = self;

    init_logging(self->parser, log_level);

    if (tcp_callback) {
        Py_INCREF(tcp_callback);
        self->tcp_flow_callback = tcp_callback;
    }

    if (udp_callback) {
        Py_INCREF(udp_callback);
        self->udp_flow_callback = udp_callback;
    }

    if (after_kill_callback) {
        Py_INCREF(after_kill_callback);
        self->after_kill_callback = after_kill_callback;
        self->parser->after_kill_callback = trigger_on_kill_callback;
    }

    if (flow_timeout >= 0) {
        self->parser->flow_timeout = flow_timeout * (uint64_t) SEC;
    }

    if (fin_timeout >= 0) {
        self->parser->tcp_afterfin_timeout = fin_timeout * (uint64_t) SEC;
    }

    self->tcp_cache_table = kh_init(tcp_in_python);
    self->udp_cache_table = kh_init(udp_in_python);

    if (init_sniff(self->parser, &init) == -1) {
        PyErr_SetString(FlowParserError, "Unable to init sniffer");
        goto fail;
    }

    if (init_dumper(self->parser) == -1) {
        PyErr_SetString(FlowParserError, "Unable to init dumper thread");
        goto fail;
    }

    if (init_collector(self->parser) == -1) {
        PyErr_SetString(FlowParserError, "Unable to init collector thread");
        goto fail;
    }

    return (PyObject *) self;

fail:

    fparser_dealloc(self);
    return NULL;
}

static void init_tcp_iter(struct fparser_tcp_flow *p) {
    const struct tcp_flow *flow = p->flow;

    p->i = 0;
    packer_init_iterator(&flow->flow.timestamps, &p->packer_it);
    init_iterator(id, &flow->flow.id, &p->id_it);
    init_iterator(ttl, &flow->flow.ttl, &p->ttl_it);
    init_iterator(len, &flow->flow.len, &p->len_it);
    init_iterator(flags, &flow->flags, &p->flags_it);
    init_iterator(seq, &flow->seq, &p->seq_it);
    init_iterator(ack, &flow->ack, &p->ack_it);
    init_iterator(win, &flow->win, &p->win_it);
    p->timestamp = flow->flow.first_rx_time;
}

static void init_udp_iter(struct fparser_udp_flow *p) {
    const struct udp_flow *flow = p->flow;

    p->i = 0;
    packer_init_iterator(&flow->flow.timestamps, &p->packer_it);
    init_iterator(id, &flow->flow.id, &p->id_it);
    init_iterator(ttl, &flow->flow.ttl, &p->ttl_it);
    init_iterator(len, &flow->flow.len, &p->len_it);
    p->timestamp = flow->flow.first_rx_time;
}

static PyObject *fparser_tcp_flow_iternext(PyObject *self) {
    struct fparser_tcp_flow *py_flow = (struct fparser_tcp_flow *) self;
    const struct flow_info *info = &py_flow->flow->flow.info;

    if (py_flow->i == info->size_pkts) {
        init_tcp_iter(py_flow);
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    py_flow->i++;
    py_flow->timestamp += (uint64_t) packer_iterate(&py_flow->packer_it);
    return Py_BuildValue("(K,H,B,H,B,I,I,H)", py_flow->timestamp,
            iterate(id, &py_flow->id_it), iterate(ttl, &py_flow->ttl_it),
            iterate(len, &py_flow->len_it), iterate(flags, &py_flow->flags_it),
            iterate(seq, &py_flow->seq_it), iterate(ack, &py_flow->ack_it),
            iterate(win, &py_flow->win_it));
}

static PyObject *fparser_flow_iter_iternext(PyObject *self) {
    struct fparser_flow_iter *iter = (struct fparser_flow_iter *) self;
    struct flow_tuple *tuple;

    if (iter->curr_pos == kv_size(iter->flows)) {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    tuple = &kv_A(iter->flows, iter->curr_pos++);
    if (tuple->flow_id->flow_type == FLOW_TYPE_TCP) {
        return (PyObject *) tcp_flow_to_python(tuple->flow_id,
                (struct tcp_flow *) tuple->flow, iter->fparser);
    } else if (tuple->flow_id->flow_type == FLOW_TYPE_UDP) {
        return (PyObject *) udp_flow_to_python(tuple->flow_id,
                (struct udp_flow *) tuple->flow, iter->fparser);
    }

    PyErr_SetString(FlowParserError, "Bad flow type");
    return NULL;
}

static PyObject *fparser_find_flow(PyObject *self, PyObject *args,
        uint8_t type) {
    char *src_ip;
    char *dest_ip;
    u_short sport, dport;

    struct fparser *fparser = (struct fparser *) self;
    struct parser_base *p = fparser->parser;

    struct flow_tuple tuple;
    struct flow *found_flow;
    struct flow_id *found_id;

    struct in_addr src_ip_n;
    struct in_addr dest_ip_n;

    if (!PyArg_ParseTuple(args, "sHsH", &src_ip, &sport, &dest_ip, &dport)) {
        return NULL;
    }

    if (inet_aton(src_ip, &src_ip_n) == 0) {
        PyErr_SetString(FlowParserError, "Bad src address");
        return NULL;
    }

    if (inet_aton(dest_ip, &dest_ip_n) == 0) {
        PyErr_SetString(FlowParserError, "Bad dest address");
        return NULL;
    }

    static struct flow_id id;
    id.src = src_ip_n;
    id.dest = dest_ip_n;
    id.sport = htons(sport);
    id.dport = htons(dport);
    id.flow_type = type;

    find_flow_and_id(p, &id, &tuple);
    found_flow = tuple.flow;
    found_id = tuple.flow_id;

    if (found_flow == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    if (pthread_mutex_lock(&found_flow->mutex) != 0) {
        PyErr_SetString(FlowParserError, "Unable to acquire mutex on flow");
        return NULL;
    }

    if (found_flow->info.flow_state & FLOW_STATE_PASSIVE_TIMED_OUT) {
        if (pthread_mutex_unlock(&found_flow->mutex) != 0) {
            PyErr_SetString(FlowParserError, "Unable to release flow mutex.");
            return NULL;
        }
        Py_INCREF(Py_None);
        return Py_None;
    }

    found_flow->info.flow_state |= FLOW_STATE_ITERATED_OVER;

    if (pthread_mutex_unlock(&found_flow->mutex) != 0) {
        PyErr_SetString(FlowParserError, "Unable to release flow mutex.");
        return NULL;
    }

    if (type == FLOW_TYPE_TCP) {
        return (PyObject *) tcp_flow_to_python(found_id,
                (struct tcp_flow *) found_flow, fparser);
    } else if (type == FLOW_TYPE_UDP) {
        return (PyObject *) udp_flow_to_python(found_id,
                (struct udp_flow *) found_flow, fparser);
    }

    PyErr_SetString(FlowParserError, "Bad flow type.");
    return NULL;
}

static PyObject *fparser_find_tcp_flow(PyObject *self, PyObject *args) {
    return fparser_find_flow(self, args, FLOW_TYPE_TCP);
}

static PyObject *fparser_find_udp_flow(PyObject *self, PyObject *args) {
    return fparser_find_flow(self, args, FLOW_TYPE_UDP);
}

static void fparser_flow_iter_dealloc(struct fparser_flow_iter *iter) {
    kv_destroy(iter->flows);
    iter->ob_type->tp_free((PyObject *) iter);
}

static void fparser_common_flow_dealloc(struct flow *flow) {
    if (pthread_mutex_lock(&flow->mutex) != 0) {
        PyErr_SetString(FlowParserError, "Unable to acquire mutex on flow");
        return;
    }

    if (flow->info.flow_state & FLOW_STATE_PASSIVE_TIMED_OUT ||
            !(flow->info.flow_state & FLOW_STATE_ITERATED_OVER)) {
        if (pthread_mutex_unlock(&flow->mutex) != 0) {
            PyErr_SetString(FlowParserError, "Unable to release flow mutex.");
            return;
        }
        PyErr_SetString(FlowParserError, "Flow in bad state upon dealloc.");
        return;
    }

    flow->info.flow_state &= ~FLOW_STATE_ITERATED_OVER;

    if (pthread_mutex_unlock(&flow->mutex) != 0) {
        PyErr_SetString(FlowParserError, "Unable to release flow mutex.");
        return;
    }

    return;
}

static void fparser_tcp_flow_dealloc(struct fparser_tcp_flow *fparser_flow) {
    khiter_t k;
    kh_tcp_in_python_t *table;

    fparser_common_flow_dealloc((struct flow *) fparser_flow->flow);

    table = fparser_flow->fparser->tcp_cache_table;
    k = kh_get(tcp_in_python, table,
            fparser_flow->id);
    if (k == kh_end(table)) {
        PyErr_SetString(FlowParserError, "TCP flow not in cache when free");
    } else {
        kh_del(tcp_in_python, table, k);
    }

    fparser_flow->ob_type->tp_free((PyObject *) fparser_flow);
}

static void fparser_udp_flow_dealloc(struct fparser_udp_flow *fparser_flow) {
    khiter_t k;
    kh_udp_in_python_t *table;

    fparser_common_flow_dealloc((struct flow *) fparser_flow->flow);

    table = fparser_flow->fparser->udp_cache_table;
    k = kh_get(udp_in_python, table,
            fparser_flow->id);
    if (k == kh_end(table)) {
        PyErr_SetString(FlowParserError, "UDP flow not in cache when free");
    } else {
        kh_del(udp_in_python, table, k);
    }

    fparser_flow->ob_type->tp_free((PyObject *) fparser_flow);
}

PyTypeObject fparser_flow_iter_type = {
    PyObject_HEAD_INIT(NULL)
    0, /*ob_size*/
    "fparser._FlowIter", /*tp_name*/
    sizeof (struct fparser_flow_iter), /*tp_basicsize*/
    0, /*tp_itemsize*/
    (destructor) fparser_flow_iter_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_compare*/
    0, /*tp_repr*/
    0, /*tp_as_number*/
    0, /*tp_as_sequence*/
    0, /*tp_as_mapping*/
    0, /*tp_hash */
    0, /*tp_call*/
    0, /*tp_str*/
    0, /*tp_getattro*/
    0, /*tp_setattro*/
    0, /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
    "Internal iterator over the flows of an fparser.", /* tp_doc */
    0, /* tp_traverse */
    0, /* tp_clear */
    0, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    fparser_flow_iter_iter, /* tp_iter: __iter__() method */
    fparser_flow_iter_iternext, /* tp_iternext: next() method */
    0 /* tp_methods */
};

static PyObject *fparser_get_flow_iter(PyObject *self,
        PyObject *args, PyObject *kwds) {
    static char* argnames[] = {"sort_order", NULL};

    struct fparser *fparser = (struct fparser *) self;
    struct parser_base *p = fparser->parser;
    struct flow *flow;
    struct flow_id *id;
    struct flow_tuple *tuple;
    khiter_t main_iter;
    struct fparser_flow_iter *iter;
    uint8_t sort_order = SORTED_NONE;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|B:get_flow_iter",
            argnames, &sort_order)) {
        return NULL;
    }

    iter = PyObject_New(struct fparser_flow_iter, &fparser_flow_iter_type);
    if (!iter) {
        PyErr_SetString(FlowParserError, "Unable to allocate iter object");
        return NULL;
    }

    if (!PyObject_Init((PyObject *) iter, &fparser_flow_iter_type)) {
        Py_DECREF(iter);
        PyErr_SetString(FlowParserError, "Unable to init iter object");
        return NULL;
    }

    kv_init(iter->flows);
    iter->curr_pos = 0;
    iter->fparser = fparser;

    pthread_rwlock_rdlock(&p->flows_table_lock);
    DEBUG(p, "Acquired read lock on flows table");

    for (main_iter = kh_begin(p->flows_table);
            main_iter != kh_end(p->flows_table); main_iter++) {
        if (kh_exist(p->flows_table, main_iter)) {
            flow = kh_value(p->flows_table, main_iter);
            id = kh_key(p->flows_table, main_iter);

            if (pthread_mutex_lock(&flow->mutex) != 0) {
                ERROR(p, "Unable to acquire mutex on flow");
            }

            if (flow->info.flow_state & FLOW_STATE_PASSIVE_TIMED_OUT) {
                if (pthread_mutex_unlock(&flow->mutex) != 0) {
                    ERROR(p, "Unable to release flow mutex.");
                }
                continue;
            }

            flow->info.flow_state |= FLOW_STATE_ITERATED_OVER;

            if (pthread_mutex_unlock(&flow->mutex) != 0) {
                ERROR(p, "Unable to release flow mutex.");
            }

            tuple = (kv_pushp(struct flow_tuple, iter->flows));
            tuple->flow = flow;
            tuple->flow_id = id;
        }
    }

    pthread_rwlock_unlock(&p->flows_table_lock);
    DEBUG(p, "Released read lock on flows table");

    sort_tuples(kv_size(iter->flows), iter->flows.a, sort_order);

    return (PyObject *) iter;
}

static PyObject *fparser_udp_flow_iternext(PyObject *self) {
    struct fparser_udp_flow *py_flow = (struct fparser_udp_flow *) self;
    const struct flow_info *info = &py_flow->flow->flow.info;

    if (py_flow->i == info->size_pkts) {
        init_udp_iter(py_flow);
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    py_flow->i++;
    py_flow->timestamp += (uint64_t) packer_iterate(&py_flow->packer_it);
    return Py_BuildValue("(K,H,B,H)", py_flow->timestamp,
            iterate(id, &py_flow->id_it), iterate(ttl, &py_flow->ttl_it),
            iterate(len, &py_flow->len_it));
}

static Py_ssize_t fparser_flow_get_len(PyObject *self) {
    struct fparser_tcp_flow *py_flow = (struct fparser_tcp_flow *) self;
    return (Py_ssize_t) py_flow->flow->flow.info.size_pkts;
}

static PyObject *fparser_flow_get_id(PyObject *self) {
    char src_ip[50];
    char dest_ip[50];

    struct fparser_tcp_flow *py_flow = (struct fparser_tcp_flow *) self;
    strcpy(src_ip, inet_ntoa(py_flow->id->src));
    strcpy(dest_ip, inet_ntoa(py_flow->id->dest));

    PyObject *ntuple = PyStructSequence_New(&fparser_flow_id_ntuple_type);
    PyStructSequence_SET_ITEM(ntuple, 0, PyString_FromString(src_ip));
    PyStructSequence_SET_ITEM(ntuple, 1,
            PyInt_FromSize_t((size_t) ntohs(py_flow->id->sport)));
    PyStructSequence_SET_ITEM(ntuple, 2, PyString_FromString(dest_ip));
    PyStructSequence_SET_ITEM(ntuple, 3,
            PyInt_FromSize_t((size_t) ntohs(py_flow->id->dport)));
    PyStructSequence_SET_ITEM(ntuple, 4,
            PyInt_FromSize_t((size_t) py_flow->id->flow_type));

    return ntuple;
}

static PyObject *fparser_flow_get_info(PyObject *self) {
    PyObject *ntuple;

    struct fparser_tcp_flow *py_flow = (struct fparser_tcp_flow *) self;
    struct flow *flow = &py_flow->flow->flow;

    pthread_mutex_lock(&flow->mutex);
    ntuple = PyStructSequence_New(&fparser_flow_info_ntuple_type);
    PyStructSequence_SET_ITEM(ntuple, 0,
            PyLong_FromUnsignedLong((unsigned long) flow->info.size_pkts));
    PyStructSequence_SET_ITEM(ntuple, 1,
            PyLong_FromUnsignedLongLong((unsigned long long) flow->info.size_bytes));
    PyStructSequence_SET_ITEM(ntuple, 2,
            PyFloat_FromDouble((double) flow->avg_pkts_per_period / (double) FIXED_1));
    PyStructSequence_SET_ITEM(ntuple, 3,
            PyFloat_FromDouble((double) flow->avg_bytes_per_period / (double) FIXED_1));
    PyStructSequence_SET_ITEM(ntuple, 4,
            PyLong_FromUnsignedLongLong((unsigned long long) flow->first_rx_time));
    PyStructSequence_SET_ITEM(ntuple, 5,
            PyLong_FromUnsignedLongLong((unsigned long long) flow->last_rx_time));
    pthread_mutex_unlock(&flow->mutex);
    return ntuple;
}

static PyObject *fparser_flow_get_ip_id_encoded(PyObject *self) {
    struct fparser_tcp_flow *py_flow = (struct fparser_tcp_flow *) self;
    const stride_field(id) * s_field = &py_flow->flow->flow.id;
    uint32_t i, n;
    u_short value;
    u_short stride;
    size_t stride_len;

    n = kv_size(s_field->vector);
    PyObject *return_tuple = PyTuple_New(n);

    for (i = 0; i < n; i++) {
        get_stride_at(id, s_field, i, &value, &stride, &stride_len);
        PyTuple_SET_ITEM(return_tuple, i, Py_BuildValue("(HHI)", value,
                stride, stride_len));
    }

    return return_tuple;
}

static PyObject *fparser_flow_get_ttl_encoded(PyObject *self) {
    struct fparser_tcp_flow *py_flow = (struct fparser_tcp_flow *) self;
    const stride_field(ttl) * s_field = &py_flow->flow->flow.ttl;
    uint32_t i, n;
    u_char value;
    u_char stride;
    size_t stride_len;

    n = kv_size(s_field->vector);
    PyObject *return_tuple = PyTuple_New(n);

    for (i = 0; i < n; i++) {
        get_stride_at(ttl, s_field, i, &value, &stride, &stride_len);
        PyTuple_SET_ITEM(return_tuple, i, Py_BuildValue("(BBI)", value,
                stride, stride_len));
    }

    return return_tuple;
}

static PyObject *fparser_tcp_flow_get_encoding_info(PyObject *self) {
    struct fparser_tcp_flow *py_flow = (struct fparser_tcp_flow *) self;
    const struct flow *flow = &py_flow->flow->flow;
    const struct tcp_flow *tcp_flow = py_flow->flow;

    size_t id_fields = 0, ttl_fields = 0, len_fields = 0, seq_fields = 0,
            ack_fields = 0, win_fields = 0, flags_fields = 0;
    size_t id_stride = 0, ttl_stride = 0, len_stride = 0, seq_stride = 0,
            ack_stride = 0, win_stride = 0, flags_stride = 0;

    get_size(id, &flow->id, &id_fields, &id_stride);
    get_size(ttl, &flow->ttl, &ttl_fields, &ttl_stride);
    get_size(len, &flow->len, &len_fields, &len_stride);
    get_size(seq, &tcp_flow->seq, &seq_fields, &seq_stride);
    get_size(ack, &tcp_flow->ack, &ack_fields, &ack_stride);
    get_size(flags, &tcp_flow->flags, &flags_fields, &flags_stride);
    get_size(win, &tcp_flow->win, &win_fields, &win_stride);

    return Py_BuildValue("{s:I, s:I, s:I, s:I, s:I, s:I, s:I, s:I, "
            "s:I, s:I, s:I, s:I, s:I}",
            "id_fields", id_fields, "id_stride", id_stride,
            "ttl_fields", ttl_fields, "ttl_stride", ttl_stride,
            "len_fields", len_fields, "len_stride", len_stride,
            "seq_fields", seq_fields, "seq_stride", seq_stride,
            "ack_fields", ack_fields, "ack_stride", ack_stride,
            "win_fields", win_stride, "flags_fields", flags_fields,
            "flags_stride", flags_stride);
}

static PyObject *fparser_udp_flow_get_encoding_info(PyObject *self) {
    struct fparser_udp_flow *py_flow = (struct fparser_udp_flow *) self;
    const struct flow *flow = &py_flow->flow->flow;

    size_t id_fields = 0, ttl_fields = 0, len_fields = 0;
    size_t id_stride = 0, ttl_stride = 0, len_stride = 0;

    get_size(id, &flow->id, &id_fields, &id_stride);
    get_size(ttl, &flow->ttl, &ttl_fields, &ttl_stride);
    get_size(len, &flow->len, &len_fields, &len_stride);

    return Py_BuildValue("{s:I, s:I, s:I, s:I, s:I, s:I}",
            "id_fields", id_fields, "id_stride", id_stride,
            "ttl_fields", ttl_fields, "ttl_stride", ttl_stride,
            "len_fields", len_fields, "len_stride", len_stride);
}

static PyObject *fparser_get_info(PyObject *self, PyObject *args) {
    UNUSED(args);

    struct fparser *fparser;
    struct parser_info info;
    struct sniff_info sniff_info;

    PyObject *sniff_ntuple;
    PyObject *info_ntuple;
    fparser = (struct fparser *) self;

    populate_parser_info(fparser->parser, &info);
    populate_sniff_info(fparser->parser, &sniff_info);

    sniff_ntuple = PyStructSequence_New(&fparser_cap_info_ntuple_type);
    PyStructSequence_SET_ITEM(sniff_ntuple, 0,
            PyString_FromString(fparser->parser->sniffer_data.source));
    PyStructSequence_SET_ITEM(sniff_ntuple, 1,
            PyString_FromString(fparser->parser->sniffer_data.filter));
    PyStructSequence_SET_ITEM(sniff_ntuple, 2,
            PyInt_FromLong((long) fparser->parser->sniffer_data.snaplen));
    PyStructSequence_SET_ITEM(sniff_ntuple, 3,
            PyLong_FromUnsignedLong((unsigned long) sniff_info.pkts_rx));
    PyStructSequence_SET_ITEM(sniff_ntuple, 4,
            PyLong_FromUnsignedLong((unsigned long) sniff_info.pkts_dropped));
    PyStructSequence_SET_ITEM(sniff_ntuple, 5,
            PyLong_FromUnsignedLong((unsigned long) sniff_info.pkts_ifdropped));

    info_ntuple = PyStructSequence_New(&fparser_info_ntuple_type);
    PyStructSequence_SET_ITEM(info_ntuple, 0,
            PyFloat_FromDouble(info.avg_pkts_per_sec));
    PyStructSequence_SET_ITEM(info_ntuple, 1,
            PyLong_FromUnsignedLong((unsigned long) info.tcp_flows));
    PyStructSequence_SET_ITEM(info_ntuple, 2,
            PyLong_FromUnsignedLong((unsigned long) info.udp_flows));
    PyStructSequence_SET_ITEM(info_ntuple, 3,
            PyLong_FromUnsignedLong((unsigned long) info.tcp_pkts));
    PyStructSequence_SET_ITEM(info_ntuple, 4,
            PyLong_FromUnsignedLong((unsigned long) info.udp_pkts));
    PyStructSequence_SET_ITEM(info_ntuple, 5,
            PyLong_FromUnsignedLongLong(
            (unsigned long long) info.time_spent_collecting));
    PyStructSequence_SET_ITEM(info_ntuple, 6, sniff_ntuple);

    return info_ntuple;
}

static PyObject *set_callback(PyObject *self, PyObject *args, int tcp) {
    struct fparser *fparser = (struct fparser *) self;

    PyObject *result = NULL;
    PyObject *temp;

    if (PyArg_ParseTuple(args, "O:set_callback", &temp)) {
        if (!PyCallable_Check(temp)) {
            PyErr_SetString(PyExc_TypeError, "parameter must be callable");
            return NULL;
        }
        Py_XINCREF(temp); /* Add a reference to new callback */
        if (tcp) {
            Py_XDECREF(fparser->tcp_flow_callback);
            fparser->tcp_flow_callback = temp;
        } else {
            Py_XDECREF(fparser->udp_flow_callback);
            fparser->udp_flow_callback = temp;
        }

        Py_INCREF(Py_None);
        result = Py_None;
    }
    return result;
}

static PyObject *fparser_set_tcp_callback(PyObject *self, PyObject *args) {
    return set_callback(self, args, 1);
}

static PyObject *fparser_set_udp_callback(PyObject *self, PyObject *args) {
    return set_callback(self, args, 0);
}

static PyMethodDef fparser_module_methods[] = {
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyMethodDef fparser_methods[] = {
    {"stop", fparser_stop, METH_VARARGS, "stops the parser"},
    {"set_tcp_callback", fparser_set_tcp_callback, METH_VARARGS,
        "Sets the TCP callback"},
    {"set_udp_callback", fparser_set_udp_callback, METH_VARARGS,
        "Sets the UDP callback"},
    {"flow_iter", (PyCFunction) fparser_get_flow_iter, METH_KEYWORDS,
        "Returns an iterator over the flows."},
    {"find_tcp_flow", fparser_find_tcp_flow, METH_VARARGS,
        "Finds an active TCP flow"},
    {"find_udp_flow", fparser_find_udp_flow, METH_VARARGS,
        "Finds an active UDP flow."},
    {"get_info", fparser_get_info, METH_VARARGS,
        "Gets info about the running fparser instance"},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyMethodDef tcp_flow_methods[] = {
    {"get_id", (PyCFunction) fparser_flow_get_id, METH_NOARGS,
        "Returns (source ip, source port, dest ip, dest port)"},
    {"get_info", (PyCFunction) fparser_flow_get_info, METH_NOARGS,
        "Returns a dict describing the flow"},
    {"get_encodings", (PyCFunction) fparser_tcp_flow_get_encoding_info, METH_NOARGS,
        "Returns a dict describing how this flow is encoded in memory"},
    {"get_id_encoded", (PyCFunction) fparser_flow_get_ip_id_encoded, METH_NOARGS,
        "Returns the ip id field, run length encoded as a tuple "
        "of (value, add_offset, num_values)"},
    {"get_ttl_encoded", (PyCFunction) fparser_flow_get_ttl_encoded, METH_NOARGS,
        "Returns the ip ttl field, run length encoded as a tuple "
        "of (value, add_offset, num_values)"},
    {NULL} /* Sentinel */
};

static PyMethodDef udp_flow_methods[] = {
    {"get_id", (PyCFunction) fparser_flow_get_id, METH_NOARGS,
        "Returns (source ip, source port, dest ip, dest port)"},
    {"get_info", (PyCFunction) fparser_flow_get_info, METH_NOARGS,
        "Returns a dict describing the flow"},
    {"get_encodings", (PyCFunction) fparser_udp_flow_get_encoding_info, METH_NOARGS,
        "Returns a dict describing how this flow is encoded in memory"},
    {"get_id_encoded", (PyCFunction) fparser_flow_get_ip_id_encoded, METH_NOARGS,
        "Returns the ip id field, run length encoded as a tuple "
        "of (value, add_offset, num_values)"},
    {"get_ttl_encoded", (PyCFunction) fparser_flow_get_ttl_encoded, METH_NOARGS,
        "Returns the ip ttl field, run length encoded as a tuple "
        "of (value, add_offset, num_values)"},
    {NULL} /* Sentinel */
};

static PySequenceMethods commmon_sequence_methods = {
    fparser_flow_get_len, /* sq_length */
};

PyTypeObject fparser_tcp_flow_type = {
    PyObject_HEAD_INIT(NULL)
    0, /*ob_size*/
    "fparser._TCPFlow", /*tp_name*/
    sizeof (struct fparser_tcp_flow), /*tp_basicsize*/
    0, /*tp_itemsize*/
    (destructor) fparser_tcp_flow_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_compare*/
    0, /*tp_repr*/
    0, /*tp_as_number*/
    &commmon_sequence_methods, /*tp_as_sequence*/
    0, /*tp_as_mapping*/
    0, /*tp_hash */
    0, /*tp_call*/
    0, /*tp_str*/
    0, /*tp_getattro*/
    0, /*tp_setattro*/
    0, /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
    /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
       use tp_iter and tp_iternext fields. */
    "Internal fparser TCP flow object.", /* tp_doc */
    0, /* tp_traverse */
    0, /* tp_clear */
    0, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    fparser_tcp_flow_iter, /* tp_iter: __iter__() method */
    fparser_tcp_flow_iternext, /* tp_iternext: next() method */
    tcp_flow_methods /* tp_methods */
};

PyTypeObject fparser_udp_flow_type = {
    PyObject_HEAD_INIT(NULL)
    0, /*ob_size*/
    "fparser._UDPFlow", /*tp_name*/
    sizeof (struct fparser_udp_flow), /*tp_basicsize*/
    0, /*tp_itemsize*/
    (destructor) fparser_udp_flow_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_compare*/
    0, /*tp_repr*/
    0, /*tp_as_number*/
    &commmon_sequence_methods, /*tp_as_sequence*/
    0, /*tp_as_mapping*/
    0, /*tp_hash */
    0, /*tp_call*/
    0, /*tp_str*/
    0, /*tp_getattro*/
    0, /*tp_setattro*/
    0, /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,
    /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
       use tp_iter and tp_iternext fields. */
    "Internal fparser UDP flow object.", /* tp_doc */
    0, /* tp_traverse */
    0, /* tp_clear */
    0, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    fparser_udp_flow_iter, /* tp_iter: __iter__() method */
    fparser_udp_flow_iternext, /* tp_iternext: next() method */
    udp_flow_methods /* tp_methods */
};

PyTypeObject fparser_type = {
    PyObject_HEAD_INIT(NULL)
    0, /*ob_size*/
    "fparser.FParser", /*tp_name*/
    sizeof (struct fparser), /*tp_basicsize*/
    0, /*tp_itemsize*/
    (destructor) fparser_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    0, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_compare*/
    0, /*tp_repr*/
    0, /*tp_as_number*/
    0, /*tp_as_sequence*/
    0, /*tp_as_mapping*/
    0, /*tp_hash */
    0, /*tp_call*/
    0, /*tp_str*/
    0, /*tp_getattro*/
    0, /*tp_setattro*/
    0, /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,
    /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
       use tp_iter and tp_iternext fields. */
    "Internal fparser object.", /* tp_doc */
    0, /* tp_traverse */
    0, /* tp_clear */
    0, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    0, /* tp_iter: __iter__() method */
    0, /* tp_iternext: next() method */
    fparser_methods, /* tp_methods */
    0, /* tp_members */
    0, /* tp_getset */
    0, /* tp_base */
    0, /* tp_dict */
    0, /* tp_descr_get */
    0, /* tp_descr_set */
    0, /* tp_dictoffset */
    0, /* tp_init */
    0, /* tp_alloc */
    fparser_new, /* tp_new */
};

PyMODINIT_FUNC initfparser(void) {
    PyObject *m;

    m = Py_InitModule("fparser", fparser_module_methods);
    if (m == NULL) {
        return;
    }

    if (PyType_Ready(&fparser_type) < 0) {
        return;
    }

    if (PyType_Ready(&fparser_tcp_flow_type) < 0) {
        return;
    }

    if (PyType_Ready(&fparser_udp_flow_type) < 0) {
        return;
    }

    if (PyType_Ready(&fparser_flow_iter_type) < 0) {
        return;
    }

    PyStructSequence_InitType(&fparser_flow_id_ntuple_type,
            &flow_id_ntuple_desc);
    Py_INCREF(&fparser_flow_id_ntuple_type);
    PyModule_AddObject(m, "FlowId", (PyObject *) & fparser_flow_id_ntuple_type);

    PyStructSequence_InitType(&fparser_flow_info_ntuple_type,
            &flow_info_ntuple_desc);
    Py_INCREF(&fparser_flow_info_ntuple_type);
    PyModule_AddObject(m, "FlowInfo",
            (PyObject *) & fparser_flow_info_ntuple_type);

    PyStructSequence_InitType(&fparser_info_ntuple_type,
            &info_ntuple_desc);
    Py_INCREF(&fparser_info_ntuple_type);
    PyModule_AddObject(m, "FParserInfo",
            (PyObject *) & fparser_info_ntuple_type);

    PyStructSequence_InitType(&fparser_cap_info_ntuple_type,
            &cap_info_ntuple_desc);
    Py_INCREF(&fparser_cap_info_ntuple_type);
    PyModule_AddObject(m, "FParserCapInfo",
            (PyObject *) & fparser_cap_info_ntuple_type);

    FlowParserError = PyErr_NewException("fparser.error", NULL, NULL);
    Py_INCREF(FlowParserError);
    PyModule_AddObject(m, "error", FlowParserError);

    Py_INCREF(&fparser_tcp_flow_type);
    PyModule_AddObject(m, "_TCPFlow", (PyObject *) & fparser_tcp_flow_type);

    Py_INCREF(&fparser_udp_flow_type);
    PyModule_AddObject(m, "_UDPFlow", (PyObject *) & fparser_udp_flow_type);

    Py_INCREF(&fparser_type);
    PyModule_AddObject(m, "FParser", (PyObject *) & fparser_type);

    Py_INCREF(&fparser_flow_iter_type);
    PyModule_AddObject(m, "_FlowIter", (PyObject *) & fparser_flow_iter_type);

    PyModule_AddIntConstant(m, "SORT_NONE", SORTED_NONE);
    PyModule_AddIntConstant(m, "SORT_PKTS", SORTED_PKTS);
    PyModule_AddIntConstant(m, "SORT_BYTES", SORTED_BYTES);
    PyModule_AddIntConstant(m, "SORT_PPS", SORTED_PPS);
    PyModule_AddIntConstant(m, "SORT_BPS", SORTED_BPS);
    PyModule_AddIntConstant(m, "FLOW_TYPE_TCP", FLOW_TYPE_TCP);
    PyModule_AddIntConstant(m, "FLOW_TYPE_UDP", FLOW_TYPE_UDP);

    PyEval_InitThreads();
}

/**
 * Constructs a new python object that reflects the in-memory TCP flow stored 
 * in a parser.
 * 
 * @param id the flow id
 * @param flow the TCP flow that the new python flow will represent 
 * @return a new fparser_tcp_flow or NULL on failure
 */
static struct fparser_tcp_flow *tcp_flow_to_python(struct flow_id *id,
        struct tcp_flow *flow, struct fparser *fparser) {
    struct fparser_tcp_flow *py_flow;
    khiter_t k;
    int ret;

    k = kh_get(tcp_in_python, fparser->tcp_cache_table, id);
    if (k != kh_end(fparser->tcp_cache_table)) {
        py_flow = kh_value(fparser->tcp_cache_table, k);
        Py_INCREF(py_flow);
        return py_flow;
    }

    py_flow = PyObject_New(struct fparser_tcp_flow, &fparser_tcp_flow_type);
    if (!py_flow) {
        return NULL;
    }

    if (!PyObject_Init((PyObject *) py_flow, &fparser_tcp_flow_type)) {
        Py_DECREF(py_flow);
        return NULL;
    }

    py_flow->flow = flow;
    py_flow->id = id;
    py_flow->fparser = fparser;
    init_tcp_iter(py_flow);

    k = kh_put(tcp_in_python, fparser->tcp_cache_table, id, &ret);
    kh_value(fparser->tcp_cache_table, k) = py_flow;

    return py_flow;
}

static void trigger_on_kill_callback(struct parser_base *p) {
    PyGILState_STATE d_gstate;
    struct fparser *fparser = (struct fparser *) p->user;
    PyObject *result;

    if (fparser->after_kill_callback == NULL) {
        return;
    }

    d_gstate = PyGILState_Ensure();
    result = PyObject_CallObject(fparser->after_kill_callback, NULL);
    if (result == NULL) {
        PyErr_Print();
    }

    Py_XDECREF(result);
    PyGILState_Release(d_gstate);
}

/**
 * Called by the dumper when a TCP flow completes and needs to be offloaded. If 
 * there is no TCP callback registered with the python fparser object this 
 * function returns without doing anything. If there is, it is called with a 
 * new fparser_tcp_flow to reflect the flow.
 * 
 * @param p the parser context
 * @param id the flow id
 * @param flow the flow
 */
void offload_tcp_flow(struct parser_base *p, struct flow_id *id,
        struct tcp_flow *flow) {
    PyGILState_STATE d_gstate;
    struct fparser_tcp_flow *py_flow;
    PyObject *arglist;
    PyObject *result;

    struct fparser *fparser = (struct fparser *) p->user;
    if (fparser->tcp_flow_callback == NULL) {
        return;
    }

    d_gstate = PyGILState_Ensure();
    py_flow = tcp_flow_to_python(id, flow, fparser);
    if (py_flow == NULL) {
        PyGILState_Release(d_gstate);
        return;
    }

    arglist = Py_BuildValue("(O)", py_flow);
    Py_DECREF(py_flow);
    result = PyObject_CallObject(fparser->tcp_flow_callback, arglist);
    Py_DECREF(arglist);

    if (result == NULL) {
        PyErr_Print();
    }

    Py_XDECREF(result);
    PyGILState_Release(d_gstate);
}

/**
 * Constructs a new python object that reflects the in-memory UDP flow stored 
 * in a parser.
 * 
 * @param id the flow id
 * @param flow the UDP flow that the new python flow will represent
 * @return a new fparser_udp_flow or NULL on failure
 */
static struct fparser_udp_flow *udp_flow_to_python(struct flow_id *id,
        struct udp_flow *flow, struct fparser *fparser) {
    struct fparser_udp_flow *py_flow;
    khiter_t k;
    int ret;

    k = kh_get(udp_in_python, fparser->udp_cache_table, id);
    if (k != kh_end(fparser->udp_cache_table)) {
        py_flow = kh_value(fparser->udp_cache_table, k);
        Py_INCREF(py_flow);
        return py_flow;
    }

    py_flow = PyObject_New(struct fparser_udp_flow, &fparser_udp_flow_type);
    if (!py_flow) {
        return NULL;
    }

    if (!PyObject_Init((PyObject *) py_flow, &fparser_udp_flow_type)) {
        Py_DECREF(py_flow);
        return NULL;
    }

    py_flow->flow = flow;
    py_flow->id = id;
    py_flow->fparser = fparser;
    init_udp_iter(py_flow);

    k = kh_put(udp_in_python, fparser->udp_cache_table, id, &ret);
    kh_value(fparser->udp_cache_table, k) = py_flow;

    return py_flow;
}

/**
 * Called by the dumper when a UDP flow completes and needs to be offloaded. If 
 * there is no UDP callback registered with the python fparser object this 
 * function returns without doing anything. If there is, it is called with a 
 * new fparser_udp_flow to reflect the flow.
 * 
 * @param p the parser context
 * @param id the flow id
 * @param flow the flow
 */
void offload_udp_flow(struct parser_base *parser,
        struct flow_id *id, struct udp_flow *flow) {
    PyGILState_STATE d_gstate;
    PyObject *arglist;
    PyObject *result;
    struct fparser_udp_flow *py_flow;

    struct fparser *fparser = (struct fparser *) parser->user;
    if (fparser->udp_flow_callback == NULL) {
        return;
    }

    d_gstate = PyGILState_Ensure();
    py_flow = udp_flow_to_python(id, flow, fparser);
    if (py_flow == NULL) {
        PyGILState_Release(d_gstate);
        return;
    }

    arglist = Py_BuildValue("(O)", py_flow);
    Py_DECREF(py_flow);
    result = PyObject_CallObject(fparser->udp_flow_callback, arglist);
    Py_DECREF(arglist);

    if (result == NULL) {
        PyErr_Print();
    }

    Py_XDECREF(result);
    PyGILState_Release(d_gstate);
}
