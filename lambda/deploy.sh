#!/bin/bash

#### Script that builds the lambda zip file

# Delete the lambda_deploy folder if exists
rm -rf lambda_deploy_db
rm -rf lambda_deploy_sf

# Create new lambda_deploy folder
mkdir lambda_deploy_db
mkdir lambda_deploy_sf

# Install psycopg2 libraries in the lambda_deploy folder
python3 -m pip install -r requirements.txt -t lambda_deploy_db
python3 -m pip install -r requirements.txt -t lambda_deploy_sf

# Copy the lambda script into the lambda_deploy folder
cp db.py lambda_deploy_db
cd init_db
cp init_db.py ../lambda_deploy_db
cd ..

cp db.py lambda_deploy_sf
cd step_function
cp dedup_lambda.py ../lambda_deploy_sf
cp db_insert.py ../lambda_deploy_sf
cp create_ec2.py ../lambda_deploy_sf
cp dummy.py ../lambda_deploy_sf
cp jira_api.py ../lambda_deploy_sf
cd..

# Generate the zip file from the lambda_deploy folder
cd lambda_deploy_db
zip -r9 ../lambda_deploy_db.zip .
cd ..
rm -rf lambda_deploy_db

cd lambda_deploy_sf
zip -r9 ../lambda_deploy_sf.zip .
cd ..
rm -rf lambda_deploy_sf