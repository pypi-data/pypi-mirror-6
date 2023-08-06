#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <errno.h>
#include <unistd.h>

#include "parser.h"
#include "logging.h"

int close_dumper(struct parser_base *p) {
    void *status;
    int ret;

    if ((ret = pthread_mutex_lock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to lock thread status mutex: %s", strerror(ret));
        return -1;
    }

    if (p->dumper_status == RUNNING) {
        INFO(p, "Joining dumper thread - %zu flows to be flushed", p->dump_queue->size);

        if ((ret = pthread_mutex_lock(&p->dump_queue_mutex)) != 0) {
            ERROR(p, "Unable to lock dump queue mutex: %s", strerror(ret));
            pthread_mutex_unlock(&p->thread_status_mutex);
            return -1;
        }

        p->dumper_to_kill = 1;

        if ((ret = pthread_cond_signal(&p->dump_queue_has_items)) != 0) {
            ERROR(p, "Unable to signal dump queue: %s", strerror(ret));
            pthread_mutex_unlock(&p->dump_queue_mutex);
            pthread_mutex_unlock(&p->thread_status_mutex);
            return -1;
        }

        if ((ret = pthread_mutex_unlock(&p->dump_queue_mutex)) != 0) {
            ERROR(p, "Unable to unlock dump queue mutex: %s", strerror(ret));
            pthread_mutex_unlock(&p->thread_status_mutex);
            return -1;
        }

        if ((ret = pthread_join(p->dumper, &status)) != 0) {
            ERROR(p, "Unable to join dump thread: %s", strerror(ret));
            pthread_mutex_unlock(&p->thread_status_mutex);
            return -1;
        }

        if (p->dump_queue->size) {
            WARN(p, "Not all flows flushed");
        }

        kl_destroy(32, p->dump_queue);

        p->dumper_status = KILLED;
    }

    if ((ret = pthread_mutex_unlock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to unlock thread status mutex: %s", strerror(ret));
        return -1;
    }
    
    return 0;
}

void enqueue_flow_for_dumping(struct parser_base *p, struct flow_id* id, struct flow* flow) {
    int ret;

    struct flow_tuple *dump_tuple = malloc(sizeof (struct flow_tuple));
    dump_tuple->flow = flow;
    dump_tuple->flow_id = id;

    if ((ret = pthread_mutex_lock(&p->dump_queue_mutex)) != 0) {
        ERROR(p, "Unable to lock dump queue mutex: %s", strerror(ret));
        return;
    }

    *kl_pushp(32, p->dump_queue) = dump_tuple;
    if ((ret = pthread_cond_signal(&p->dump_queue_has_items)) != 0) {
        ERROR(p, "Unable to signal dump queue: %s", strerror(ret));
    }

    if ((ret = pthread_mutex_unlock(&p->dump_queue_mutex)) != 0) {
        ERROR(p, "Unable to unlock dump queue mutex: %s", strerror(ret));
    }
}

static void *dumper_thread(void *user) {
    struct parser_base *p = (struct parser_base *) user;
    int ret;

    struct flow_tuple *dump_tuple;
    uint8_t type;

    while (p->dump_queue->size || !p->dumper_to_kill) {
        /* sloppy - size is not protected by mutex, but should be fine since 
         * it is checked again after waking from the condition. */

        if ((ret = pthread_mutex_lock(&p->dump_queue_mutex)) != 0) {
            ERROR(p, "Unable to lock dump queue mutex: %s", strerror(ret));
            break;
        }

        if (!p->dump_queue->size) {
            if ((ret = pthread_cond_wait(&p->dump_queue_has_items, &p->dump_queue_mutex)) != 0) {
                ERROR(p, "Unable to wait on dump queue condition: %s", strerror(ret));
                pthread_mutex_unlock(&p->dump_queue_mutex);
                break;
            }
        }

        if (p->dump_queue->size) {
            dump_tuple = kl_val(kl_begin(p->dump_queue));
            kl_shift(32, p->dump_queue, NULL);
            if ((ret = pthread_mutex_unlock(&p->dump_queue_mutex)) != 0) {
                ERROR(p, "Unable to unlock dump queue mutex: %s", strerror(ret));
                break;
            }

            type = dump_tuple->flow_id->flow_type;
            if (type == FLOW_TYPE_TCP) {
                offload_tcp_flow(p, dump_tuple->flow_id, (struct tcp_flow *) dump_tuple->flow);
                free_tcp_chunk(p, dump_tuple->flow_id, (struct tcp_flow *) dump_tuple->flow);
            } else if (type == FLOW_TYPE_UDP) {
                offload_udp_flow(p, dump_tuple->flow_id, (struct udp_flow *) dump_tuple->flow);
                free_udp_chunk(p, dump_tuple->flow_id, (struct udp_flow *) dump_tuple->flow);
            } else {
                ERROR(p, "Bad flow id in dumper. Memory corrupted");
            }

            free(dump_tuple);
        } else {
            if ((ret = pthread_mutex_unlock(&p->dump_queue_mutex)) != 0) {
                ERROR(p, "Unable to unlock dump queue mutex: %s", strerror(ret));
                break;
            }
        }
    }

    pthread_exit(NULL);
}

int init_dumper(struct parser_base *p) {
    pthread_attr_t attr;
    int ret;

    if ((ret = pthread_mutex_lock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to lock thread status mutex: %s", strerror(ret));
        return -1;
    }

    if (p->dumper_status != NOT_STARTED) {
        ERROR(p, "Tried to init dumper twice");
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    p->dumper_to_kill = 0;

    if ((ret = pthread_mutex_init(&p->dump_queue_mutex, NULL)) != 0) {
        ERROR(p, "Unable to init dump queue mutex: %s", strerror(ret));
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    if ((ret = pthread_cond_init(&p->dump_queue_has_items, NULL)) != 0) {
        ERROR(p, "Unable to init dump queue condition: %s", strerror(ret));
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    p->dump_queue = kl_init(32);

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

    ret = pthread_create(&p->dumper, &attr, dumper_thread, p);
    if (ret) {
        ERROR(p, "Unable to create dumper thread: %s", strerror(ret));
        pthread_attr_destroy(&attr);
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    if ((ret = pthread_attr_destroy(&attr)) != 0) {
        ERROR(p, "Unable to destroy pthread attr: %s", strerror(ret));
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    p->dumper_status = RUNNING;

    if ((ret = pthread_mutex_unlock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to unlock thread status mutex: %s", strerror(ret));
        return -1;
    }

    return 0;
}

size_t get_dump_queue_size(struct parser_base *p) {
    int ret;
    size_t return_size = 0;

    if ((ret = pthread_mutex_lock(&p->dump_queue_mutex)) != 0) {
        ERROR(p, "Unable to lock dump queue mutex: %s", strerror(ret));
        return 0;
    }

    return_size = p->dump_queue->size;

    if ((ret = pthread_mutex_unlock(&p->dump_queue_mutex)) != 0) {
        ERROR(p, "Unable to unlock dump queue mutex: %s", strerror(ret));
        return 0;
    }

    return return_size;
}
