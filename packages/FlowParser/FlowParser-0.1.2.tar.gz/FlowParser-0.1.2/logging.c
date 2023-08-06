#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <time.h>
#include <inttypes.h>
#include <pthread.h>
#include <string.h>

#include "logging.h"
#include "parser.h"

void init_logging(struct parser_base *p, int level) {
    p->debug_level = level;
}

static uint64_t gettid(void) {
    size_t copy_size = sizeof(pthread_t);
    if (sizeof(uint64_t) < copy_size) {
        copy_size = sizeof(uint64_t);
    }
    
    pthread_t tid = pthread_self();
    uint64_t return_id = 0;
    memcpy(&return_id, &tid, copy_size);
    return return_id;
}

inline void log_message(struct parser_base *p, const char *fname, int lineno, const char *fxname,
        const int level, const char *tag, const char *format, ...) {
    UNUSED(p);
    UNUSED(level);
    
    char logging_buffer[LOGGING_BUFFER_SIZE] = {0};
    
    va_list args;
    va_start(args, format);
    vsprintf(logging_buffer, format, args);
    va_end(args);
    
    time_t now;
    
    time(&now);
    printf("%s in %s line %d func %s tid %" PRIu64 "\n [%s]: %s\n", ctime(&now), 
            fname, lineno, fxname, gettid(), tag, logging_buffer);    
}
