#!/bin/bash

# This script is intended to be run via `make app APP_NAME=<app_name> VERSION=<version>`

if [ -z "$VERSION" ]
then
  VERSION=DEVELOPMENT
fi

if [ -z "$APP_NAME" ]
then
  echo "No APP_NAME specified!" >&2
  exit 1
fi

APP_DIR="notectl/plugins/$APP_NAME"
if [ ! -d $APP_DIR ]
then
  echo "No plugin found at $APP_DIR for \"$APP_NAME\"!" >&2
  exit 1
fi

PACKAGE_NAME="${APP_NAME}v${VERSION}"
ZIP_TARGET="${PACKAGE_NAME}.tar.gz"

echo "Building ${PACKAGE_NAME}..."
tar -czvf "${ZIP_TARGET}" notectl/plugins/$APP_NAME
# TODO upload new file to registry
# TODO register version with registry
rm "${ZIP_TARGET}"
