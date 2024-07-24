#!/bin/bash

function write_red() {
    printf "\033[0;31m%s\033[0m\n" "${1}"
}

function write_yellow() {
    printf "\033[0;33m%s\033[0m\n" "${1}"
}

# List all files with a size >25Mo, compress them with bzip2
readarray -t files_to_compress < <(find . -type f -size +25M -and -name "*.log")

for log_file in "${files_to_compress[@]}"
do
    archive_file=${log_file::-4}'.tar.bz2'
    if [[ -f "$archive_file" ]]
    then
        echo "Archive already exists for ${log_file}!"
        echo 'Skip!'
        echo
    else
        file_size=$(du -hs "$log_file" | cut -f1)
        echo "Generating archive: ${archive_file}... (original size: ${file_size})"
        tar -jcf "${archive_file}" "${log_file}"
        archive_size=$(du -hs "$archive_file" | cut -f1)
        echo 'Adding to .gitignore...'
        echo "${log_file}" >> ./.gitignore
        echo "Done! (final size: ${archive_size})"
        archive_size=${archive_size::-1}
        last_char=${archive_size:-1}
        if [[ $archive_size -gt 100 && "${last_char}" == "M" ]]
        then
            write_red 'Archive bigger than 100MB, Github will refuse it! Consider putting it in the .gitignore file'
        elif [[ $archive_size -gt 50 && "${last_char}" == "M" ]]
        then
            write_yellow 'Archive is bigger than 50MB, Github will allow it but this is really big...'
        fi

        echo
    fi 
done