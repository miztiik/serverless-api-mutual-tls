#!/usr/bin/env python3

from stacks.back_end.serverless_api_producer_cust_info.serverless_api_cust_info_producer import ServerlessApiCustInfoProducerStack

from aws_cdk import core


app = core.App()


# Produce Customer Info Messages
customer_info_producer_api_stack = ServerlessApiCustInfoProducerStack(
    app,
    f"{app.node.try_get_context('project')}-producer-stack",
    stack_log_level="INFO",
    back_end_api_name="customer_info_producer",
    description="Miztiik Automation: Produce Customer Info Messages"
)


# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            core.Tags.of(app).add(k, v, apply_to_launched_instances=True)


app.synth()
