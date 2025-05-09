import json

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_apigateway as apigw,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_lambda as _lambda,
    aws_rds as rds,
    aws_secretsmanager as secrets,
    RemovalPolicy,
    aws_lambda_event_sources as event_sources,
    aws_logs as logs, custom_resources as cr, SecretValue
)
from aws_cdk.aws_stepfunctions import TaskInput, JsonPath
from aws_cdk.custom_resources import (
    AwsCustomResource,
    AwsCustomResourcePolicy,
    PhysicalResourceId,
    AwsSdkCall
)
from aws_cdk import Aws
from aws_cdk import Duration

from aws_cdk import CfnOutput
from aws_cdk import aws_stepfunctions as sfn, aws_stepfunctions_tasks as tasks

from constructs import Construct
import random
import string

from aws_cdk import aws_events as events
from aws_cdk import aws_pipes as pipes
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk.aws_iam import Role, ServicePrincipal, PolicyStatement

# Function to generate a random API Key
def generate_api_key(length=32):
    # testing TODO
    # this would need to be shared with the jira webhook creation
    return "hello world"
    # return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class DisneyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # stackName: str = "DisneyStack"
        stackShortNamePrefix = "DS_"
        queueName: str = stackShortNamePrefix+"Queue"
        apigwName: str = stackShortNamePrefix+"ApiGateway"
        db_name: str = stackShortNamePrefix+"AuroraDatabase"
        db_creds_name: str = stackShortNamePrefix+"AuroraClusterCredentials"
        vpcName: str = stackShortNamePrefix+"VPC"
        aurora_cluster_username: str = stackShortNamePrefix+"dbadmin"
        lambda_runtime = _lambda.Runtime.PYTHON_3_9
        
        # Create an SQS Queue
        queue = sqs.Queue(self, queueName)

        # Create the API GW service role with permissions to call SQS
