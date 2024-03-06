====================================================
 Deploy and Expose Custom LLM model as an API
====================================================


   

Summary: Existing base LLMs provide excellent baseline that can be trained further and can be deployed to serve specific context. This small project aims at using Flan-T5 base model from hugging face, train with  custom dataset,stored in hugging face, with custom qustion-answer, create and deploy the fresh trained model to sagemaker and expose as an API. Some featurs of the project -
1. The base model chosen for fine tune training is `FlanT5 base model https://huggingface.co/google/flan-t5-base>`__.
2. The base model is less than a gigs size and hence trained in local machine, within jupyter notebook.
3. The training conducted with a small example `dataset <https://huggingface.co/datasets/bsaurav/biography>`__.
3. The training involved Seq2SeqTrainer with T5Tokenizer, T5ForConditionalGeneration as tokenizer and model respectively.
4. The fine tuned model (less than a gigs size,  num_train_epochs=6), has been pushed to both hugging face and AWS S3 (after achiving as .tar.gz file) for deployment.
5. The model containes inference.py file that encode/decode input/output before sending it to model for prediction purpose.
6. The model has been exposed as a lambda API.




Table of Contents
-----------------
1. `Training Base model <#Training-Base-model>`__
2. `Package Model <#Package-Model>`__
3. `AWS Permissions <#AWS-Permissions>`__
4. `Deployment  <#Deployment>`__
5. `Expose As an API  <#Expose-As-an-API>`__
6. `Next Steps <#Next-Steps>`__

Training Base model
-------------------

Flan T5 base model has been chosen as this is less than 1 GB, has showed good model performance and easy to train with custom data set. Though Flan T5 is for test summierization, this can also be used for question-answering (though it may not be best in performance).
As per prereq, an example `dataset <https://huggingface.co/datasets/bsaurav/biography>`__ has been created. the Seq2Seq trainer trains with multiple epochs, trains and stores in local folder. 
The trained model has been pushed to HF using git-lfs.

The trained model :  https://huggingface.co/bsaurav/results.

Package Model
~~~~~~~~~~~~

There are two ways models can be deployed in AWS (yes, we shall use AWS), one from HF directly and another from S3. As we want to control access of the model, hence S3 is preferred ove Hugging face directly.
Also as Flan T5 is encoder-decoder transformer model, hence we need to encode and decode request/responses instead of direct invocation. What I am referring to is an interceptor that will encode/decode for the caller. I have developed code/inference.py which will be part of the package (.tar.gz format)

::

  |
  |- code
       |- inference.py
  |- training_args.bin
  |- spiece.model
  |- special_tokens_map.json
  |- tokenizer_config.json
  |- pytorch_model.bin
  |- generation_config.json
  |- config.json

Once the package is built (tar -cvzf test-model.tar.gz *), it has been pushed to S3 under a bucket/folder.


AWS Permissions
~~~~~~~~~~~~~~~~~~~~~~
 In order to deploy to sagemaker, it is very important to set up the right IAM roles. In this project, we have used custom script for deployment from local machine. hence we created a new IAM user and role that will be used to upload atifact to s3, validate file sizes for correctly assessing instance size and fianlly run deployment procedured.

As a managed service, Amazon SageMaker performs operations on your behalf on the AWS hardware that is managed by Amazon SageMaker.
Amazon SageMaker can perform only operations that the user permits.
You can read more about which permissions are necessary in the `AWS Documentation <https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html>`__.

The SageMaker Python SDK should not require any additional permissions aside from what is required for using SageMaker.
However, if you are using an IAM role with a path in it, you should grant permission for ``iam:GetRole``.


The IAM user will have the following policies for:

S3 interaction:
::

 {
     "Version": "2012-10-17",
     "Statement": [
         {
             "Sid": "VisualEditor0",
             "Effect": "Allow",
             "Action": [
                 "s3:PutObject",
                 "s3:PutObjectTagging",
                 "s3:ListBucket",
                 "s3:ListAllMyBuckets",
                 "s3:GetObject",
                 "s3:CreateBucket"
             ],
             "Resource": "*"
         }
     ]
 }

IAM passrole needed for sagemaker:
::

 {
     "Version": "2012-10-17",
     "Statement": [
         {
             "Sid": "VisualEditor0",
             "Effect": "Allow",
             "Action": [
                 "iam:PassRole",
                 "iam:TagRole",
                 "iam:getRole",
                 "iam:TagPolicy",
                 "iam:TagUser"
             ],
             "Resource": "arn:aws:iam::xxxx:role/xxxxx"
         }
     ]
 }

Sagemaker policy for inference deployment:
::

 {
     "Version": "2012-10-17",
     "Statement": [
         {
             "Sid": "VisualEditor0",
             "Effect": "Allow",
             "Action": [
                 "sagemaker:DeleteTags",
                 "sagemaker:CreateModel",
                 "sagemaker:CreateEndpointConfig",
                 "sagemaker:CreateEndpoint",
                 "sagemaker:AddTags",
                 "sagemaker:InvokeEndpoint",
                 "sagemaker:InvokeEndpointWithResponseStream"
             ],
             "Resource": [
                 "arn:aws:sagemaker:us-east-1:xxxxx:model/*",
                 "arn:aws:sagemaker:us-east-1:xxxxx:endpoint-config/*",
                 "arn:aws:sagemaker:us-east-1:xxxxx:endpoint/*"
             ]
         }
     ]
 }

