#!/usr/bin/env python3

from aws_cdk import core

from serverless_api_mutual_tls.serverless_api_mutual_tls_stack import ServerlessApiMutualTlsStack


app = core.App()
ServerlessApiMutualTlsStack(app, "serverless-api-mutual-tls")

app.synth()
