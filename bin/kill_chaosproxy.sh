#!/bin/bash

ps -ef | grep chaosproxy | grep -v grep | awk '{print $2}' | xargs kill -9
