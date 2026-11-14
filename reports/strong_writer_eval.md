# Matched-condition evaluation

Model qwen2.5:7b; temperature [0.7]; up to [3] model attempts per task for every condition; seeds [1, 2, 3, 4, 5].

Success is strict: the target test passes and no test that passed before the edit fails afterwards.
Base tasks excluded because their target test passes before any edit: python_price_currency_spacing.

## Success rates

| Condition | Runs | Strict success | Target test only | First attempt | Train | Held-out | Adversarial | Passed but regressed | Mean calls | Unparseable replies |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_skill | 500 | 0.568 | 0.590 | 0.312 | 0.720 | 0.512 | 0.413 | 10 | 2.06 | 23.1% |
| placebo | 500 | 0.571 | 0.579 | 0.217 | 0.750 | 0.528 | 0.367 | 4 | 2.18 | 27.9% |
| model_skill | 500 | 0.549 | 0.560 | 0.297 | 0.675 | 0.584 | 0.353 | 5 | 2.08 | 11.9% |
| strong_skill | 500 | 0.592 | 0.627 | 0.335 | 0.725 | 0.632 | 0.380 | 17 | 2.00 | 6.9% |

## Paired differences

Mean over base tasks of (A − B), 95% bootstrap CI resampling base tasks; better/worse/tied counts are base tasks.

| A − B | Strict success | Better / worse / tied | First attempt | Target test only | Train | Held-out | Adversarial |
| --- | --- | --- | --- | --- | --- | --- | --- |
| strong_skill − no_skill (primary) | +0.023 [-0.072, +0.118] | 8 / 4 / 7 | +0.023 [-0.078, +0.120] | +0.038 [-0.061, +0.139] | +0.005 [-0.095, +0.095] | +0.120 [-0.072, +0.328] | -0.033 [-0.240, +0.147] |
| strong_skill − model_skill | +0.042 [-0.008, +0.095] | 9 / 4 / 6 | +0.038 [-0.008, +0.093] | +0.067 [+0.006, +0.128] | +0.050 [-0.005, +0.110] | +0.048 [-0.072, +0.184] | +0.027 [-0.080, +0.140] |
| strong_skill − placebo | +0.021 [-0.082, +0.118] | 9 / 4 / 6 | +0.118 [+0.002, +0.232] | +0.048 [-0.072, +0.173] | -0.025 [-0.205, +0.095] | +0.104 [-0.064, +0.328] | +0.013 [-0.153, +0.167] |
| model_skill − no_skill | -0.019 [-0.084, +0.055] | 6 / 8 / 5 | -0.015 [-0.086, +0.057] | -0.029 [-0.095, +0.044] | -0.045 [-0.130, +0.025] | +0.072 [-0.040, +0.280] | -0.060 [-0.167, +0.027] |

## By task family (sensitivity)

Base tasks within a family share one repository, so they are not fully independent. Mean (A − B) per family, no interval (only four families):

| A − B | cli_edge_case | config_env_failure | dependency_mismatch | python_test_failure |
| --- | ---: | ---: | ---: | ---: |
| strong_skill - no_skill | -0.024 | +0.072 | +0.000 | +0.040 |
| strong_skill - model_skill | +0.016 | +0.104 | +0.070 | -0.016 |
| strong_skill - placebo | +0.000 | +0.040 | -0.110 | +0.128 |
| model_skill - no_skill | -0.040 | -0.032 | -0.070 | +0.056 |

## Per base task (strict success, all variants and seeds)

| Base task | no_skill | placebo | model_skill | strong_skill |
| --- | ---: | ---: | ---: | ---: |
| cli_empty_input | 0.00 | 0.00 | 0.08 | 0.04 |
| cli_invalid_input_nonzero | 0.00 | 0.00 | 0.00 | 0.00 |
| cli_json_error_valid | 0.16 | 0.04 | 0.00 | 0.00 |
| cli_json_flag | 1.00 | 1.00 | 0.88 | 1.00 |
| cli_missing_file_error | 0.00 | 0.00 | 0.00 | 0.00 |
| config_missing_optional_region | 0.96 | 1.00 | 0.96 | 1.00 |
| config_missing_required_api_key | 0.28 | 0.28 | 0.32 | 0.56 |
| config_nested_auth_token | 0.16 | 0.32 | 0.12 | 0.40 |
| config_request_timeout_type | 1.00 | 0.96 | 0.96 | 0.80 |
| config_timeout_key | 1.00 | 1.00 | 0.88 | 1.00 |
| dependency_format_order_signature | 0.96 | 0.92 | 0.92 | 1.00 |
| dependency_format_user_signature | 0.68 | 0.84 | 0.72 | 0.92 |
| dependency_no_global_adapter_break | 1.00 | 1.00 | 1.00 | 1.00 |
| dependency_parse_result_shape | 0.68 | 1.00 | 0.40 | 0.40 |
| python_email_preserve_plus_tag | 0.20 | 0.16 | 0.24 | 0.36 |
| python_email_whitespace | 0.44 | 0.24 | 0.48 | 0.44 |
| python_price_comma | 1.00 | 0.92 | 1.00 | 1.00 |
| python_price_currency_spacing | 1.00 | 1.00 | 1.00 | 1.00 |
| python_sku_preserve_comma | 0.84 | 0.72 | 0.56 | 0.36 |
| python_slug_punctuation | 0.44 | 0.44 | 0.92 | 0.96 |
