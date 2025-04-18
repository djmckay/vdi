from diagrams import Diagram, Cluster
from diagrams.aws.compute import Lambda
from diagrams.aws.integration import SQS, StepFunctions
from diagrams.aws.network import APIGateway
from diagrams.aws.database import RDS
from diagrams.aws.security import SecretsManager
from diagrams.aws.compute import Lambda, LambdaFunction
from diagrams.generic.blank import Blank
from diagrams.programming.flowchart import Document
from diagrams.aws.integration import Eventbridge

with (Diagram("AWS CDK Architecture for VDI", show=False, direction="LR")):
    jira = Blank("Jira")
    secrets_manager = SecretsManager("VDI Secrets Manager")

    api_gateway = APIGateway("Jira Webhook API Gateway")
    lambdaAuthorizer = LambdaFunction("Jira Authorizer")
    lambdaAuthorizer << secrets_manager
    validate_signature = Document("Jira.validate_signature")
    jira >> api_gateway >> lambdaAuthorizer
    lambdaAuthorizer - validate_signature
    queue = SQS("Webhook SQS Queue")

    eventbridge = Eventbridge("SqsToStepFunctionPipe")
    with Cluster("VDI Step Function Workflow"):
        dedup_lambda = Lambda("Step 1: Jira.Deduplication")
        jira_in_progress = Lambda("Step 2: Jira.InProgress")
        launch_ec2_lambda = Lambda("Step 3: EC2.Launch")
        vdi_lambda = Lambda("Step 4: VDI.Update")

        with Cluster("Leostream API"):

            broker_login = Document("Broker.Login")
            user_add_api = Document("User.Add")
            vm_add_api = Document("VM.Add")
            vm_assign_api = Document("VM.Assign")

        final_lambda = Lambda("Step 5: Jira.Done")
        step_function = StepFunctions("VDI State Machine")

        vdi_lambda >> [vm_assign_api, vm_add_api, user_add_api, broker_login]
        step_function >> [final_lambda, vdi_lambda, dedup_lambda, launch_ec2_lambda]
        # step_function >> user_add_lambda
        # step_function >> launch_ec2_lambda
        # step_function >> vm_add_lambda
        # step_function >> vm_assign_lambda
        # step_function >> final_lambda
        # step_function >> processing_lambda

    database = RDS("Aurora PostgreSQL")

    lambdaAuthorizer >> queue >> eventbridge >> step_function
    dedup_lambda >> database  # <-- This shows Dedup Lambda linking to Aurora
    vdi_lambda >> database
    launch_ec2_lambda >> database
    final_lambda >> database
    database << secrets_manager
