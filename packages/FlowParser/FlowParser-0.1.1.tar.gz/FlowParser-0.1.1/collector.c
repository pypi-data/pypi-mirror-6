#include <sys/time.h>
#include <unistd.h>
#include <pthread.h>

#include "parser.h"
#include "logging.h"

struct collector_info {
    uint32_t flows_collected;
};

static void update_avg(struct parser_base *p) {
    p->avg_pkts_per_second = FIXED_ALPHA * (p->pkts_last_second << FSHIFT) +
            FIXED_1_ALPHA * p->avg_pkts_per_second;
    p->avg_pkts_per_second >>= FSHIFT;

    p->pkts_last_second = p->pkts_this_second;
    p->pkts_this_second = 0;
}

static inline void update_flow_avg(struct flow *f) {
    f->avg_bytes_per_period = FIXED_ALPHA * (f->bytes_last_period << FSHIFT) +
            FIXED_1_ALPHA * f->avg_bytes_per_period;
    f->avg_bytes_per_period >>= FSHIFT;

    f->avg_pkts_per_period = FIXED_ALPHA * (f->pkts_last_period << FSHIFT) +
            FIXED_1_ALPHA * f->avg_pkts_per_period;
    f->avg_pkts_per_period >>= FSHIFT;

    f->bytes_last_period = f->bytes_this_period;
    f->bytes_this_period = 0;
    f->pkts_last_period = f->pkts_this_period;
    f->pkts_this_period = 0;
}

static void timeout_flows(struct parser_base *p, struct collector_info *info) {
    khiter_t flows_iter;
    size_t i;

    chunk_iter(tcp_chunks) tcp_it;
    chunk_iter(udp_chunks) udp_it;

    struct tcp_chunk *tcp_chunk;
    struct udp_chunk *udp_chunk;
    struct flow *flow;
    struct flow_id *id;
    int ret;

    const uint64_t time = p->last_rx_time;
    kv_reset(p->collector_list);

    if ((ret = pthread_rwlock_rdlock(&p->flows_table_lock)) != 0) {
        ERROR(p, "Unable to acquire read lock on flow table: %s", strerror(ret));
        return;
    }

    chunk_iter_register(tcp_chunks, &p->tcp_chunks, &tcp_it);
    while ((tcp_chunk = chunk_iter_next(tcp_chunks, &tcp_it)) != NULL) {
        flow = &tcp_chunk->flow.flow;
        id = &tcp_chunk->id;

        if ((ret = pthread_mutex_lock(&flow->mutex)) != 0) {
            ERROR(p, "Unable to acquire mutex on flow: %s", strerror(ret));
        }

        update_flow_avg(flow);
        if (time > flow->expiry_time) {
            if (!(flow->info.flow_state & FLOW_STATE_ITERATED_OVER)) {
                flow->info.flow_state |= FLOW_STATE_PASSIVE_TIMED_OUT;
                kv_push(struct flow_id *, p->collector_list, id);
            }
        }

        if ((ret = pthread_mutex_unlock(&flow->mutex)) != 0) {
            ERROR(p, "Unable to release flow mutex: %s", strerror(ret));
        }
    }

    chunk_iter_register(udp_chunks, &p->udp_chunks, &udp_it);
    while ((udp_chunk = chunk_iter_next(udp_chunks, &udp_it)) != NULL) {
        flow = &udp_chunk->flow.flow;
        id = &udp_chunk->id;

        if ((ret = pthread_mutex_lock(&flow->mutex)) != 0) {
            ERROR(p, "Unable to acquire mutex on flow: %s", strerror(ret));
        }
        
        update_flow_avg(flow);
        if (time > flow->expiry_time) {
            if (!(flow->info.flow_state & FLOW_STATE_ITERATED_OVER)) {
                flow->info.flow_state |= FLOW_STATE_PASSIVE_TIMED_OUT;
                kv_push(struct flow_id *, p->collector_list, id);
            }
        }
        
        if ((ret = pthread_mutex_unlock(&flow->mutex)) != 0) {
            ERROR(p, "Unable to release flow mutex: %s", strerror(ret));
        }
    }

    if ((ret = pthread_rwlock_unlock(&p->flows_table_lock)) != 0) {
        ERROR(p, "Unable to release read lock on flow table: %s", strerror(ret));
        return;
    }

    if ((ret = pthread_rwlock_wrlock(&p->flows_table_lock)) != 0) {
        ERROR(p, "Unable to acquire write lock on flow table: %s", strerror(ret));
        return;
    }

    for (i = 0; i < kv_size(p->collector_list); i++) {
        id = kv_A(p->collector_list, i);
        flows_iter = kh_get(32, p->flows_table, id);

        if (flows_iter != kh_end(p->flows_table)) {
            flow = kh_value(p->flows_table, flows_iter);
            enqueue_flow_for_dumping(p, id, flow);

            kh_del(32, p->flows_table, flows_iter);
            info->flows_collected++;
        }
    }

    if ((ret = pthread_rwlock_unlock(&p->flows_table_lock)) != 0) {
        ERROR(p, "Unable to release write lock on flow table: %s", strerror(ret));
        return;
    }
}

