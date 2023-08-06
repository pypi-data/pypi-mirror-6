#ifndef LOGGING_H
#define	LOGGING_H

#include <syslog.h>

#include "parser.h"

#define LOGGING_TAG "ttl_parser"
#define LOGGING_BUFFER_SIZE 500

#define WARN(p, format, ...) do {if (p->debug_level >= LOG_WARNING) {\
                log_message(p, __FILE__, __LINE__, __func__, LOG_WARNING, "WARN", format, ##__VA_ARGS__);}} while (0)

#define ERROR(p, format, ...) do {if (p->debug_level >= LOG_ERR) {\
                log_message(p, __FILE__, __LINE__, __func__, LOG_ERR, "ERROR", format, ##__VA_ARGS__);}} while (0)

#define DEBUG(p, format, ...) do {if (p->debug_level >= LOG_DEBUG) {\
                log_message(p, __FILE__, __LINE__, __func__, LOG_DEBUG, "DEBUG", format, ##__VA_ARGS__);}} while (0)

#define INFO(p, format, ...) do {if (p->debug_level >= LOG_INFO) {\
                log_message(p, __FILE__, __LINE__, __func__, LOG_INFO, "INFO", format, ##__VA_ARGS__);}} while (0)

void init_logging(struct parser_base *parser, int level);
void log_message(struct parser_base *p, const char *fname, int lineno, const char *fxname,
        const int level, const char *tag, const char *format, ...);
#endif	/* LOGGING_H */

