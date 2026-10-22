#!/usr/bin/env bash
# Static slots versus dynamic (model-chosen) grouping, on the persona harness, for several interview models.
#   bash experiments/run_interview_modes.sh [runs]
# Each configuration starts its own web server on port 8092 with its own session folder, plays every persona
# through it, and writes experiments/out/task-i-<stamp>-<tag>.md. The persona player is the local gemma4:12b
# for the Gemini configurations (no quota spent on role-play) and the interview model itself for the local ones.
set -e
cd "$(dirname "$0")/.."
RUNS="${1:-1}"
run_cfg() {   # tag  INTERVIEW_MODE  LLM_BACKEND  OLLAMA_MODEL(for server)  persona OLLAMA_MODEL
  local tag="$1" mode="$2" backend="$3" smodel="$4" pmodel="$5"
  local dir="$PWD/experiments/out/sessions-$tag"; mkdir -p "$dir"
  echo "== $tag  (mode=$mode backend=$backend model=$smodel; persona=$pmodel)"
  INTERVIEW_MODE="$mode" LLM_BACKEND="$backend" OLLAMA_MODEL="$smodel" WEBAPP_PORT=8092 SESSIONS_DIR="$dir" \
    setsid nohup .venv/bin/python webapp/server.py > "$dir/server.log" 2>&1 &
  sleep 4
  SESSIONS_DIR="$dir" LLM_BACKEND=ollama OLLAMA_MODEL="$pmodel" \
    .venv/bin/python experiments/task_i_harness.py --host http://127.0.0.1:8092 --runs "$RUNS" --tag "$tag" 2>&1 | tail -12
  local pid; pid=$(ss -ltnp | grep ':8092 ' | grep -oE 'pid=[0-9]+' | head -1 | cut -d= -f2); [ -n "$pid" ] && kill "$pid"; sleep 2
}
run_cfg static-gemma4   static  ollama gemma4:12b  gemma4:12b
run_cfg dynamic-gemma4  dynamic ollama gemma4:12b  gemma4:12b
run_cfg static-qwen35   static  ollama qwen3.5:9b  qwen3.5:9b
run_cfg dynamic-qwen35  dynamic ollama qwen3.5:9b  qwen3.5:9b
run_cfg static-gemini   static  gemini gemma4:12b  gemma4:12b
run_cfg dynamic-gemini  dynamic gemini gemma4:12b  gemma4:12b
echo "all configurations done"