int close_collector(struct parser_base *p) {
    void *status;
    int ret;

    if ((ret = pthread_mutex_lock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to lock thread status mutex: %s", strerror(ret));
        return -1;
    }

    if (p->collector_status == RUNNING) {
        INFO(p, "Joining collector thread");
        
        if ((ret = pthread_join(p->collector, &status)) != 0) {
            ERROR(p, "Unable to join collector thread: %s", strerror(ret));
            pthread_mutex_unlock(&p->thread_status_mutex);
            return -1;
        }

        p->last_rx_time = UINT64_MAX;

        struct collector_info info;
        info.flows_collected = 0;

        timeout_flows(p, &info);
        kv_destroy(p->collector_list);
        INFO(p, "Final collection %d flows collected", info.flows_collected);

        p->collector_status = KILLED;
    }

    if ((ret = pthread_mutex_unlock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to unlock thread status mutex: %s", strerror(ret));
        return -1;
    }
    
    return 0;
}

static void *collector_thread(void *user) {
    struct parser_base *p = (struct parser_base *) user;

    struct collector_info info;
    struct timeval start;
    struct timeval end;
    uint32_t correction;

    while (!p->to_kill) {
        gettimeofday(&start, NULL);

        info.flows_collected = 0;

        update_avg(p);
        timeout_flows(p, &info);
        p->flows_collected += info.flows_collected;

        gettimeofday(&end, NULL);

        correction = (end.tv_sec * SEC + end.tv_usec) -
                (start.tv_sec * SEC + start.tv_usec);
        p->time_spent_collecting += correction;
        if (correction > SEC) {
            WARN(p, "Slow collection %u microseconds", correction);
            continue;
        }

        DEBUG(p, "Collector pass %u microseconds flows collected %d "
                "(queue size %d)", correction, info.flows_collected,
                get_dump_queue_size(p));

        usleep(SEC - correction);
    }

    pthread_exit(NULL);
}

int init_collector(struct parser_base *p) {
    int ret;
    pthread_attr_t attr;

    if ((ret = pthread_mutex_lock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to lock thread status mutex: %s", strerror(ret));
        return -1;
    }

    if (p->collector_status != NOT_STARTED) {
        ERROR(p, "Tried to init collector twice");
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }
    
    kv_init(p->collector_list);

    if ((ret = pthread_attr_init(&attr)) != 0) {
        ERROR(p, "Unable to init pthread attr: %s", strerror(ret));
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    if ((ret = pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE)) != 0) {
        ERROR(p, "Unable to set thread detach state: %s", strerror(ret));
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    ret = pthread_create(&p->collector, &attr, collector_thread, p);
    if (ret) {
        ERROR(p, "Unable to create collector thread: %s", strerror(ret));
        pthread_attr_destroy(&attr);
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }
    
    if ((ret = pthread_attr_destroy(&attr)) != 0) {
        ERROR(p, "Unable to destroy pthread attr: %s", strerror(ret));
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    p->collector_status = RUNNING;

    if ((ret = pthread_mutex_unlock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to unlock thread status mutex: %s", strerror(ret));
        return -1;
    }

    return 0;
}
