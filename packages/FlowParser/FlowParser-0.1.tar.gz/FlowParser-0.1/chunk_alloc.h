#ifndef CHUNK_ALLOC_H
#define	CHUNK_ALLOC_H

#include <sys/types.h>
#include <pthread.h>

#include "khash/kvec.h"

#define CHUNK_ALLOC(id, type, block_size)\
struct chunk_##id {\
   type data;\
   uint8_t flag;\
   size_t index;\
};\
struct block_##id {\
   struct chunk_##id chunks[block_size];\
};\
struct chunk_alloc_base_##id {\
   kvec_t(struct block_##id*) blocks;\
   kvec_t(size_t) free_data;\
   size_t block_index;\
   size_t chunk_index;\
   volatile size_t max_pos;\
   volatile size_t iterated_over;\
   pthread_mutex_t mutex;\
};\
struct chunk_alloc_iter_##id {\
   size_t curr_pos;\
   size_t curr_chunk_index;\
   struct block_##id *curr_block;\
   struct chunk_alloc_base_##id *base;\
};\
static inline type *iter_next_##id(struct chunk_alloc_iter_##id *it) {\
   struct chunk_##id *chunk;\
   if (it->curr_pos == it->base->max_pos) {\
        return NULL;\
   }\
\
   if (it->curr_chunk_index == block_size) {\
        it->curr_chunk_index = 0;\
        it->curr_block = kv_A(it->base->blocks, (it->curr_pos / block_size));\
   }\
\
   it->curr_pos++;\
   chunk = &(it->curr_block->chunks[it->curr_chunk_index++]);\
   if (chunk->flag) {\
        return &chunk->data;\
   }\
   return iter_next_##id(it);\
}\
static inline void register_iterator_##id(struct chunk_alloc_base_##id *base,\
        struct chunk_alloc_iter_##id *it) {\
   it->curr_pos = 0;\
   it->curr_chunk_index = 0;\
   it->base = base;\
   __sync_fetch_and_add(&base->iterated_over, 1);\
   if (kv_size(it->base->blocks)) {\
        it->curr_block = kv_A(it->base->blocks, 0);\
   } else {\
        it->curr_block = NULL;\
   }\
}\
static inline void unregister_iterator_##id(struct chunk_alloc_iter_##id *it) {\
   __sync_fetch_and_sub(&it->base->iterated_over, 1);\
}\
static inline void init_chunk_base_##id(struct chunk_alloc_base_##id *base) {\
   kv_init(base->blocks);\
   kv_init(base->free_data);\
   base->block_index = 0;\
   base->chunk_index = 0;\
   base->max_pos = 0;\
   pthread_mutex_init(&base->mutex, NULL);\
   *(kv_pushp(struct block_##id *, base->blocks)) = malloc(sizeof(struct block_##id));\
}\
static inline void close_chunk_base_##id(struct chunk_alloc_base_##id *base) {\
    size_t i;\
    struct block_##id *block;\
    for (i = 0; i < kv_size(base->blocks); i++) {\
        block = kv_A(base->blocks, i);\
        free(block);\
    }\
    kv_destroy(base->blocks);\
    kv_destroy(base->free_data);\
}\
static inline type *chunk_alloc_##id(struct chunk_alloc_base_##id *base) {\
   struct chunk_##id *chunk;\
   struct block_##id *block;\
   pthread_mutex_lock(&base->mutex);\
   if (kv_size(base->free_data) && !base->iterated_over) {\
      size_t i = kv_pop(base->free_data);\
      size_t block_index = i / block_size;\
      size_t chunk_index = i % block_size;\
      chunk = &(kv_A(base->blocks, block_index)->chunks[chunk_index]);\
      chunk->flag = 1;\
      pthread_mutex_unlock(&base->mutex);\
      return &chunk->data;\
   }\
\
   if (base->chunk_index == block_size) {\
      block = malloc(sizeof(struct block_##id));\
      *(kv_pushp(struct block_##id *, base->blocks)) = block;\
      base->chunk_index = 0;\
      base->block_index = kv_size(base->blocks) - 1;\
   } else {\
      block = kv_A(base->blocks, base->block_index);\
   }\
\
   chunk = &block->chunks[base->chunk_index];\
\
   chunk->flag = 1;\
   chunk->index = base->block_index * block_size + base->chunk_index++;\
   __sync_fetch_and_add(&base->max_pos, 1);\
   pthread_mutex_unlock(&base->mutex);\
   return &chunk->data;\
}\
static inline void chunk_dealloc_##id(struct chunk_alloc_base_##id *base,\
   type *p) {\
   pthread_mutex_lock(&base->mutex);\
   struct chunk_##id *chunk_p = (struct chunk_##id *) p;\
   chunk_p->flag = 0;\
   kv_push(size_t, base->free_data, chunk_p->index);\
   pthread_mutex_unlock(&base->mutex);\
}

#define chunk_base(id) struct chunk_alloc_base_##id
#define chunk_iter(id) struct chunk_alloc_iter_##id

#define chunk_data(chunk_base, i) (kv_A(chunk_base.chunks, i))
#define chunk_used(chunk) (chunk->flag != 0)
#define chunk_totalnum(chunk_base) (kv_size(chunk_base->chunks))
#define chunk_alloc(id, base) chunk_alloc_##id(base)
#define chunk_dealloc(id, base, p) chunk_dealloc_##id(base, p)
#define chunk_base_init(id, base) init_chunk_base_##id(base)
#define chunk_base_close(id, base) close_chunk_base_##id(base)
#define chunk_iter_register(id, base, it) register_iterator_##id(base, it)
#define chunk_iter_unregister(id, it) unregister_iterator_##id(it)
#define chunk_iter_next(id, it) iter_next_##id(it)

#endif	/* CHUNK_ALLOC_H */

