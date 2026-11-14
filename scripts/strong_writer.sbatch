#!/usr/bin/env bash
# Skills written by a larger model, then evaluated (docs/strong_writer_protocol.md). One RTX 6000 Ada (48 GB): the writer needs ~19 GB.
# Usage: sbatch scripts/strong_writer.sbatch <strong_skills_dir> <out.jsonl> <seeds> [extra matched-eval args...]
# Paths below are for the UCR csgrad cluster; override with env vars elsewhere.
#SBATCH --job-name=fm-serial
#SBATCH --dependency=singleton
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/strong-writer-%j.out

set -euo pipefail
REPO="${REPO:-$HOME/terminal_dreamgym}"
OLLAMA_SIF="${OLLAMA_SIF:-$HOME/frontiermemory-experiment-20261024/containers/ollama.sif}"
MODEL_STORE="${MODEL_STORE:-$HOME/shared-mem-gov-pilot/models}"
PORT="${PORT:-11500}"
WRITER="${WRITER:-qwen3-coder:30b}"
WEAK_SKILLS="${WEAK_SKILLS:-skills/model_written}"
SKILLS="${1:?skills dir required}"; OUT="${2:?output jsonl required}"; SEEDS="${3:?seeds required}"; shift 3
cd "$REPO"
mkdir -p logs

apptainer exec --fakeroot --nv --bind "${MODEL_STORE}:/models" \
  --env OLLAMA_MODELS=/models --env OLLAMA_HOST=127.0.0.1:${PORT} \
  --env OLLAMA_CONTEXT_LENGTH=16384 --env OLLAMA_NUM_PARALLEL=4 \
  "$OLLAMA_SIF" ollama serve > "logs/ollama-matched-${SLURM_JOB_ID}.log" 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null || true; wait $SERVER_PID 2>/dev/null || true' EXIT

for _ in $(seq 1 90); do
  curl --fail --silent "http://127.0.0.1:${PORT}/api/tags" >/dev/null && break
  sleep 2
done
apptainer exec --fakeroot --bind "${MODEL_STORE}:/models" --env OLLAMA_MODELS=/models \
  --env OLLAMA_HOST=127.0.0.1:${PORT} "$OLLAMA_SIF" ollama pull qwen2.5:7b
curl --fail --silent "http://127.0.0.1:${PORT}/api/tags" | grep -q '"qwen2.5:7b"'
curl --fail --silent "http://127.0.0.1:${PORT}/api/tags" | grep -q "\"${WRITER}\""
nvidia-smi -L
# Load the writer before the first timed call (cold load from network storage is slow).
curl --fail --silent --max-time 1200 "http://127.0.0.1:${PORT}/api/generate" -d "{\"model\": \"${WRITER}\", \"prompt\": \"\", \"keep_alive\": \"30m\"}" >/dev/null
git rev-parse HEAD

export QWEN_BASE_URL="http://127.0.0.1:${PORT}/v1" QWEN_MODEL=qwen2.5:7b
export TERMINAL_DREAMGYM_TEMPERATURE=0.7 TERMINAL_DREAMGYM_MAX_STEPS=3 TERMINAL_DREAMGYM_MAX_OUTPUT_TOKENS=2048
.venv/bin/python -m terminal_dreamgym.cli write-skills --mode qwen --writer-model "$WRITER" \
  --source runs/matched_eval.jsonl --out-dir "$SKILLS" --seeds "$SEEDS"
# Free the writer's memory before the solver runs.
curl --silent "http://127.0.0.1:${PORT}/api/generate" -d "{\"model\": \"${WRITER}\", \"keep_alive\": 0}" >/dev/null || true
.venv/bin/python -m terminal_dreamgym.cli matched-eval --mode qwen --out "$OUT" --seeds "$SEEDS" \
  --skills-dir "$WEAK_SKILLS" --strong-skills-dir "$SKILLS" \
  --conditions no_skill,strong_skill,model_skill,placebo --concurrency 4 "$@"