The IAM role will have the following policies for:
 IAM passrole:
 ::
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": "iam:PassRole",
              "Resource": "*",
              "Condition": {
                  "StringEquals": {
                      "iam:PassedToService": [
                          "sagemaker.amazonaws.com"
                      ]
                  }
              }
          }
      ]
  }

 S3 access:
 ::
   
   {
         "Version": "2012-10-17",
         "Statement": [
             {
                 "Sid": "Statement1",
                 "Effect": "Allow",
                 "Action": [
                     "s3:ListBucket",
                     "s3:GetObject",
                     "s3:CreateBucket",
                     "s3:ListAllMyBuckets"
                 ],
                 "Resource": [
                     "*"
                 ]
             }
         ]
     }

 Logging to cloudwatch:
 ::

   {
    "Version": "2012-10-17",
    "Statement": [
        {
                    "Action": [
                        "logs:CreateLogDelivery",
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:DeleteLogDelivery",
                        "logs:Describe*",
                        "logs:GetLogEvents",
                        "logs:GetLogDelivery",
                        "logs:ListLogDeliveries",
                        "logs:PutLogEvents",
                        "logs:PutResourcePolicy",
                        "logs:UpdateLogDelivery"
                    ],
                    "Resource": "*",
                    "Effect": "Allow"
                }
            ]
        }


Deployment
~~~~~~~~~~~~~~~
The deployment script, used in this project, is a customized version of `Ezsmdeploy <https://github.com/aws-samples/easy-amazon-sagemaker-deployments>`__.

As the deployment will be AWS to AWS, hence the script need to accommodate:
 1. The s3 bucket and folder
 2. The role which will have proper access to get artifact from s3, deploy to sagemaker, log to cloudwatch
 3. The instance size calculation with serverless option.
 4. Type of hugging face artifact.

 
The **Deploy** class is called with these parameters:

::

    Deploy(model = 's3://xxxxxx/deploy/test-model.tar.gz',
                    serverless=True,
                    script="modelscript_sklearn.py",
                    bucket="xxxxxxxx",
                    bucket_folder="deploy",
                    framework = "pytorch",
                    huggingface_model = "true",
                    huggingface_model_task = "question-answering",
                    dependencies = ["data"],
                    #image='.dkr.ecr.us-east-1.amazonaws.com/nnnn-image-1',
                    aws_role="arn:aws:iam::xxxxxxxxxx:role/xxxxxxxx")


Let's take a look at each of these parameters and what they do:

* The model location is the S3 file location 

* Simply do `serverless=True`. Make sure you size your serverless endpoint correctly using `serverless_memory` and `serverless_concurrency`. You can combine other features as well, for example, to deploy a huggingface model on serverless use:

 :: 

    Deploy(model = ... ,
    serverless=True,
    ...,
    huggingface_model = "true",
    huggingface_model_task = "question-answering",
    ...)
                      
                      
* **"script**" is set to a value for non hugging face deployment where methods load_model and predict need to be overridden.
|

* Passing a valid **"bucket"** name will force to use this bucket rather than the Sagemaker default session bucket

|

* Passing a valid **"bucket folder"** name will force to use the specific folder within a bucket rather than everything under a bucket

|

* Choose a supported **"framework"** "tensorflow", "pytorch", "mxnet", "sklearn", "huggingface"

|

* **"dependencies"** refer to the directory from where necessary files are picked up for docker image creation ( not needed for hugging face models). Presently it is mandatory but will be removed for 

|
* If you already have a prebuild docker image, use the **"image"** argument or pass in a **"dockerfilepath"** if you want ezsmdeploy to use this image. Note that ezsmdeploy will automatically build a custom image with your requirements and the right deployment stack (flask-nginx or MMS) based on the arguments passed in. 

|

* If you do not pass in an **"instance_type"**, ezsmdeploy will choose an instance based on the total size of the model (or multiple models passed in), take into account the multiple workers per endpoint, and also optionally a **"budget"** that will choose instance_type based on a maximum acceptible cost per hour. You can of course, choose an instance as well. We assume you need at least 4 workers and each model is deployed redundantly to every vcpu  available on the selected instance; this eliminates instance tupes with lower number of available vcpus to choose from. If model is being downloaded from a hub (like TF hub or Torch hub or NGC) one should ideally pass in an instance since we don't know the size of model. For all instances that have the same memory per vcpu, what is done to tie break is min (cost/total vpcus). Also 'd' instances are preferred to others for faster load times at the same cost since they have NvMe. 

|

* Passing in an **"instance_count"** > 1 will change the initial number of instances that the model(s) is(are) deployed on.

|

* Set **"asynchronous"** to True if you would like to turn this into an async endpoint. Read more about Model monitor here - https://docs.aws.amazon.com/sagemaker/latest/dg/async-inference.html

|

Supported Python Versions
~~~~~~~~~~~~~~~~~~~~~~~~~

The script has been tested on Python 3.6; should run in higher versions!


Expose As an API
~~~~~~~~~~~~~~~~
Now that we have the model deployed in sagemaker, as serverless deployment, its time to test and expose the same as an API. A lambda will be exposed as an API.

The lambda input:

::

{
  "MLKey": "The key that will invoke the right deployed ML version",
  "question": "The question about the person that will be answered by the model"
}


::


    
    payload =  json.dumps({"inputs":"" + event["question"] + " answer:"""})
    endpoint_name = "serv-hf-endpoint-" + event["MLKey"]
    
    sm_runtime = boto3.client("runtime.sagemaker")
    response = sm_runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=payload)

    response_str = response["Body"].read().decode()
    return {
        'answer': json.dumps(response_str)
    }


The lambda been wrapped around API gateway as an GET REST endpoint. The following curl request has been tested successfully - 

::
curl --location --request GET 'https://cder.execute-api.us-east-1.amazonaws.com/default/' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data '{
  "MLKey": "MLkey",
  "question": "WHat is your passion?"
}'

response - 

::

{
    "statusCode": 200,
    "body": "\"\\\"maths!\\\"\""
}




