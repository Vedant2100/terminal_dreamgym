# Benchmark v2 evaluation

Model qwen2.5:7b; temperature [0.7]; up to [3] attempts; seeds [1, 2, 3, 4, 5]. 52 tasks in 16 repos (config 1, contract 6, error_handling 14, logic 25, trap 6).

Success is strict: the target test passes and no test that passed before the edit fails afterwards.

## Success rates

| Condition | Runs | Strict success | Target test only | First attempt | Passed but broke another test | Unparseable replies |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| no_skill | 260 | 0.488 | 0.565 | 0.346 | 20 | 1.1% |
| handwritten_skills | 260 | 0.454 | 0.573 | 0.323 | 31 | 2.2% |
| strong_skill | 260 | 0.389 | 0.481 | 0.292 | 24 | 1.6% |
| placebo | 260 | 0.423 | 0.481 | 0.319 | 15 | 2.3% |

## Paired differences

Mean over tasks of (A − B). Primary interval: bootstrap resampling repos. Co-primary comparisons use 97.5% intervals (Bonferroni over two); secondary ones 95%, uncorrected.

| A − B | Role | Strict success (repo-cluster CI) | Task-level CI | Tasks better / worse / tied | First attempt |
| --- | --- | --- | --- | --- | --- |
| handwritten_skills − no_skill | co-primary (97.5%) | -0.035 [-0.129, +0.053] | -0.035 [-0.131, +0.061] | 13 / 17 / 22 | -0.023 [-0.077, +0.033] |
| strong_skill − no_skill | co-primary (97.5%) | -0.100 [-0.187, -0.018] | -0.100 [-0.189, -0.008] | 14 / 26 / 12 | -0.054 [-0.114, +0.004] |
| strong_skill − handwritten_skills | secondary (95.0%) | -0.065 [-0.170, +0.023] | -0.065 [-0.142, +0.008] | 16 / 20 / 16 | -0.031 [-0.110, +0.039] |
| handwritten_skills − placebo | secondary (95.0%) | +0.031 [-0.105, +0.168] | +0.031 [-0.061, +0.131] | 18 / 16 / 18 | +0.004 [-0.108, +0.122] |
| strong_skill − placebo | secondary (95.0%) | -0.035 [-0.162, +0.073] | -0.035 [-0.123, +0.054] | 18 / 18 / 16 | -0.027 [-0.115, +0.051] |
| placebo − no_skill | secondary (95.0%) | -0.065 [-0.157, +0.033] | -0.065 [-0.154, +0.023] | 11 / 21 / 20 | -0.027 [-0.114, +0.061] |

## By bug category (exploratory, 95% repo-cluster CI)

| A − B | config | contract | error_handling | logic | trap |
| --- | --- | --- | --- | --- | --- |
| handwritten_skills − no_skill | +0.400 [+0.400, +0.400] | -0.133 [-0.200, -0.067] | -0.186 [-0.400, -0.022] | +0.056 [-0.078, +0.163] | -0.033 [-0.233, +0.167] |
| strong_skill − no_skill | +0.200 [+0.200, +0.200] | -0.033 [-0.200, +0.100] | -0.171 [-0.339, -0.015] | -0.096 [-0.227, +0.029] | -0.067 [-0.167, +0.067] |
| strong_skill − handwritten_skills | -0.200 [-0.200, -0.200] | +0.100 [-0.080, +0.240] | +0.014 [-0.129, +0.150] | -0.152 [-0.285, -0.040] | -0.033 [-0.233, +0.167] |
| handwritten_skills − placebo | +1.000 [+1.000, +1.000] | +0.000 [-0.160, +0.120] | -0.114 [-0.317, +0.031] | +0.104 [-0.087, +0.267] | -0.067 [-0.233, +0.100] |
| strong_skill − placebo | +0.800 [+0.800, +0.800] | +0.100 [-0.080, +0.250] | -0.100 [-0.292, +0.086] | -0.048 [-0.200, +0.074] | -0.100 [-0.333, +0.067] |
| placebo − no_skill | -0.600 [-0.600, -0.600] | -0.133 [-0.200, -0.040] | -0.071 [-0.277, +0.123] | -0.048 [-0.182, +0.073] | +0.033 [-0.133, +0.200] |

## By authored difficulty (exploratory, 95% repo-cluster CI)

| A − B | easy | hard | medium |
| --- | --- | --- | --- |
| handwritten_skills − no_skill | -0.070 [-0.224, +0.048] | +0.167 [+0.033, +0.333] | -0.052 [-0.136, +0.053] |
| strong_skill − no_skill | -0.174 [-0.290, -0.072] | -0.133 [-0.333, +0.067] | -0.017 [-0.106, +0.048] |
| strong_skill − handwritten_skills | -0.104 [-0.215, +0.009] | -0.300 [-0.467, -0.133] | +0.035 [-0.122, +0.155] |
| handwritten_skills − placebo | +0.017 [-0.244, +0.238] | +0.133 [-0.067, +0.333] | +0.017 [-0.082, +0.152] |
| strong_skill − placebo | -0.087 [-0.278, +0.067] | -0.167 [-0.367, +0.000] | +0.052 [-0.116, +0.183] |
| placebo − no_skill | -0.087 [-0.242, +0.095] | +0.033 [-0.300, +0.333] | -0.070 [-0.152, +0.022] |

## Per task (strict success over seeds)

