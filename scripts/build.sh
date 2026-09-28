#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
python3 scripts/fetch_dependencies.py
export PI_PROFILE="$ROOT/profile.yaml"
: "${ANDROID_HOME:?Set ANDROID_HOME to your Android SDK}"
: "${JAVA_HOME:?Set JAVA_HOME to JDK 17 or newer}"
python3 vendor/MaaFwApp/scripts/setup_maa_framework.py --tag v5.14.1 --abi arm64-v8a
printf 'sdk.dir=%s\nbuild.debugAbi=arm64-v8a\nbuild.releaseAbi=arm64-v8a\n' "$ANDROID_HOME" > vendor/MaaFwApp/local.properties
cd vendor/MaaFwApp
./gradlew :app:assembleDebug --console=plain
mkdir -p "$ROOT/artifacts"
cp app/build/outputs/apk/debug/*.apk "$ROOT/artifacts/diandao-experimental-debug.apk"
