import startDeploy
import os

hub = {
  #'HF_MODEL_ID':'distilbert-base-uncased-distilled-squad', # model_id from hf.co/models
  'HF_TASK':'question-answering'                           # NLP task you want to use for predictions
}

startDeploy.Deploy(model = 's3://personalassistantml/deploy/test-model.tar.gz',
                    serverless=True,
                    script="modelscript_sklearn.py",
                    bucket="personalassistantml",
                    bucket_folder="deploy",
                    framework = "pytorch",
                    huggingface_model = "true",
                    huggingface_model_task = "question-answering",
                    dependencies = ["data"],
                    #image='419270912185.dkr.ecr.us-east-1.amazonaws.com/personalassistent-image-1',
                    aws_role="arn:aws:iam::419270912185:role/personaltrainersagemaker")
