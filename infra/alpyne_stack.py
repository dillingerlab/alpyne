import os
import pathlib
import subprocess

from aws_cdk import Stack, aws_events, aws_events_targets  # Duration,; aws_sqs as sqs,
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class AlpyneStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ab_path = pathlib.Path().resolve()

        build_path = "./build/alpyne/python"
        req = "./lambdas/alpyne/requirements.txt"

        if not os.path.isdir(f"{ab_path}/.build/alpyne/python"):
            subprocess.check_call(f"pip install -q -r {req} -t {build_path}".split())

        layer = _lambda.LayerVersion(self, "alpyne-deps", code=_lambda.Code.from_asset("./build/alpyne"))

        function = _lambda.Function(
            self,
            "alpyne",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset("lambdas/alpyne"),
            handler="main.handler",
            layers=[layer],
            environment={"KEY": "VALUE"},
        )

        weather_api_secret = secretsmanager.Secret.from_secret_name_v2(self, "openweather", "openweather")

        weather_api_secret.grant_read(function)

        # BROKEN
        # aws_events.Rule(
        #    self,
        #    "alpyne-cron-rule",
        #    schedule=aws_events.Schedule.cron(minute="0", hour="6", week_day="0-6"),
        #    targets=[aws_events_targets.LambdaFunction(function)],
        # )
