#!/bin/sh
db=postgres_korek_1
backup_folder=/tmp

date_bkp=$(date +"%y-%m-%d")
container_db=""

local_media=0

echo "### STOPPING DB CONTAINER ###"
echo "stopping database ${db}..." && \
container_db=$(docker ps | grep ${db} | awk '{print $NF}' | sed 's/ //g') && \
docker stop ${container_db}

if [[ $(docker volume ls | grep media) == "" ]]; then
	local_media=1
fi

echo "### CREATE KOREK BACKUP ###"
volume_to_save=korekbackend_pgdata
echo "saving ${volume_to_save}..."
# Save docker volume on host in /tmp
docker run --rm -v ${volume_to_save}:/volume -v ${backup_folder}:/backup alpine \
	sh -c "cd /backup/; tar -zvcf korek_${volume_to_save}_${date_bkp}.tar.gz /volume"

docker restart ${container_db}

volume_to_save=korekbackend_media
if [[ $local_media == 1 ]]; then
	echo "### BACKUP FOLDER FROM HOST ###"
	echo "saving ${volume_to_save}..."
	# Save docker volume on host in /tmp
	docker run --rm -v $(pwd)/media:/volume -v ${backup_folder}:/backup alpine \
		sh -c "cd /backup/; tar -zvcf korek_${volume_to_save}_${date_bkp}.tar.gz /volume"
else
	echo "saving ${volume_to_save}..."
	# Save docker volume on host in /tmp
	docker run --rm -v ${volume_to_save}:/volume -v ${backup_folder}:/backup alpine \
		sh -c "cd /backup/; tar -zvcf korek_${volume_to_save}_${date_bkp}.tar.gz /volume"
fi


echo "### BACKUP KOREK CREATED WITH DATE $date_bkp ###"
