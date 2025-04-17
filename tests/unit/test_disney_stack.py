import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.disney_stack import DisneyStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk/disney_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DisneyStack(app, "cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
