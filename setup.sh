#!/usr/bin/env bash
# Installs everything the engine needs. Safe to run repeatedly.
set -e
pip install skia-python kokoro-onnx soundfile numpy --break-system-packages -q 2>&1 | grep -vi warning || true
mkdir -p /tmp/kokoro
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s /tmp/kokoro/$f ] || curl -sSL -o /tmp/kokoro/$f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f
done
which ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
python3 -c "import skia, kokoro_onnx; print('setup ok')"
