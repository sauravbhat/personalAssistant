import startDeploy
import os


startDeploy.Deploy(model = ['s3://xxxxx/test-model.tar.gz'],
                    serverless=True,
                    script="modelscript_sklearn.py",
                    bucket="personalassistsagemaker",
                    framework = "pytorch",
                    dependencies = ["data"],
                    image='xxxxx.dkr.ecr.us-east-1.amazonaws.com/personalassistent-image-1')
