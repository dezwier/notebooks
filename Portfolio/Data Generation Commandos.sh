
# CHECK CONFIGURATION
cd ~/git/lily-demo/financial/schemas
mvn clean install

# MASTER MERGE
git checkout master
git pull
git checkout DemoCarLoanUseCase2
git merge master


# DEPLOY
cd ~/git/lily-demo/financial/deploy/financial_interactive_staging_v2
fab upload_config apply_config upload_scripts

# GENERATE AND LOAD DATA
ssh financial-interactive-staging-v201
screen -r Desiré

/usr/lib/lily-demo/staging/scripts/data-generate-customers.py -n 50000 -o /disk1/current/ -m /usr/lib/lily-demo/staging/scripts/data-generate-model/
/usr/lib/lily-demo/staging/scripts/data-generate-productsv2.py  -o /disk1/current/ -m /usr/lib/lily-demo/staging/scripts/data-generate-model -c /disk1/current/CrmDataToFilter.csv 
/usr/lib/lily-demo/staging/scripts/data-generate-account.py  -o /disk1/current/ -m /usr/lib/lily-demo/staging/scripts/data-generate-model -c /disk1/current/EntityDataAll.csv 
/usr/lib/lily-demo/staging/scripts/data-generate-account_role.py  -o /disk1/current/ -m /usr/lib/lily-demo/staging/scripts/data-generate-model -c /disk1/current/EntityDataAll.csv 
/usr/lib/lily-demo/staging/scripts/data-generate-itxv3.py -n 6 -o /disk1/current -m /usr/lib/lily-demo/staging/scripts/data-generate-model/

/usr/lib/lily-demo/staging/scripts/data-load-customers.sh   /disk1/current/CrmDataToLoad.csv 
/usr/lib/lily-demo/staging/scripts/data-load-products.sh /disk1/current/EntityDataToLoad.csv
/usr/lib/lily-demo/staging/scripts/data-load-account.sh  /disk1/current/AccountData.csv 
/usr/lib/lily-demo/staging/scripts/data-load-account_role.sh /disk1/current/AccountRoleData.csv
/usr/lib/lily-demo/staging/scripts/data-reload-itx.sh /disk1/current

# CHECK CSV ON CLUSTER
ssh financial-interactive-staging-v201
less /disk1/current/EntityDataAll.csv
scp financial-interactive-staging-v201:/disk1/current/EntityDataAll.csv /Users/desiredewaele/Desktop/

# BATCH CALC
lily dna-entity-batch-calc --dna-entity-type customer_crm --start-date 2015-12-31
lily master-batch-update-factual --dna-entity-type customer 
lily set-membership-calc --dna-entity-type customer --start-date 2015-12-31
lily dna-set-batch-calc --dna-entity-type customer --start-date 2015-12-31

# SHOW LOGFILE
ssh financial-interactive-staging-v201
cd /var/log/lily-demo
cat data-batch-calc.log

# LOCATIES
Bash script: ~/git/lily-demo/financial/deploy/sandbox/
Metrieken:   ~/git/lily-demo/financial/schemas/src/main/resources/dna/campaigndna
Revised XML:   cd ~/git/lily-demo/financial/schemas/src/main/resources/dna/customer/definition
Scripts: cd ~/git/lily-demo/financial/schemas/src/main/resources/scripts
Create Data persona: cd ~/git/lily-demo/financial/schemas/src/main/resources/scripts

# PHOENIX QUERIES
ssh financial-interactive-staging-v201
lily sql-phoenix0
select customer_id, category, margin from customer_product where customer_id = 6;

# JOB KILLEN
ssh financial-interactive-staging-v201
mapred job -kill job_1489733729094_1612

# LILY DOWN
ssh financial-interactive-staging-v201
sudo service lily-rest status
sudo service lily-rest start

# DASHBOARD DELEN
!outputformat vertical
select * from lily.settings;