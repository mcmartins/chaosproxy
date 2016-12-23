#!/bin/bash

set -e

this=`basename $0`
config_file=~/.conf_chaosproxy.json
log_file_path=~/
chaos_proxy_zip=chaosproxy.zip
chaos_proxy_dir=chaosproxy-master
chaos_proxy_remote=https://codeload.github.com/mcmartins/chaosproxy/zip/master

if [ ! -d "${chaos_proxy_dir}" ]; then
    echo "Downloading latest version of ChaosProxy from: '${chaos_proxy_remote}'"
    curl -so ${chaos_proxy_zip} ${chaos_proxy_remote} > /dev/null
    echo "ChaosProxy download finished... Installation directory is: '${chaos_proxy_dir}'"
	echo "Installing ChaosProxy"
	unzip ${chaos_proxy_zip}
	rm ${chaos_proxy_zip}
	cd ${chaos_proxy_dir}
	sudo python2 setup.py clean build install
	echo "ChaosProxy installation finished"
	cd ..
else
    echo "Using local version of ChaosProxy"
    echo "(If you want to update it, stop the server, delete the folder '${chaos_proxy_dir}' and start the server again)"
fi

echo "Starting ChaosProxy using the following configuration file: ${config_file}"

python2 -m chaosproxy.__main__ -v -i ${config_file} -p ${log_file_path} &>/dev/null &

echo "ChaosProxy Started... Log files path is: '${log_file_path}'"
