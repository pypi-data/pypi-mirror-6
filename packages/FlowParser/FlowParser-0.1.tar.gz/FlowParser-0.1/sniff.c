#include <sys/poll.h>
#include "sniff.h"
#include "parser.h"
#include "logging.h"

static int init_offset(struct parser_base *p) {
    if (p->sniffer_data.datalink == DLT_EN10MB) {
        return SIZE_ETHERNET;
    } else if (p->sniffer_data.datalink == DLT_RAW) {
        return 0;
    } else {
        return -1;
    }
}

static void sniff_tcp(struct parser_base *p,
        uint64_t timestamp, int size_ip, int init_offset,
        const struct sniff_ip *ip, const u_char *pkt) {
    const struct sniff_tcp *tcp;
    int size_tcp;

    tcp = (const struct sniff_tcp*) (pkt + init_offset + size_ip);
    size_tcp = TH_OFF(tcp)*4;
    if (size_tcp < 20) {
        INFO(p, "Invalid TCP header length: %u bytes\n", size_tcp);
        return;
    }

    static struct flow_id id;
    id.src = ip->ip_src;
    id.dest = ip->ip_dst;
    id.sport = tcp->th_sport;
    id.dport = tcp->th_dport;
    id.flow_type = FLOW_TYPE_TCP;

    struct flow *flow = lookup_flow(p, &id);
    handle_tcp_pkt(p, (struct tcp_flow *) flow, ip, tcp, timestamp);
}

static void sniff_udp(struct parser_base *p,
        uint64_t timestamp, int size_ip, int init_offset,
        const struct sniff_ip *ip, const u_char *pkt) {
    const struct sniff_udp *udp;

    udp = (const struct sniff_udp*) (pkt + init_offset + size_ip);

    static struct flow_id id;
    id.src = ip->ip_src;
    id.dest = ip->ip_dst;
    id.sport = udp->uh_sport;
    id.dport = udp->uh_dport;
    id.flow_type = FLOW_TYPE_UDP;

    struct flow *flow = lookup_flow(p, &id);
    handle_udp_pkt(p, (struct udp_flow *) flow, ip, timestamp);
}

static void got_packet(u_char *args, const struct pcap_pkthdr *header,
        const u_char *packet) {
    struct parser_base *p = (struct parser_base *) args;

    uint64_t timestamp;
    const struct sniff_ip *ip; /* The IP header */
    int size_ip;

    timestamp = ((uint64_t) header->ts.tv_sec) * SEC +
            (uint64_t) header->ts.tv_usec;

    /* define/compute ip header offset */
    int offset = init_offset(p);
    ip = (const struct sniff_ip*) (packet + offset);

    size_ip = IP_HL(ip)*4;
    if (size_ip < 20) {
        INFO(p, "Invalid IP header length: %u bytes pcap header len %u\n", size_ip, header->len);
        return;
    }

    if (ip->ip_p == IPPROTO_TCP) {
        sniff_tcp(p, timestamp, size_ip, offset, ip, packet);
    } else if (ip->ip_p == IPPROTO_UDP) {
        sniff_udp(p, timestamp, size_ip, offset, ip, packet);
    } else {
        DEBUG(p, "Tried to handle unknown protocol type");
    }

    return;
}

static int sniff_open(struct parser_base *p) {
    struct sniff_data *init = &p->sniffer_data;
    char errbuf[PCAP_ERRBUF_SIZE];
    struct bpf_program fp;
    bpf_u_int32 mask = 0;
    bpf_u_int32 net = 0;

    if (init->is_source_file) {
        p->sniffer_handle = pcap_open_offline(init->source, errbuf);
    } else {
        p->sniffer_handle = pcap_open_live(init->source, init->snaplen, 1,
                1000, errbuf);
    }

    if (p->sniffer_handle == NULL) {
        ERROR(p, "Couldn't open source %s: %s", init->source, errbuf);
        return -1;
    }

    int datalink = pcap_datalink(p->sniffer_handle);
    if (datalink != DLT_EN10MB && datalink != DLT_RAW) {
        ERROR(p, "Unknown datalink %s", pcap_datalink_val_to_name(datalink));
        return -1;
    } else {
        INFO(p, "Loaded datalink %s", pcap_datalink_val_to_name(datalink));
        init->datalink = datalink;
    }

    if (!init->is_source_file) {
        if (pcap_lookupnet(init->source, &net, &mask, errbuf) == -1) {
            WARN(p, "Couldn't get netmask for device %s: %s", init->source, errbuf);
            net = 0;
            mask = 0;
        }

        if (pcap_setnonblock(p->sniffer_handle, 1, errbuf) == -1) {
            ERROR(p, "Could not set device %s to non-blocking: %s\n",
                    init->source, errbuf);
            pcap_freecode(&fp);
            return -1;
        }
    }

    if (pcap_compile(p->sniffer_handle, &fp, init->filter, 0, net) == -1) {
        ERROR(p, "Couldn't parse filter %s: %s",
                init->filter, pcap_geterr(p->sniffer_handle));
        pcap_freecode(&fp);
        return -1;
    }

    if (pcap_setfilter(p->sniffer_handle, &fp) == -1) {
        ERROR(p, "Couldn't install filter %s: %s",
                init->filter, pcap_geterr(p->sniffer_handle));
        pcap_freecode(&fp);
        return -1;
    }

    pcap_freecode(&fp);
    return 0;
}

