# Matched-condition evaluation

Model qwen2.5:7b; temperature [0.7]; up to [3] model attempts per task for every condition; seeds [1, 2, 3].

Success is strict: the target test passes and no test that passed before the edit fails afterwards.
Base tasks excluded because their target test passes before any edit: python_price_currency_spacing.

## Success rates

| Condition | Runs | Strict success | Target test only | First attempt | Train | Held-out | Adversarial | Passed but regressed | Mean calls | Unparseable replies |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_skill | 300 | 0.512 | 0.537 | 0.284 | 0.717 | 0.453 | 0.289 | 7 | 2.12 | 27.2% |
| handwritten_skills | 300 | 0.572 | 0.621 | 0.291 | 0.658 | 0.600 | 0.433 | 14 | 2.06 | 11.2% |
| placebo | 300 | 0.530 | 0.533 | 0.253 | 0.683 | 0.413 | 0.422 | 1 | 2.19 | 32.0% |
| symptom_patch | 300 | 0.442 | 0.446 | 0.217 | 0.625 | 0.400 | 0.233 | 1 | 2.29 | 39.0% |

## Paired differences

Mean over base tasks of (A − B), 95% bootstrap CI resampling base tasks; better/worse/tied counts are base tasks.

| A − B | Strict success | Better / worse / tied | First attempt | Target test only | Train | Held-out | Adversarial |
| --- | --- | --- | --- | --- | --- | --- | --- |
| handwritten_skills − no_skill (primary) | +0.060 [-0.028, +0.151] | 6 / 4 / 9 | +0.007 [-0.067, +0.095] | +0.084 [-0.014, +0.182] | -0.058 [-0.150, +0.008] | +0.147 [-0.053, +0.373] | +0.144 [+0.044, +0.256] |
| handwritten_skills − placebo | +0.042 [-0.049, +0.147] | 7 / 5 / 7 | +0.039 [-0.046, +0.130] | +0.088 [-0.032, +0.217] | -0.025 [-0.158, +0.100] | +0.187 [-0.053, +0.480] | +0.011 [-0.022, +0.044] |
| placebo − no_skill | +0.018 [-0.039, +0.077] | 5 / 4 / 10 | -0.032 [-0.095, +0.032] | -0.004 [-0.063, +0.060] | -0.033 [-0.100, +0.025] | -0.040 [-0.120, +0.000] | +0.133 [+0.033, +0.244] |
| symptom_patch − no_skill | -0.070 [-0.179, +0.025] | 5 / 5 / 9 | -0.067 [-0.175, +0.028] | -0.091 [-0.200, +0.004] | -0.092 [-0.267, +0.042] | -0.053 [-0.160, +0.027] | -0.056 [-0.311, +0.122] |

## By task family (sensitivity)

Base tasks within a family share one repository, so they are not fully independent. Mean (A − B) per family, no interval (only four families):

| A − B | cli_edge_case | config_env_failure | dependency_mismatch | python_test_failure |
| --- | ---: | ---: | ---: | ---: |
| handwritten_skills - no_skill | +0.000 | +0.080 | -0.100 | +0.227 |
| handwritten_skills - placebo | +0.013 | +0.027 | -0.133 | +0.227 |
| placebo - no_skill | -0.013 | +0.053 | +0.033 | +0.000 |
| symptom_patch - no_skill | +0.000 | +0.053 | +0.033 | -0.347 |

## Per base task (strict success, all variants and seeds)

| Base task | no_skill | handwritten_skills | placebo | symptom_patch |
| --- | ---: | ---: | ---: | ---: |
| cli_empty_input | 0.00 | 0.00 | 0.00 | 0.00 |
| cli_invalid_input_nonzero | 0.00 | 0.00 | 0.00 | 0.00 |
| cli_json_error_valid | 0.00 | 0.00 | 0.00 | 0.00 |
| cli_json_flag | 1.00 | 1.00 | 0.93 | 1.00 |
| cli_missing_file_error | 0.00 | 0.00 | 0.00 | 0.00 |
| config_missing_optional_region | 1.00 | 1.00 | 1.00 | 1.00 |
| config_missing_required_api_key | 0.07 | 0.40 | 0.33 | 0.27 |
| config_nested_auth_token | 0.07 | 0.40 | 0.07 | 0.07 |
| config_request_timeout_type | 0.87 | 0.73 | 0.87 | 0.93 |
| config_timeout_key | 1.00 | 0.87 | 1.00 | 1.00 |
| dependency_format_order_signature | 1.00 | 1.00 | 1.00 | 0.93 |
| dependency_format_user_signature | 0.73 | 0.40 | 0.80 | 0.87 |
| dependency_no_global_adapter_break | 1.00 | 1.00 | 1.00 | 1.00 |
| dependency_parse_result_shape | 0.73 | 0.67 | 0.80 | 0.80 |
| python_email_preserve_plus_tag | 0.00 | 0.27 | 0.20 | 0.13 |
| python_email_whitespace | 0.33 | 0.40 | 0.13 | 0.00 |
| python_price_comma | 0.93 | 0.93 | 0.80 | 0.33 |
| python_price_currency_spacing | 1.00 | 1.00 | 1.00 | 1.00 |
| python_sku_preserve_comma | 0.67 | 0.93 | 1.00 | 0.00 |
| python_slug_punctuation | 0.33 | 0.87 | 0.13 | 0.07 |