#         rest_api_role = iam.Role(
#             self,
#             stackShortNamePrefix+"RestAPIRole",
#             assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
#             managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")]
#         )
#         queue.grant_send_messages(rest_api_role)
        # Create an API Gateway to receive Jira webhooks and send to SQS
        api = apigw.RestApi(self, apigwName)

        CfnOutput(
            self, "ApiEndpoint",
            value=api.url
        )

        api_key_value = generate_api_key()

        # Authorizer Lambda
        authorizer_lambda = _lambda.Function(
            self, "AuthLambda",
            runtime=lambda_runtime,
            handler="jira_authorizer.lambda_handler",
            code=_lambda.Code.from_asset("lambda/auth"),
        )

        # authorizer = apigw.TokenAuthorizer(
        #     self, "LambdaAuthorizer",
        #     handler=authorizer_lambda,
        #     identity_source="method.request.header.Authorization"
        # )

        send_to_sqs_lambda = _lambda.Function(
            self, "SendToSqsLambda",
            runtime=lambda_runtime,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda/send_to_sqs"),
            environment={
                "QUEUE_URL": queue.queue_url,
                "API_SECRET": api_key_value
            }
        )
        queue.grant_send_messages(send_to_sqs_lambda)

        # Store API Key in AWS Secrets Manager
        # Create an API Key Secret in Secrets Manager (Auto-generated)
        # Store API Key in AWS Secrets Manager
        # api_key_secret = secrets.Secret(
        #     self, "ApiKeySecret",
        #     secret_string_value=SecretValue(api_key_value)
        # )
        #
        # # Create an API Key in API Gateway
        # api_key = api.add_api_key(
        #     stackName+"MyApiKey",
        #     value=api_key_value  # Use the generated key
        # )
        #
        # # Create a Usage Plan (CDK v2 uses `apigateway.UsagePlan`)
        # usage_plan = apigw.UsagePlan(
        #     self, stackName+"MyUsagePlan",
        #     name="MyUsagePlan",
        #     api_stages=[
        #         apigw.UsagePlanPerApiStage(
        #             api=api,
        #             stage=api.deployment_stage
        #         )
        #     ],
        #     throttle=apigw.ThrottleSettings(
        #         rate_limit=10,  # 10 requests per second
        #         burst_limit=20
        #     )
        # )
        #
        # # Attach the API Key to the Usage Plan
        # usage_plan.add_api_key(api_key)

        # Require API Key for the POST method
        # api.root.add_method(
        #     "POST",
        #     apigw.AwsIntegration(
        #         service="sqs",
        #         path=f"{queue.queue_arn}",
        #         integration_http_method="POST",
        #         options=apigw.IntegrationOptions(
        #             credentials_role=rest_api_role,
        #             passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH
        #         )
        #     ),
        #     api_key_required=True  # ✅ CDK v2 API key requirement
        # )

        # integration = apigw.AwsIntegration(
        #     service="sqs",
        #     path=f"{Aws.ACCOUNT_ID}/{queue.queue_name}",
        #     integration_http_method="POST",
        #     options=apigw.IntegrationOptions(
        #         credentials_role=rest_api_role,
        #         request_parameters={
        #             "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
        #         },
        #         request_templates={
        #             "application/json": (
        #                 "Action=SendMessage&MessageBody=$util.urlEncode($input.body)"
        #             )
        #         },
        #         passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH
        #     )
        # )

        api.root.add_method("POST",
                            # integration,
                            apigw.LambdaIntegration(send_to_sqs_lambda),
                            # authorizer=authorizer,
                            authorization_type=apigw.AuthorizationType.NONE,
                            api_key_required=False  # ✅ CDK v2 API key requirement
                            )



        # api.root.add_method("POST", apigw.AwsIntegration(
        #     service="sqs",
        #     path=f"{queue.queue_arn}",
        #     integration_http_method="POST",
        #     options=apigw.IntegrationOptions(
        #         credentials_role=None,
        #         passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH
        #     )
        # ))

        ##
        ## Secret username/password for the cluster.
        ##


        aurora_cluster_secret = secrets.Secret(self, db_creds_name,
                                               secret_name=db_name + db_creds_name,
                                               description=db_name + "Aurora Cluster Credentials",
                                               generate_secret_string=secrets.SecretStringGenerator(
                                                   exclude_characters="\"@/\\ '",
                                                   generate_string_key="password",
                                                   password_length=30,
                                                   secret_string_template='{"username":"' + aurora_cluster_username + '"}'),
                                               )


        aurora_cluster_credentials = rds.Credentials.from_secret(aurora_cluster_secret, aurora_cluster_username)

        # db_secret = secrets.Secret(self, "DBSecret")
        vpc = ec2.Vpc(self, vpcName
    #                   ,
    # max_azs=2,
    # subnet_configuration=[
    #     ec2.SubnetConfiguration(
    #         name="PublicSubnet",
    #         subnet_type=ec2.SubnetType.PUBLIC,
    #         cidr_mask=24
    #     ),
    #     ec2.SubnetConfiguration(
    #         name="PrivateSubnet",
    #         subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
    #         cidr_mask=24
    #     )
    # ]
                      )


        # Create a Security Group for Aurora
        db_security_group = ec2.SecurityGroup(
            self, stackShortNamePrefix+"AuroraSecurityGroup",
            vpc=vpc,
            description="Allow Lambda access to Aurora"
        )

        # Create a Security Group for Lambda
        lambda_security_group = ec2.SecurityGroup(
            self, stackShortNamePrefix+"LambdaSecurityGroup",
            vpc=vpc,
            description="Lambda security group"
        )

        # Allow Lambda to access Aurora on PostgreSQL port 5432
        db_security_group.add_ingress_rule(
            lambda_security_group,
            ec2.Port.tcp(5432),
            "Allow Lambda access to Aurora"
        )
        db = rds.DatabaseCluster(
            self, db_name,
            engine=rds.DatabaseClusterEngine.aurora_postgres(version=rds.AuroraPostgresEngineVersion.VER_16_6),
            credentials=aurora_cluster_credentials,
            default_database_name=stackShortNamePrefix+"db",
            # instance_props={
            #     # "instance_type": ec2.InstanceType.of(
            #     #     ec2.InstanceClass.BURSTABLE4_GRAVITON, ec2.InstanceSize.MEDIUM
            #     # ),
            #     "vpc": vpc
            # },
            # instances=2,
            writer=rds.ClusterInstance.serverless_v2("WriterInstance"),
            readers=[
                rds.ClusterInstance.serverless_v2("ReaderInstance1"),
            ],
            vpc=vpc,
            enable_data_api=True,
            # serverless_v2_min_capacity=0.5,
            # serverless_v2_max_capacity=2,
            security_groups=[db_security_group]
        )

        # create layer
        # layer = _lambda.LayerVersion(self, 'helper_layer',
        #                              code=_lambda.Code.from_asset("layer"),
        #                              description='Common helper utility',
        #                              compatible_runtimes=[
        #                                  _lambda.Runtime.PYTHON_3_6,
        #                                  _lambda.Runtime.PYTHON_3_7,
        #                                  _lambda.Runtime.PYTHON_3_8,
        #                                  lambda_runtime
        #                              ],
        #                              removal_policy=RemovalPolicy.DESTROY
        #                              )

        # Create a Database Initialization Lambda Function
        # init_db_lambda = createLambda(self, stackShortNamePrefix+"InitDBLambda", vpc, "init_db.lambda_handler", 
        #                               "lambda/lambda_deploy_db.zip", [lambda_security_group], {
        #         "DB_SECRET": aurora_cluster_secret.secret_name
        #     })
        init_db_lambda = _lambda.Function(
            self, stackShortNamePrefix+"InitDBLambda",
            runtime=lambda_runtime,
            handler="init_db.lambda_handler",
            code=_lambda.Code.from_asset("lambda/lambda_deploy_db.zip"),
            # layers = [layer],
            vpc=vpc,
            security_groups=[lambda_security_group] , # Attach Lambda SG
            environment={
                "DB_SECRET": aurora_cluster_secret.secret_name
            }

        )
        aurora_cluster_secret.grant_read(init_db_lambda)

        CfnOutput(
            self, "DbSetupArn",
            value=init_db_lambda.function_arn
        )

        failed = sfn.Fail(self, "Failed", error="Failed")
        success = sfn.Succeed(self, "Success")
        skipped = sfn.Succeed(self, "Skipped")

        # Create a Deduplication Lambda Function
        dedup_lambda = _lambda.Function(
            self, stackShortNamePrefix+"Jira.Dedup",
            runtime=lambda_runtime,
            handler="dedup_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda/lambda_deploy_sf.zip"),
            # layers=[layer],
            vpc=vpc,
            security_groups=[lambda_security_group],  # Attach Lambda SG
            environment={
                "DB_SECRET": aurora_cluster_secret.secret_name
            }
        )
        aurora_cluster_secret.grant_read(dedup_lambda)

        error_lambda = _lambda.Function(
            self, stackShortNamePrefix + "Error",
            runtime=lambda_runtime,
            handler="dummy.lambda_handler",
            code=_lambda.Code.from_asset("lambda/lambda_deploy_sf.zip"),
            # layers=[layer],
            vpc=vpc,
            security_groups=[lambda_security_group],  # Attach Lambda SG
            environment={
                "DB_SECRET": aurora_cluster_secret.secret_name
            }
        )
        # Define the task for EC2 provision Lambda
        error_task = tasks.LambdaInvoke(
            self, "ErrorTask",
            lambda_function=error_lambda,
            # output_path="$.Payload",
            retry_on_service_exceptions=True,
            result_path="$.ErrorTaskResult",
        )

        wrap_array = sfn.Pass(
            self, "SQS.DataPrep.WrapArray",
            parameters={
                "data.$": "$"
            }
        )

        flatten_input = sfn.Pass(
            self, "SQS.DataPrep.flatten",
            parameters={
                "webhook.$": "$.data[0]"
            }
        )

        parse_body_step = sfn.Pass(
            self, "SQS.DataPrep.bodyStringToJson",
            parameters={
                "webhook.$": "States.StringToJson($.webhook.body)"
            }
        )
        # Step Function: Deduplication Step
        dedup_task = (tasks.LambdaInvoke(
            self, "DedupCheck",
            lambda_function=dedup_lambda,
            result_path="$.DedupCheckResult",
            result_selector={"Payload": sfn.JsonPath.string_at("$.Payload") },
            payload=sfn.TaskInput.from_json_path_at("$.webhook.body"),
        )
            .add_catch(skipped)
#         .add_catch(
#     handler=sfn.Fail(self, "DuplicateWebhook", error="WebhookIsDuplicate"),
#     errors=["WebhookIsDuplicate"]
# )
        )

        # Step Function Choice: Proceed only if not duplicate
        # check_duplicate = sfn.Choice(self, "CheckIfDuplicate")
        # check_duplicate.when(
        #     sfn.Condition.string_equals("$.dedupResult.body", "Duplicate webhook ignored."),
        #     sfn.Succeed(self, "SkipProcessing")
        # )

        # Step Function: Lambda Processing Step (Only if not a duplicate)
        # Create a Processing Lambda Function
        db_insert_fn = _lambda.Function(
            self, stackShortNamePrefix + "DB.insert",
            runtime=lambda_runtime,
            handler="db_insert.lambda_handler",
            code=_lambda.Code.from_asset("lambda/lambda_deploy_sf.zip"),
            # layers=[layer],
            vpc=vpc,
            security_groups=[lambda_security_group],  # Attach Lambda SG
            environment={
                "DB_SECRET": aurora_cluster_secret.secret_name
            }
        )

        aurora_cluster_secret.grant_read(db_insert_fn)

        db_insert_task = tasks.LambdaInvoke(
            self, "DB.insert",
            lambda_function=db_insert_fn,
            # payload=sfn.TaskInput.from_json_path_at("$.DedupCheckResult.body"),
            result_path="$.DBInsertResult",
            result_selector={"Payload": sfn.JsonPath.string_at("$.Payload")},
            payload = sfn.TaskInput.from_json_path_at("$.webhook.body"),
            # output_path="$.Payload"
        ).add_retry(
    backoff_rate=2.0,        # Exponential backoff multiplier
    interval=Duration.seconds(5),  # Initial retry interval
    max_attempts=3,          # Maximum number of retries
    errors=["States.ALL"]    # Retry on all errors, or specify ones like 'Lambda.ServiceException'
).add_catch(handler=error_task,
    errors=["States.ALL"],
    result_path="$.errorInfo")

        # error_json = json.dumps({
        #     "fields": {
        #         "status": "Error"
        #     }
        # })
        # jira_inProgress = sfn.Pass(
        #     self, "Jira.Status.InProgress",
        #     parameters={
        #         "id.$": "$.webhook.body.issue.id",
        #         "data": "{\"fields\": {\"status\": \"In Progress\"}}"
        #     }
        #     , result_path="$.jira"
        # )
        #
        # jira_error = sfn.Pass(
        #     self, "Jira.Status.Error",
        #     parameters={
        #         "id.$": "$.webhook.body.issue.id",
        #         "data": "{\"fields\": {\"status\": \"Error\"}}"
        #     }
        #     ,result_path="$.jira"
        # )

        jira_api = _lambda.Function(
            self, stackShortNamePrefix + "Jira.Api",
            runtime=lambda_runtime,
            handler="jira_api.lambda_handler",
            code=_lambda.Code.from_asset("lambda/lambda_deploy_sf.zip"),
            # layers=[layer],
            vpc=vpc,
            security_groups=[lambda_security_group],  # Attach Lambda SG
            environment={
                "JIRA_URL": "https://<site-url>/rest/api/3/"
            }
        )

        jira_api_inprogress_task = tasks.LambdaInvoke(
            self, "Jira.api.inprogress",
            lambda_function=jira_api,
            # output_path="$.Payload",
            retry_on_service_exceptions=True,
            payload=TaskInput.from_object({
                "jira": {
                    "key": JsonPath.string_at("$.webhook.body.issue.key"),
                    "data": {
                        "fields": {
                            "status": "In Progress"
                        }
                    }
                }
            }),
            result_path="$.jiraApiInProgressResult",
            result_selector={"Payload": sfn.JsonPath.string_at("$.Payload")}
        ).add_retry(
    backoff_rate=2.0,        # Exponential backoff multiplier
    interval=Duration.seconds(5),  # Initial retry interval
    max_attempts=3,          # Maximum number of retries
    errors=["States.ALL"]    # Retry on all errors, or specify ones like 'Lambda.ServiceException'
).add_catch(handler=error_task,
    errors=["States.ALL"],
    result_path="$.jiraApiErrorInfo")

        jira_api_error_task = tasks.LambdaInvoke(
            self, "Jira.api.error",
            lambda_function=jira_api,
            # output_path="$.Payload",
            retry_on_service_exceptions=True,
            payload=TaskInput.from_object({
                "jira": {
                    "key": JsonPath.string_at("$.webhook.body.issue.key"),
                    "data": {
                        "fields": {
                            "status": "Error"
                        }
                    }
                }
            }),
            result_path="$.jiraApiErrorResult",
            result_selector={"Payload": sfn.JsonPath.string_at("$.Payload")}
        ).add_retry(
            backoff_rate=2.0,  # Exponential backoff multiplier
            interval=Duration.seconds(5),  # Initial retry interval
            max_attempts=3,  # Maximum number of retries
            errors=["States.ALL"]  # Retry on all errors, or specify ones like 'Lambda.ServiceException'
        ).add_catch(handler=failed,
                    errors=["States.ALL"],
                    result_path="$.jiraApiErrorInfo")

        error_task.next(jira_api_error_task).next(failed)

        ec2_fn = _lambda.Function(
            self, stackShortNamePrefix + "EC2.provision",
            runtime=lambda_runtime,
            handler="dummy.lambda_handler",
            code=_lambda.Code.from_asset("lambda/lambda_deploy_sf.zip"),
            # layers=[layer],
            vpc=vpc,
            security_groups=[lambda_security_group],  # Attach Lambda SG
            environment={
                "DB_SECRET": aurora_cluster_secret.secret_name,
                "SUBNET_ID": vpc.private_subnets[0].subnet_id
            }
        )

        ec2_fn.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2FullAccess")
        )
        # Define the task for EC2 provision Lambda
        provision_ec2_task = tasks.LambdaInvoke(
            self, "EC2.provision",
            lambda_function=ec2_fn,
            # output_path="$.Payload",
            retry_on_service_exceptions=True,
            result_path="$.ec2Result",
            result_selector={"Payload": sfn.JsonPath.string_at("$.Payload")}
        ).add_catch(handler=error_task,
    errors=["States.ALL"],
    result_path="$.errorInfo")


        vdi_update = _lambda.Function(
            self, stackShortNamePrefix + "VDI.update",
            runtime=lambda_runtime,
            handler="dummy.lambda_handler",
            code=_lambda.Code.from_asset("lambda/lambda_deploy_sf.zip"),
            # layers=[layer],
            vpc=vpc,
            security_groups=[lambda_security_group],  # Attach Lambda SG
            environment={
                "DB_SECRET": aurora_cluster_secret.secret_name
            }
        )
        # Define the task for EC2 provision Lambda
        vdi_update_task = tasks.LambdaInvoke(
            self, "VDI.update",
            lambda_function=ec2_fn,
            # output_path="$.Payload",
            retry_on_service_exceptions=True,
            result_path="$.vdiResult",
            result_selector={"Payload": sfn.JsonPath.string_at("$.Payload")}
        ).add_catch(handler=error_task,
    errors=["States.ALL"],
    result_path="$.errorInfo")

        # jira_done = sfn.Pass(
        #     self, "Jira.Status.Done",
        #     parameters={
        #         "id.$": "$.webhook.body.issue.id",
        #          "data": "{\"fields\": {\"status\": \"Done\"}}"
        #     }
        #     , result_path="$.jira"
        # )
        jira_api_done_task = tasks.LambdaInvoke(
            self, "Jira.api.done",
            lambda_function=jira_api,
            # output_path="$.Payload",
            retry_on_service_exceptions=True,
            payload=TaskInput.from_object({
                "jira": {
                    "key": JsonPath.string_at("$.webhook.body.issue.key"),
                    "data": {
                        "fields": {
                            "status": "Done"
                        }
                    }
                }
            }),
            result_path="$.jiraApiDoneResult",
            result_selector={"Payload": sfn.JsonPath.string_at("$.Payload")}
        ).add_retry(
            backoff_rate=2.0,  # Exponential backoff multiplier
            interval=Duration.seconds(5),  # Initial retry interval
            max_attempts=3,  # Maximum number of retries
            errors=["States.ALL"]  # Retry on all errors, or specify ones like 'Lambda.ServiceException'
        ).add_catch(handler=error_task,
                    errors=["States.ALL"],
                    result_path="$.jiraApiErrorInfo")

    #     jira_final = _lambda.Function(
    #         self, stackShortNamePrefix + "Jira.final",
    #         runtime=lambda_runtime,
    #         handler="dummy.lambda_handler",
    #         code=_lambda.Code.from_asset("lambda/lambda_deploy_sf.zip"),
    #         # layers=[layer],
    #         vpc=vpc,
    #         security_groups=[lambda_security_group],  # Attach Lambda SG
    #         environment={
    #             "DB_SECRET": aurora_cluster_secret.secret_name
    #         }
    #     )
    #     # Define the task for EC2 provision Lambda
    #     jira_final_task = tasks.LambdaInvoke(
    #         self, "Jira.final",
    #         lambda_function=jira_final,
    #         # output_path="$.Payload",
    #         retry_on_service_exceptions=True,
    #         result_path="$.finalResult",
    #         result_selector={"Payload": sfn.JsonPath.string_at("$.Payload")}
    #     ).add_catch(handler=error_task,
    # errors=["States.ALL"],
    # result_path="$.errorInfo")

        # check_duplicate.otherwise(lambda_task)
        sf_definition = (sfn.Chain.start(wrap_array).next(flatten_input).next(parse_body_step).next(dedup_task).next(db_insert_task).next(jira_api_inprogress_task)
                         .next(provision_ec2_task).next(vdi_update_task).next(jira_api_done_task).next(success))

        # lambda_task.next(provision_ec2_task)
        # provision_ec2_task.next(vdi_update_task)
        # vdi_update_task.next(jira_final_task)

        # Create the Step Function State Machine
        state_machine = sfn.StateMachine(
            self, stackShortNamePrefix+"StateMachine",
            definition=sf_definition
            # definition=dedup_task.next(check_duplicate)
            ,timeout=Duration.minutes(5)
        )

        # ✅ Allow Step Function to Invoke Lambdas
        dedup_lambda.add_permission("InvokeByStepFunction", principal=iam.ServicePrincipal("states.amazonaws.com"))
        db_insert_fn.add_permission("InvokeByStepFunction", principal=iam.ServicePrincipal("states.amazonaws.com"))
        ec2_fn.add_permission("InvokeByStepFunction", principal=iam.ServicePrincipal("states.amazonaws.com"))
        vdi_update.add_permission("InvokeByStepFunction", principal=iam.ServicePrincipal("states.amazonaws.com"))
        jira_api.add_permission("InvokeByStepFunction", principal=iam.ServicePrincipal("states.amazonaws.com"))

        # ✅ SQS Event Source for Step Function Trigger
        queue_event_source = event_sources.SqsEventSource(queue)
        # dedup_lambda.add_event_source(queue_event_source)

        # IAM role for the pipe
        pipe_role = Role(self, "PipeRole",
                         assumed_by=ServicePrincipal("pipes.amazonaws.com")
                         )
        queue.grant_consume_messages(pipe_role)
        state_machine.grant_start_execution(pipe_role)

        # Create the pipe
        pipe = pipes.CfnPipe(self, "SqsToStepFunctionPipe",
                             role_arn=pipe_role.role_arn,
                             source=queue.queue_arn,
                             source_parameters=pipes.CfnPipe.PipeSourceParametersProperty(
                                 sqs_queue_parameters=pipes.CfnPipe.PipeSourceSqsQueueParametersProperty(
                                     batch_size=1
                                 )
                             ),
                             target=state_machine.state_machine_arn,
                             target_parameters=pipes.CfnPipe.PipeTargetParametersProperty(
                                 step_function_state_machine_parameters=pipes.CfnPipe.PipeTargetStateMachineParametersProperty(
                                     invocation_type="FIRE_AND_FORGET"
                                 )
                             )
                             )