| Task | no_skill | handwritten_skills | strong_skill | placebo |
| --- | ---: | ---: | ---: | ---: |
| cart__zero_quantity_allowed | 0.20 | 0.20 | 0.40 | 1.00 |
| csv_report__average_divides_by_zero | 1.00 | 1.00 | 0.80 | 1.00 |
| csv_report__empty_text_stopiteration | 0.60 | 1.00 | 0.40 | 1.00 |
| csv_report__render_key_not_normalised | 0.40 | 0.40 | 0.20 | 0.20 |
| dep_graph__deps_not_lowercased | 0.60 | 1.00 | 0.80 | 0.40 |
| dep_graph__lineno_zero_based | 0.40 | 1.00 | 0.20 | 0.40 |
| dep_graph__missing_name_unchecked | 0.80 | 0.40 | 0.40 | 0.20 |
| dep_graph__ready_list_not_heapified | 0.60 | 0.60 | 0.20 | 0.80 |
| inventory__release_checks_on_hand | 0.60 | 0.40 | 0.60 | 0.40 |
| inventory__reserve_zero_from_empty_site | 0.20 | 0.40 | 0.00 | 0.60 |
| inventory__unknown_site_created | 0.00 | 0.00 | 0.00 | 0.00 |
| ledger__empty_amount_check | 0.20 | 0.20 | 0.40 | 0.20 |
| ledger__round_half_even | 0.20 | 0.20 | 0.00 | 0.40 |
| ledger__thousands_separator | 0.00 | 0.20 | 0.20 | 0.60 |
| log_parser__dash_size_rejected | 0.20 | 0.20 | 0.40 | 0.20 |
| log_parser__duration_left_in_seconds | 0.20 | 0.40 | 0.40 | 0.40 |
| log_parser__error_rate_reuses_errors | 0.80 | 0.40 | 0.80 | 0.80 |
| log_parser__percentile_floor_rank | 0.60 | 0.80 | 0.40 | 0.40 |
| log_parser__percentile_range_unchecked | 0.80 | 0.00 | 0.20 | 0.00 |
| log_parser__query_string_kept | 0.80 | 0.40 | 0.80 | 0.20 |
| log_parser__tie_order_by_insertion | 0.20 | 0.20 | 0.40 | 0.20 |
| log_parser__window_end_inclusive | 0.20 | 1.00 | 1.00 | 0.60 |
| markdown_table__decimals_not_passed | 0.60 | 1.00 | 0.80 | 0.00 |
| markdown_table__int_without_separators | 1.00 | 1.00 | 0.40 | 0.00 |
| markdown_table__newline_dropped | 0.80 | 1.00 | 0.60 | 0.60 |
| rate_limiter__clock_allows_backwards | 1.00 | 1.00 | 1.00 | 0.80 |
| rate_limiter__per_minute_not_converted | 0.20 | 0.20 | 0.00 | 0.00 |
| rate_limiter__refill_timestamp_not_updated | 0.00 | 0.00 | 0.00 | 0.00 |
| rate_limiter__retry_after_multiplied | 0.20 | 0.00 | 0.20 | 0.00 |
| scheduling__business_days_ignore_holidays | 1.00 | 1.00 | 0.40 | 0.40 |
| scheduling__conflicts_not_sorted | 0.80 | 0.80 | 1.00 | 0.80 |
| scheduling__empty_slot_between_back_to_back | 0.00 | 0.20 | 0.20 | 0.00 |
| scheduling__holiday_shift_drops_holidays | 0.20 | 0.00 | 0.00 | 0.00 |
| semver__build_in_sort_key | 1.00 | 1.00 | 0.60 | 1.00 |
| semver__resolve_returns_none | 0.40 | 0.40 | 0.00 | 0.40 |
| settings__ini_missing_section_crashes | 0.20 | 0.00 | 0.20 | 0.20 |
| todo_cli__blank_title_checked_before_strip | 0.20 | 0.20 | 0.40 | 0.00 |
| todo_cli__next_id_from_count | 1.00 | 1.00 | 0.80 | 0.80 |
| todo_cli__pending_sort_key | 1.00 | 0.80 | 0.80 | 0.40 |
| todo_cli__remove_by_position | 0.40 | 1.00 | 0.60 | 1.00 |
| ttl_cache__memo_none_treated_as_missing | 0.60 | 0.40 | 0.60 | 0.60 |
| ttl_cache__read_not_counted_as_use | 0.20 | 0.20 | 0.20 | 0.20 |
| units__degree_alias_key_case | 0.20 | 0.20 | 0.00 | 0.00 |
| units__dimension_check_removed | 0.40 | 0.00 | 0.20 | 0.20 |
| units__kelvin_gets_degree_sign | 0.60 | 0.40 | 0.40 | 0.60 |
| units__malformed_not_checked | 0.60 | 0.00 | 0.00 | 0.40 |
| units__to_swaps_units | 0.20 | 0.00 | 0.40 | 0.20 |
| url_router__build_skips_param_check | 1.00 | 0.20 | 0.40 | 1.00 |
| user_registry__deactivated_user_can_act | 0.00 | 0.20 | 0.00 | 0.20 |
| user_registry__hash_argument_order | 0.40 | 0.20 | 0.20 | 0.40 |
| user_registry__min_length_off_by_one | 0.80 | 0.00 | 0.00 | 0.80 |
| user_registry__username_in_password_case_sensitive | 0.80 | 0.80 | 0.80 | 1.00 |
