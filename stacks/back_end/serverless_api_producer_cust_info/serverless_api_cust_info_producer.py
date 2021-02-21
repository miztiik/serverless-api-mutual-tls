from aws_cdk import aws_apigateway as _apigw
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_logs as _logs
from aws_cdk import aws_iam as _iam
from aws_cdk import core


class GlobalArgs:
    """
    Helper to define global statics
    """

    OWNER = "MystiqueAutomation"
    ENVIRONMENT = "production"
    REPO_NAME = "reliable-queues-with-retry-dlq"
    SOURCE_INFO = f"https://github.com/miztiik/{REPO_NAME}"
    VERSION = "2021_02_07"
    MIZTIIK_SUPPORT_EMAIL = ["mystique@example.com", ]


class ServerlessApiCustInfoProducerStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        construct_id: str,
        stack_log_level: str,
        back_end_api_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add your stack resources below):
        ###################################################
        #######                                     #######
        #######     Customer Info Data Producer     #######
        #######                                     #######
        ###################################################

        # Read Lambda Code
        try:
            with open("stacks/back_end/serverless_api_producer_cust_info/lambda_src/api_producer_cust_info.py",
                      encoding="utf-8",
                      mode="r"
                      ) as f:
                data_producer_fn_code = f.read()
        except OSError:
            print("Unable to read Lambda Function Code")
            raise

        data_producer_fn = _lambda.Function(
            self,
            "sqsDataProducerFn",
            function_name=f"data_producer_fn_{construct_id}",
            description="Produce customer info messages with attributes and send them as a list",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(
                data_producer_fn_code),
            handler="index.lambda_handler",
            timeout=core.Duration.seconds(2),
            reserved_concurrent_executions=2,
            environment={
                "LOG_LEVEL": f"{stack_log_level}",
                "APP_ENV": "Production",
                "MAX_MSGS_TO_PRODUCE": "2",
            }
        )

        data_producer_fn_version = data_producer_fn.latest_version
        data_producer_fn_version_alias = _lambda.Alias(
            self,
            "greeterFnAlias",
            alias_name="MystiqueAutomation",
            version=data_producer_fn_version
        )

        # Create Custom Loggroup for Producer
        data_producer_lg = _logs.LogGroup(
            self,
            "dataProducerLogGroup",
            log_group_name=f"/aws/lambda/{data_producer_fn.function_name}",
            removal_policy=core.RemovalPolicy.DESTROY,
            retention=_logs.RetentionDays.ONE_DAY
        )

        # Restrict Produce Lambda to be invoked only from the stack owner account
        data_producer_fn.add_permission(
            "restrictLambdaInvocationToFhInOwnAccount",
            principal=_iam.AccountRootPrincipal(),
            action="lambda:InvokeFunction",
            source_account=core.Aws.ACCOUNT_ID
        )

        # Create API Gateway

        # Add API GW front end for the Lambda
        cust_info_api_stage_01_options = _apigw.StageOptions(
            stage_name="miztiik-cust-info-v1",
            logging_level=_apigw.MethodLoggingLevel.INFO
        )

        cust_info_api = _apigw.RestApi(
            self,
            "backEnd01Api",
            rest_api_name=f"{back_end_api_name}",
            deploy_options=cust_info_api_stage_01_options,
            endpoint_types=[
                _apigw.EndpointType.EDGE
            ],
            description=f"{GlobalArgs.OWNER}: API Security Automation demonstration using - Mutual TLS"
        )

        cust_info_api_res_root = cust_info_api.root.add_resource("cust-info")
        cust_info_res_v1 = cust_info_api_res_root.add_resource("v1")
        cust_info_v1_data = cust_info_res_v1.add_resource("data")

        cust_info_v1_data_method_get = cust_info_v1_data.add_method(
            http_method="GET",
            request_parameters={
                "method.request.header.InvocationType": True,
                "method.request.path.number": True
            },
            integration=_apigw.LambdaIntegration(
                handler=data_producer_fn,
                proxy=True
            )
        )

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = core.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )

        output_1 = core.CfnOutput(
            self,
            "CustomerInfoDataProducer",
            value=f"https://console.aws.amazon.com/lambda/home?region={core.Aws.REGION}#/functions/{data_producer_fn.function_name}",
            description="Produce data events and push to SQS Queue."
        )

        output_2 = core.CfnOutput(
            self,
            "CustomerInfoProducerApi",
            value=f"{cust_info_v1_data.url}",
            description="Use your browser to fetch customer data from this API."
        )
    """
    # properties to share with other stacks
    @property
    def get_queue(self):
        return self.reliable_q

    @property
    def get_dlq(self):
        return self.reliable_q_retry_1
    """
