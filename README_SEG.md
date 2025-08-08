# Segregation Steps for Disturbance

# Step 1: export disturbance tables and reversion schema from ledger
### EXCLUDE Reversion and add schema only for reversion
NOTE: normally for PROD you would not exclude the reversion tables as in the command below. But for DEV work, these can be excluded to speed up DB backup and restore.
```

Run pg_dump on the ledger database.

`pg_dump -U ledger_prod -W --exclude-table='django_cron*' --exclude-table='reversion_revision' --exclude-table='reversion_version' -t 'disturbance_*' -t 'taggit_*' -t 'accounts_*' -t 'address_*' -t 'analytics_*' -t 'auth_*' -t 'django_*' ledger_prod -h <db_hostname> -p 5432 > /dbdumps/dumps/das_seg_tables_DDMMYYYY.sql

### Append empty reversion tables
`pg_dump -U ledger_prod -W --schema-only -t reversion_revision -t reversion_version ledger_prod -h <db_hostname> -p 5432 >> /dbdumps/dumps/reversion_schema_das_seg_tables_DDMMYYYY.sql
```

# Step 2: create new disturbance database

As a postgres admin user (`su postgres` then `psql`) create the new disturbance database.
```

`CREATE DATABASE das_dev;`

`CREATE USER das_dev WITH PASSWORD 'password';`

`GRANT ALL ON DATABASE das_dev to das_dev;`

`\c das_dev`

`create extension postgis;`

`GRANT ALL ON ALL TABLES IN SCHEMA public TO das_dev;`

`GRANT ALL ON SCHEMA public TO das_dev;`
```

# Step 3: to restore exported tables in to new DB disturbance
```
psql -U das_dev das_dev -h localhost -W <  das_seg_tables_DDMMYYYY.sql

psql -U das_dev das_dev -h localhost -W <  reversion_schema_das_seg_tables_DDMMYYYY.sql
```

# Step 4: Update environment variable with new database url (and other variables)

Update the environment variables:

- DATABASE_URL=postgis://das_dev:<passwd>@172.17.0.1:5432/das_seg_dev
- ENABLE_DJANGO_LOGIN=True

# Step 5: delete the migrations for app django_cron
```
./manage_ds.py dbshell

delete from django_migrations where app = 'django_cron';
```

# Step 6: Run all other migrations
```
./manage_ds.py migrate disturbance
./manage_ds.py migrate
```

# Step 7: Delete the Apiary Proposal Types

<!-- delete the Apiary proposal type in Admin (via Django Admin) - those with blank application_name (and v1) OR -->
```
./manage_ds.py shell_plus

apiary_proposal_types=['Apiary','Site Transfer','Temporary Use']
ProposalType.objects.filter(name__in=apiary_proposal_types).delete()
```

