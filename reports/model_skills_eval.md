# Matched-condition evaluation

Model qwen2.5:7b; temperature [0.7]; up to [3] model attempts per task for every condition; seeds [1, 2, 3, 4, 5].

Success is strict: the target test passes and no test that passed before the edit fails afterwards.
Base tasks excluded because their target test passes before any edit: python_price_currency_spacing.

## Success rates

| Condition | Runs | Strict success | Target test only | First attempt | Train | Held-out | Adversarial | Passed but regressed | Mean calls | Unparseable replies |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_skill | 500 | 0.558 | 0.579 | 0.290 | 0.730 | 0.480 | 0.393 | 10 | 2.08 | 24.2% |
| handwritten_skills | 500 | 0.575 | 0.608 | 0.299 | 0.645 | 0.616 | 0.447 | 16 | 2.05 | 12.1% |
| placebo | 500 | 0.537 | 0.549 | 0.194 | 0.700 | 0.512 | 0.340 | 6 | 2.22 | 30.6% |
| model_skill | 500 | 0.558 | 0.583 | 0.293 | 0.715 | 0.560 | 0.347 | 12 | 2.08 | 11.1% |

## Paired differences

Mean over base tasks of (A − B), 95% bootstrap CI resampling base tasks; better/worse/tied counts are base tasks.

| A − B | Strict success | Better / worse / tied | First attempt | Target test only | Train | Held-out | Adversarial |
| --- | --- | --- | --- | --- | --- | --- | --- |
| model_skill − no_skill (primary) | +0.000 [-0.088, +0.097] | 6 / 8 / 5 | +0.002 [-0.074, +0.072] | +0.004 [-0.086, +0.105] | -0.015 [-0.140, +0.135] | +0.080 [-0.080, +0.280] | -0.047 [-0.193, +0.093] |
| model_skill − handwritten_skills | -0.017 [-0.105, +0.059] | 6 / 7 / 6 | -0.006 [-0.101, +0.084] | -0.025 [-0.114, +0.053] | +0.070 [-0.055, +0.180] | -0.056 [-0.096, -0.016] | -0.100 [-0.287, +0.013] |
| model_skill − placebo | +0.021 [-0.088, +0.139] | 6 / 8 / 5 | +0.099 [+0.015, +0.187] | +0.034 [-0.080, +0.158] | +0.015 [-0.180, +0.220] | +0.048 [-0.120, +0.312] | +0.007 [-0.167, +0.160] |
| handwritten_skills − no_skill | +0.017 [-0.072, +0.114] | 7 / 7 / 5 | +0.008 [-0.093, +0.110] | +0.029 [-0.065, +0.133] | -0.085 [-0.195, +0.025] | +0.136 [-0.056, +0.352] | +0.053 [-0.067, +0.160] |

## By task family (sensitivity)

Base tasks within a family share one repository, so they are not fully independent. Mean (A − B) per family, no interval (only four families):

| A − B | cli_edge_case | config_env_failure | dependency_mismatch | python_test_failure |
| --- | ---: | ---: | ---: | ---: |
| model_skill - no_skill | -0.056 | -0.016 | -0.090 | +0.144 |
| model_skill - handwritten_skills | -0.008 | +0.008 | -0.020 | -0.048 |
| model_skill - placebo | -0.008 | -0.024 | -0.150 | +0.232 |
| handwritten_skills - no_skill | -0.048 | -0.024 | -0.070 | +0.192 |

## Per base task (strict success, all variants and seeds)

| Base task | no_skill | handwritten_skills | placebo | model_skill |
| --- | ---: | ---: | ---: | ---: |
| cli_empty_input | 0.04 | 0.00 | 0.00 | 0.08 |
| cli_invalid_input_nonzero | 0.00 | 0.00 | 0.00 | 0.00 |
| cli_json_error_valid | 0.20 | 0.00 | 0.00 | 0.00 |
| cli_json_flag | 1.00 | 1.00 | 1.00 | 0.88 |
| cli_missing_file_error | 0.00 | 0.00 | 0.00 | 0.00 |
| config_missing_optional_region | 1.00 | 1.00 | 1.00 | 1.00 |
| config_missing_required_api_key | 0.20 | 0.28 | 0.00 | 0.32 |
| config_nested_auth_token | 0.08 | 0.32 | 0.36 | 0.20 |
| config_request_timeout_type | 1.00 | 0.84 | 0.96 | 0.84 |
| config_timeout_key | 1.00 | 0.72 | 1.00 | 0.84 |
| dependency_format_order_signature | 0.96 | 1.00 | 0.96 | 0.92 |
| dependency_format_user_signature | 0.84 | 0.56 | 0.92 | 0.80 |
| dependency_no_global_adapter_break | 1.00 | 1.00 | 1.00 | 1.00 |
| dependency_parse_result_shape | 0.76 | 0.72 | 0.92 | 0.48 |
| python_email_preserve_plus_tag | 0.16 | 0.40 | 0.24 | 0.32 |
| python_email_whitespace | 0.20 | 0.40 | 0.08 | 0.64 |
| python_price_comma | 1.00 | 0.76 | 0.68 | 1.00 |
| python_price_currency_spacing | 1.00 | 1.00 | 1.00 | 1.00 |
| python_sku_preserve_comma | 0.80 | 1.00 | 0.80 | 0.44 |
| python_slug_punctuation | 0.36 | 0.92 | 0.28 | 0.84 |
