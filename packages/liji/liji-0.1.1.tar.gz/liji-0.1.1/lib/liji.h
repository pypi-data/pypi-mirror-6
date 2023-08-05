#ifndef __LIJI__INCLUDE__H__
#define __LIJI__INCLUDE__H__

#define LIJI_MAX_LEVELS 1024

#ifdef __GNUC__
#define likely(x)       __builtin_expect(!!(x), 1)
#define unlikely(x)     __builtin_expect(!!(x), 0)
#else
#define likely(x)       (x)
#define unlikely(x)     (x)
#endif

typedef struct liji_response {
    char *result_start;
    int len;
} liji_response;

typedef struct liji_parse_state {
    int level,
        current_key,
        position;
    char level_wanted_map[LIJI_MAX_LEVELS];
} liji_parse_state;

typedef struct liji_state {
    char *json_str;
    int json_str_len;
    char **wanted_keys;
    int *wanted_lens;
    int number_of_keys;
    liji_response response;
    liji_parse_state parse_state;
} liji_state;

liji_state liji_init(char *json_str, int json_str_len, char *wanted_keys[], int wanted_lens[], int number_of_keys);
int liji_find_multi_state(liji_state *state);

#endif