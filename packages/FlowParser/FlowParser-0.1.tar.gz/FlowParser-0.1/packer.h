#ifndef PACKER_H
#define	PACKER_H

#include <sys/types.h>
#include "khash/kvec.h"

struct uint_seq {
    kvec_t(u_char) array;
    uint32_t len;
};

struct packer_iterator {
    const struct uint_seq *packed_seq;
    uint32_t offset;
};

void packer_destroy(struct uint_seq *seq);
void packer_init(struct uint_seq *seq);
int packer_append(struct uint_seq *seq, uint32_t value);
void packer_init_iterator(const struct uint_seq *seq, struct packer_iterator *it);
uint32_t packer_iterate(struct packer_iterator *it);

#endif	/* PACKER_H */

