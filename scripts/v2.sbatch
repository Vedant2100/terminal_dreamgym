#!/usr/bin/env bash
# Benchmark v2 (docs/benchmark_v2_protocol.md) on one RTX 6000 Ada.
# Usage:
#   sbatch scripts/v2.sbatch calibrate <out.jsonl> <seeds> [extra matched-eval args...]
#   sbatch scripts/v2.sbatch evaluate  <out.jsonl> <seeds> [extra matched-eval args...]
# `calibrate` runs no_skill on data/tasks_v2.json; `evaluate` writes the 30B skills
# (skills/strong_written_v2, or $V2_SKILLS) and runs the four conditions.
# Build the task list first (`cli build-v2`, then `--keep` for evaluation).
#SBATCH --job-name=fm-serial
#SBATCH --dependency=singleton
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --time=24:00:00
#SBATCH --output=logs/v2-%j.out

set -euo pipefail
REPO="${REPO:-$HOME/terminal_dreamgym}"
OLLAMA_SIF="${OLLAMA_SIF:-$HOME/frontiermemory-experiment-20261024/containers/ollama.sif}"
MODEL_STORE="${MODEL_STORE:-$HOME/shared-mem-gov-pilot/models}"
PORT="${PORT:-11500}"
WRITER="${WRITER:-qwen3-coder:30b}"
V2_SKILLS="${V2_SKILLS:-skills/strong_written_v2}"
STAGE="${1:?stage required}"; OUT="${2:?output jsonl required}"; SEEDS="${3:?seeds required}"; shift 3
cd "$REPO"
mkdir -p logs

apptainer exec --fakeroot --nv --bind "${MODEL_STORE}:/models" \
  --env OLLAMA_MODELS=/models --env OLLAMA_HOST=127.0.0.1:${PORT} \
  --env OLLAMA_CONTEXT_LENGTH=16384 --env OLLAMA_NUM_PARALLEL=4 \
  "$OLLAMA_SIF" ollama serve > "logs/ollama-v2-${SLURM_JOB_ID}.log" 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null || true; wait $SERVER_PID 2>/dev/null || true' EXIT

for _ in $(seq 1 90); do
  curl --fail --silent "http://127.0.0.1:${PORT}/api/tags" >/dev/null && break
  sleep 2
done
curl --fail --silent "http://127.0.0.1:${PORT}/api/tags" | grep -q '"qwen2.5:7b"'
nvidia-smi -L
git rev-parse HEAD
sha256sum data/tasks_v2.json

export QWEN_BASE_URL="http://127.0.0.1:${PORT}/v1" QWEN_MODEL=qwen2.5:7b
export TERMINAL_DREAMGYM_TEMPERATURE=0.7 TERMINAL_DREAMGYM_MAX_STEPS=3 TERMINAL_DREAMGYM_MAX_OUTPUT_TOKENS=2048
case "$STAGE" in
  calibrate)
    .venv/bin/python -m terminal_dreamgym.cli matched-eval --mode qwen --tasks-file data/tasks_v2.json \
      --out "$OUT" --seeds "$SEEDS" --conditions no_skill --concurrency 4 "$@"
    ;;
  evaluate)
    curl --fail --silent "http://127.0.0.1:${PORT}/api/tags" | grep -q "\"${WRITER}\""
    curl --fail --silent --max-time 1200 "http://127.0.0.1:${PORT}/api/generate" \
      -d "{\"model\": \"${WRITER}\", \"prompt\": \"\", \"keep_alive\": \"30m\"}" >/dev/null
    .venv/bin/python -m terminal_dreamgym.cli write-skills --mode qwen --writer-model "$WRITER" --families all \
      --source runs/matched_eval.jsonl --out-dir "$V2_SKILLS" --seeds "$SEEDS"
    curl --silent "http://127.0.0.1:${PORT}/api/generate" -d "{\"model\": \"${WRITER}\", \"keep_alive\": 0}" >/dev/null || true
    .venv/bin/python -m terminal_dreamgym.cli matched-eval --mode qwen --tasks-file data/tasks_v2.json \
      --out "$OUT" --seeds "$SEEDS" --strong-skills-dir "$V2_SKILLS" --skill-scope all \
      --conditions no_skill,handwritten_skills,strong_skill,placebo --concurrency 4 "$@"
    ;;
  *) echo "unknown stage $STAGE" >&2; exit 2 ;;
esac
