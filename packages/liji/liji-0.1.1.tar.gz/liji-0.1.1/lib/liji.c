#include "liji.h"
#include <stdio.h>
#include <string.h>


#define FINAL_CHECKER(level) \
    if (level == result_level && tmp_result) { \
        if (!non_ws) { \
            non_ws = current_pos - 1; \
        } \
        int tmp_len = non_ws - tmp_result; \
        if (*tmp_result == '"') { \
            ++tmp_result; \
            tmp_len -= 2; \
        } \
        state->response.result_start = tmp_result; \
        state->response.len = tmp_len; \
        return 1; \
    } \
    non_ws = NULL; \


int liji_find_multi_state(liji_state *state)
{
    liji_parse_state *parse_state = &(state->parse_state);

    if (parse_state->position >= state->json_str_len) {
        return 0;
    }

    char *current_pos = (char *)(state->json_str + parse_state->position), val;

    char *key_start = 0, *tmp_result = 0, *non_ws = 0;

    int result_level = 0,
        key_len = 0,
        tmp_level;

    char in_string = 0,
         in_key = 0,
         skipping = 1,
         escaped = 0;

    memset(&(state->response), 0, sizeof(liji_response));

    while (parse_state->position++ < state->json_str_len) {
        val = *(current_pos++);

        if (val == '\\' && !escaped) {
            escaped = 1;
        } else if(escaped) {
            escaped = (escaped + 1) % 3;
        }
        if (val != '"' && in_string) {
            continue;
        }
        if (tmp_result) {
            if (val == ' ' || val == '\n' || val == '\r' || val == '\t') {
                if (skipping) {
                    tmp_result++;
                    continue;
                }
                if (!non_ws) {
                    non_ws = current_pos - 1;
                }
            } else {
                skipping = 0;
            }
        }
        switch (val) {
            case '{':
                key_start = 0;
                key_len = 0;
            case '[':
                ++parse_state->level;
                if (unlikely(parse_state->level >= LIJI_MAX_LEVELS)) {
                    fprintf(stderr, "[LIJI ERROR] Too deeply nested json\n");
                    return 0;
                }
                break;

            case '}':
            case ']':
                tmp_level = parse_state->level--;
                if (parse_state->level_wanted_map[parse_state->level]) {
                    --parse_state->current_key;
                }
                FINAL_CHECKER(tmp_level);
                break;
            case ',':
                key_start = 0;
                key_len = 0;
                FINAL_CHECKER(parse_state->level);
                break;
            case ':':
                if (in_key && !tmp_result) {
                    tmp_result = current_pos;
                    result_level = parse_state->level;
                }
                break;
            case '"':
                if (escaped) {
                    break;
                }
                in_string = !in_string;
                if (!key_start) {
                    key_start = current_pos;
                } else if (!key_len) {
                    key_len = current_pos - 1 - key_start;
                    if (key_len == state->wanted_lens[parse_state->current_key] && memcmp(key_start, state->wanted_keys[parse_state->current_key], key_len) == 0) {
                        ++parse_state->current_key;
                        parse_state->level_wanted_map[parse_state->level] = 1;
                        if (parse_state->current_key == state->number_of_keys) {
                            in_key = 1;
                            --parse_state->current_key;
                        }
                    }
                }
                break;
        }
    }

    return 0;
}


liji_state liji_init(char *json_str, int json_str_len, char *wanted_keys[], int wanted_lens[], int number_of_keys) {
    liji_state state = {json_str, json_str_len, wanted_keys, wanted_lens, number_of_keys, {0, 0}, {0, 0, 0, {0}}};
    return state;
}
