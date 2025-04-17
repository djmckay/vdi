# Deploy the infrastructure
cd lambda
./deploy.sh
#pip install --platform manylinux2014_x86_64 --only-binary=:all: psycopg2-binary -t lambda/
cd ../
  cdk bootstrap
  cdk deploy --outputs-file target/output.json

  # Execute the DB Setup function to create the table
  lambda_result=$(aws lambda invoke --function-name $(cat target/output.json | jq -r '.DisneyStack.DbSetupArn') /dev/stdout 2>&1)
  # Extract the status code from the response payload
  lambda_status_code=$(echo "$lambda_result" | jq 'first(.. | objects | select(has("statusCode"))) | .statusCode')

  if [ "$lambda_status_code" == "200" ]; then
      echo "DB Setup Lambda function executed successfully"
      cd ../../
#      export SPRING_DATASOURCE_PASSWORD=$(aws secretsmanager get-secret-value --secret-id AuroraClusterCredentials | jq --raw-output '.SecretString' | jq -r .password)
#      export SPRING_DATASOURCE_URL=jdbc:postgresql://$(aws rds describe-db-instances --db-instance-identifier unicornInstance --query "DBInstances[*].Endpoint.Address" | jq -r ".[]"):5432/unicorns
#      echo $SPRING_DATASOURCE_URL
#      export AWS_REGION=$(aws configure get region)

  else
      echo "DB Setup Lambda function execution failed"
      exit 1
  fi

