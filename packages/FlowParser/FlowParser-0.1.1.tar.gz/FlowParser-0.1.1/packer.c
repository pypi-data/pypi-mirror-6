#include <stdint.h>

#include "packer.h"

#define ONE_BYTE_LIMIT 64
#define TWO_BYTE_LIMIT 16384
#define THREE_BYTE_LIMIT 4194304
#define FOUR_BYTE_LIMIT 1073741824

#define ONE_BYTE_PACKED 0
#define TWO_BYTE_PACKED 0x40
#define THREE_BYTE_PACKED 0x80
#define FOUR_BYTE_PACKED 0xC0
#define MASK 0x3F

inline int packer_append(struct uint_seq *seq, const uint32_t value) {
    seq->len++;
    if (value < ONE_BYTE_LIMIT) {
        kv_push(u_char, seq->array, value & 0xFF);        
    } else if (value < TWO_BYTE_LIMIT) {
        kv_push(u_char, seq->array, ((value >> 8) | TWO_BYTE_PACKED) & 0xFF);
        kv_push(u_char, seq->array, value & 0xFF);
    } else if (value < THREE_BYTE_LIMIT) {
        kv_push(u_char, seq->array, ((value >> 16) | THREE_BYTE_PACKED) & 0xFF);
        kv_push(u_char, seq->array, (value >> 8) & 0xFF);
        kv_push(u_char, seq->array, value & 0xFF);
    } else if (value < FOUR_BYTE_LIMIT) {
        kv_push(u_char, seq->array, ((value >> 24) | FOUR_BYTE_PACKED) & 0xFF);
        kv_push(u_char, seq->array, (value >> 16) & 0xFF);
        kv_push(u_char, seq->array, (value >> 8) & 0xFF);
        kv_push(u_char, seq->array, value & 0xFF);
    } else {
        seq->len--;
        return -1;
    }

    return 0;
}

inline void packer_init_iterator(const struct uint_seq* seq,
        struct packer_iterator* it) {
    it->offset = 0;
    it->packed_seq = seq;
}

uint32_t packer_iterate(struct packer_iterator *it) {
    const u_char c = kv_A(it->packed_seq->array, it->offset);    
    if ((c & FOUR_BYTE_PACKED) == ONE_BYTE_PACKED) {        
        it->offset++;

        return (c & MASK);
    }

    if ((c & FOUR_BYTE_PACKED) == TWO_BYTE_PACKED) {
        it->offset += 2;

        return ((c & MASK) << 8) |
                kv_A(it->packed_seq->array, it->offset - 1);
    }
    
    if ((c & FOUR_BYTE_PACKED) == THREE_BYTE_PACKED) {
        it->offset += 3;                        
        
        return ((c & MASK) << 16) |
                (kv_A(it->packed_seq->array, it->offset - 2) << 8) |
                kv_A(it->packed_seq->array, it->offset - 1);
    }
    
    if ((c & FOUR_BYTE_PACKED) == FOUR_BYTE_PACKED) {
        it->offset += 4;
        
        return ((c & MASK) << 24) |
                (kv_A(it->packed_seq->array, it->offset - 3) << 16) |
                (kv_A(it->packed_seq->array, it->offset - 2) << 8) |
                kv_A(it->packed_seq->array, it->offset - 1);
    }   

    return 0;
}

void packer_init(struct uint_seq* seq) {
    kv_init(seq->array);
    seq->len = 0;
}

void packer_destroy(struct uint_seq* seq) {
    kv_destroy(seq->array);
}