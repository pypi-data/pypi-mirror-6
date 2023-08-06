#ifndef STRIDE_H
#define	STRIDE_H

#include "khash/kvec.h"

#define STRIDE_FIELD(id, type, def) \
struct stride_##id {\
    type value;\
    size_t length;\
    type stride;\
};\
struct stride_field_##id { \
    kvec_t(struct stride_##id) vector;\
};\
struct stride_iterator_##id {\
    const struct stride_field_##id *sfield; \
    size_t curr_blocknum; \
    struct stride_##id *curr_block;\
    size_t offset; \
};\
static inline void init_stride_field_##id(struct stride_field_##id *s) {\
        kv_init(s->vector);} \
static inline void close_stride_field_##id(struct stride_field_##id *s) {\
        kv_destroy(s->vector);} \
static inline void add_val_##id(struct stride_field_##id *sfield,\
        const type val) {   \
        const size_t v_size = kv_size(sfield->vector);\
        struct stride_##id *s;\
        if (v_size == 0) {\
            s = (kv_pushp(struct stride_##id, sfield->vector));\
            s->value = val; s->length = 0; s->stride = 0;\
            return;\
        }\
\
        s = &kv_A(sfield->vector, v_size - 1);\
        const size_t s_length = s->length;\
        if (s_length == 0) {\
            s->stride = val - s->value;\
            s->length++;\
            return;\
        }\
\
        if (s->value + (s_length + 1) * (s->stride) == val) {\
            s->length++;\
            return;\
        }\
\
        s = (kv_pushp(struct stride_##id, sfield->vector));\
        s->value = val; s->length = 0; s->stride=0;}\
static inline void init_iterator_##id(const struct stride_field_##id *sfield, \
        struct stride_iterator_##id *iter) { \
        iter->sfield = sfield;\
        iter->curr_blocknum = 0; iter->curr_block = NULL; iter->offset = 0;\
}\
static inline type iterate_##id(struct stride_iterator_##id *iter) { \
        if (iter->curr_block == NULL || iter->offset > iter->curr_block->length) { \
            if (iter->curr_blocknum == kv_size(iter->sfield->vector)) {\
                return def;\
            }\
            iter->curr_block = &kv_A(iter->sfield->vector, \
                                       iter->curr_blocknum++);\
            iter->offset = 0;\
        }\
        return iter->curr_block->value + \
                ((type) iter->offset++) * iter->curr_block->stride;\
}\
static inline type get_last_val_##id(const struct stride_field_##id *sfield) { \
        size_t v_size = kv_size(sfield->vector);\
        if (v_size == 0) return def;\
        struct stride_##id *s = &kv_A(sfield->vector, v_size - 1);\
        return s->value + (s->stride * s->length);\
}\
static inline void get_size_##id(const struct stride_field_##id *sfield, \
        size_t *nfields, size_t *total_stride) { \
        size_t i;\
        *nfields += kv_size(sfield->vector);\
        for (i = 0; i < kv_size(sfield->vector); i++) {\
            *total_stride += kv_A(sfield->vector, i).length;\
        }\
}\
static inline void get_stride_at_##id(const struct stride_field_##id *sfield, \
        size_t i, type *value, type *stride, size_t *length) {\
        *value = kv_A(sfield->vector, i).value;\
        *stride = kv_A(sfield->vector, i).stride;\
        *length = kv_A(sfield->vector, i).length;\
}

/*
static inline void dump_stride_##id(const struct stride_field_##id *sfield) {\
        size_t i;\
        printf("(");\
        for (i = 0; i < kv_size(sfield->vector); i++) {\
            struct stride_##id *s = &kv_A(sfield->vector, i);\
            printf("v: %u, l: %u, s: %u ||", s->value, s->length, s->stride);\
        }\
        printf(")\n");\
}
*/

#define stride_field(id) struct stride_field_##id
#define iterator(id) struct stride_iterator_##id
#define init_stride_field(id, s) init_stride_field_##id(s)
#define close_stride_field(id, s) close_stride_field_##id(s)
#define add_val(id, s, val) add_val_##id(s, val)
#define iterate(id, it) iterate_##id(it)
#define init_iterator(id, s, it) init_iterator_##id(s, it)
#define get_last_val(id, s) get_last_val_##id(s)
#define get_size(id, s, x, y) get_size_##id(s, x, y)
#define get_stride_at(id, s, i, val, stride, len) get_stride_at_##id(s, i, val, stride, len)

//#define dump_stride(id, s) dump_stride_##id(s)

#endif	/* STRIDE_H */

