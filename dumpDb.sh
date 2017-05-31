
BACKUP=db/backups/$(date +%F--%T) 
mkdir $BACKUP
mongodump --out $BACKUP
