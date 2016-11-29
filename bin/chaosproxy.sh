#!/bin/bash

set -e

THIS=`basename $0`
CONFIG_FILE=$1
DOWNLOAD=$2
LOG_FILE_PATH="."
CHAOS_PROXY_ZIP="chaosproxy.zip"
CHAOS_PROXY_DIR="chaosproxy-master"
CHAOS_PROXY_REMOTE="https://codeload.github.com/mcmartins/chaosproxy/zip/master"

if [[ "${DOWNLOAD}" == "false" ]]; then
    echo "Using local version of ChaosProxy..."
else
    echo "Removing installed version of ChaosProxy from: ${CHAOS_PROXY_DIR}..."
    rm -rf ${CHAOS_PROXY_DIR}
    echo "Downloading latest version of ChaosProxy from: ${CHAOS_PROXY_REMOTE}..."
    curl -so ${CHAOS_PROXY_ZIP} ${CHAOS_PROXY_REMOTE} > /dev/null
    echo "ChaosProxy download finished."
	echo "Installing ChaosProxy..."
	unzip ${CHAOS_PROXY_ZIP}
	rm ${CHAOS_PROXY_ZIP}
	cd ${CHAOS_PROXY_DIR}
	sudo python2 setup.py clean build install
	echo "ChaosProxy installation finished."
	cd ..
fi

echo "Starting ChaosProxy using the following configuration file: ${CONFIG_FILE}..."

python2 -m chaosproxy.__main__ -v -i ${CONFIG_FILE} -p ${LOG_FILE_PATH} &>/dev/null

echo "Log file path is: '${LOG_FILE_PATH}'"
