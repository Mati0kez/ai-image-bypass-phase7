#!/usr/bin/env bash
# 一键运行 Experiment 模式（使用 mock detector，快速演示）
set -e

SAMPLES=${1:-20}
OUT_DIR=${2:-experiment_demo}

echo ">>> Running experiment with ${SAMPLES} samples, output to ${OUT_DIR}"
PYTHONPATH=src benchmark \
  --mode=experiment \
  --platforms remote:mock \
  --samples "${SAMPLES}" \
  --output-dir "${OUT_DIR}"

echo ">>> Done. See ${OUT_DIR}/experiment_results.json and summary.md"
