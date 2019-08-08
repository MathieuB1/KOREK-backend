#!/bin/sh

db=postgres_korek_1
backup_folder=/tmp

container_db=$(docker ps | grep ${db} | awk '{print $NF}' | sed 's/ //g')

local_media=0

echo "### RESTORE KOREK ###"
if [[ $(docker volume ls | grep media) == "" ]]; then
	local_media=1
fi

echo "### LIST OF KOREK BACKUPS ###"
volume_to_save=korekbackend_pgdata
available_backups=$(docker run --rm -v ${volume_to_save}:/recover -v ${backup_folder}:/backup alpine sh -c 'cd /recover && \
file_cmd="ls -lrth /backup/korek* | grep '${volume_to_save}' | rev | cut -d \" \" -f1 | rev | cut -d "." -f1 | rev | cut -d "_" -f1 | rev" && \
echo $(eval "$file_cmd")')
echo $available_backups

# (1) prompt user, and read command line argument
read -p "Choose your backup date (eg: 19-08-01): "  restore_date
echo $restore_date
REGEX_DATE='^\d{2}[/-]\d{2}[/-]\d{2}$'
echo $restore_date | grep -P -q $REGEX_DATE

if [[ $? == 0 && $(echo $available_backups | grep $restore_date) != "" ]]; then

    echo "### STOPPING DB CONTAINER ###"
    echo "stopping database ${db}..." && \
    docker stop ${container_db}

    echo "### RESTORE VOLUMES ###"
    volume_to_save=korekbackend_pgdata
    docker run --rm -v ${volume_to_save}:/recover -v ${backup_folder}:/backup alpine sh -c 'cd /recover && \
    file_cmd="ls -lrth /backup/korek*${restore_date}* | grep '${volume_to_save}' | tail -1 | rev | cut -d \" \" -f1 | rev" && \
    file=$(eval "$file_cmd") && \
    cd /recover && rm -rf * && tar -xzvf $file && mv volume/* . && rm -fr volume'

    docker restart ${container_db}

    volume_to_save=korekbackend_media
    if [[ $local_media == 1 ]]; then
        echo "### RESTORE FOLDER ON HOST ###"
        docker run --rm -v $(pwd)/media:/recover -v ${backup_folder}:/backup alpine sh -c 'cd /recover && \
        file_cmd="ls -lrth /backup/korek*${restore_date}* | grep '${volume_to_save}' | tail -1 | rev | cut -d \" \" -f1 | rev" && \
        file=$(eval "$file_cmd") && \
        cd /recover && rm -rf * && tar -xzvf $file && mv volume/* . && rm -fr volume'
    else
        docker run --rm -v ${volume_to_save}:/recover -v ${backup_folder}:/backup alpine sh -c 'cd /recover && \
        file_cmd="ls -lrth /backup/korek*${restore_date}* | grep '${volume_to_save}' | tail -1 | rev | cut -d \" \" -f1 | rev" && \
        file=$(eval "$file_cmd") && \
        cd /recover && rm -rf * && tar -xzvf $file && mv volume/* . && rm -fr volume'
    fi
    echo "### KOREK HAS BEEN RESTORED ###"
else
    echo "WARNING: Backup date is invalid!"
    docker restart ${container_db}
fi