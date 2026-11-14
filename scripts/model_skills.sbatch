#!/usr/bin/env bash
# Model-written skills on one GPU (docs/model_skills_protocol.md): write skills, then evaluate.
# Usage: sbatch scripts/model_skills.sbatch <skills_dir> <out.jsonl> <seeds> [extra matched-eval args...]
# Paths below are for the UCR csgrad cluster; override with env vars elsewhere.
#SBATCH --job-name=fm-serial
#SBATCH --dependency=singleton
#SBATCH --partition=batch
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/model-skills-%j.out

set -euo pipefail
REPO="${REPO:-$HOME/terminal_dreamgym}"
OLLAMA_SIF="${OLLAMA_SIF:-$HOME/frontiermemory-experiment-20261024/containers/ollama.sif}"
MODEL_STORE="${MODEL_STORE:-$HOME/shared-mem-gov-pilot/models}"
PORT="${PORT:-11500}"
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
nvidia-smi -L
git rev-parse HEAD

export QWEN_BASE_URL="http://127.0.0.1:${PORT}/v1" QWEN_MODEL=qwen2.5:7b
export TERMINAL_DREAMGYM_TEMPERATURE=0.7 TERMINAL_DREAMGYM_MAX_STEPS=3 TERMINAL_DREAMGYM_MAX_OUTPUT_TOKENS=2048
.venv/bin/python -m terminal_dreamgym.cli write-skills --mode qwen --source runs/matched_eval.jsonl --out-dir "$SKILLS" --seeds "$SEEDS"
.venv/bin/python -m terminal_dreamgym.cli matched-eval --mode qwen --out "$OUT" --seeds "$SEEDS" --skills-dir "$SKILLS" \
  --conditions no_skill,model_skill,handwritten_skills,placebo --concurrency 4 "$@"
