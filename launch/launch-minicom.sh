#!/bin/bash
set -e

LOG_DIRECTORY="../test-logs"

config_name=${1}
selected_main=${2}

if [ -z "$config_name" ]
then
    echo "Configuration was not set..."
    exit 1
fi

# Format [config name]-[date]-[version number].log
log_date=$(date +%y-%m-%d)
version_number=1
log_file="$LOG_DIRECTORY/$config_name-$selected_main-$log_date-$version_number.log"

# If version number already exists then increment version
while [ -f "$log_file" ]
do
    version_number=$((version_number+1))
    log_file="$LOG_DIRECTORY/$config_name-$selected_main-$log_date-$version_number.log"
done


# Minicom command for logging with serial
sudo minicom --device /dev/ttyUSB0 -C "$log_file"