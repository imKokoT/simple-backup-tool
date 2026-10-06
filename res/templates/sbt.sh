#!/bin/bash
APP_DIR="{app_dir}"
APP_PATH="{app_path}"

cd "$APP_DIR" || exit 1
exec "$APP_PATH" "$@"