static void *sniff_thread(void *user) {
    struct parser_base *p = (struct parser_base *) user;
    struct sniff_data *init = &p->sniffer_data;
    struct pollfd pfd;

    int poll_result;
    int ret;

    if (init->is_source_file) {
        INFO(p, "Will start reading from %s", init->source);
        ret = pcap_loop(p->sniffer_handle, -1, got_packet, (void *) p);
        if (ret == 0) {
            INFO(p, "Done reading from %s", init->source);
        } else {
            INFO(p, "Error while reading from %s : %s", init->source, pcap_geterr(p->sniffer_handle));
        }

        kill_parser(p);
    } else {
        INFO(p, "Will start listening on %s", init->source);
        pfd.fd = pcap_fileno(p->sniffer_handle);
        pfd.events = POLLIN;

        while (!p->to_kill) {
            poll_result = poll(&pfd, 1, 1000);

            switch (poll_result) {
                case -1: // error
                    ERROR(p, "Bad poll on pcap fd");
                    pthread_exit(NULL);

                case 0: // timeout
                    break;

                default: // packet
                    pcap_dispatch(p->sniffer_handle, 1, got_packet, (void *) p);
            }
        }
    }

    pcap_close(p->sniffer_handle);
    pthread_exit(NULL);
}

void populate_sniff_info(struct parser_base *p, struct sniff_info *info) {
    struct pcap_stat ps;
    pcap_stats(p->sniffer_handle, &ps);

    info->pkts_rx = ps.ps_recv;
    info->pkts_dropped = ps.ps_drop;
    info->pkts_ifdropped = ps.ps_ifdrop;
}

int close_sniff(struct parser_base *p) {
    int ret;
    void *status;

    if ((ret = pthread_mutex_lock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to lock thread status mutex: %s", strerror(ret));
        return -1;
    }

    if (p->sniffer_status == RUNNING) {
        INFO(p, "Joining sniffer thread");
        if ((ret = pthread_join(p->sniffer, &status)) != 0) {
            ERROR(p, "Unable to join sniffer thread: %s", strerror(ret));
            pthread_mutex_unlock(&p->thread_status_mutex);
            return -1;
        }
        
        p->sniffer_status = KILLED;
    }

    if ((ret = pthread_mutex_unlock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to unlock thread status mutex: %s", strerror(ret));
        return -1;
    }

    return 0;
}

int init_sniff(struct parser_base *p, struct sniff_data *init_data) {
    pthread_attr_t attr;
    int ret;

    if ((ret = pthread_mutex_lock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to lock thread status mutex: %s", strerror(ret));
        return -1;
    }
    
    if (p->sniffer_status != NOT_STARTED) {
        ERROR(p, "Tried to init sniffer twice");
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }
    
    memcpy(&p->sniffer_data, init_data, sizeof (struct sniff_data));

    if (sniff_open(p) < 0) {
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

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

    ret = pthread_create(&p->sniffer, &attr, sniff_thread, p);
    if (ret) {
        ERROR(p, "Unable to create sniffer thread: %s", strerror(ret));
        pthread_attr_destroy(&attr);
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    if ((ret = pthread_attr_destroy(&attr)) != 0) {
        ERROR(p, "Unable to destroy pthread attr: %s", strerror(ret));
        pthread_mutex_unlock(&p->thread_status_mutex);
        return -1;
    }

    p->sniffer_status = RUNNING;
    
    if ((ret = pthread_mutex_unlock(&p->thread_status_mutex)) != 0) {
        ERROR(p, "Unable to unlock thread status mutex: %s", strerror(ret));
        return -1;
    }
    
    return 0;
}

