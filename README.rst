====================================================
 Deploying huggung face model into sagemaker from AWS S3
====================================================


   

Summary: Existing base LLMs provide excellent baseline that can be trained further and can be deployed to serve specific context. This small project is to train Flan-T5 base model with custom qustion-answering and deploy to sagemaker. The project also attempts to expose the deployed model as API for adressing question answers. Some featurs of the project -
1. Custom training has been conducted on HF FlanT5 base model 
2. The example dataset is https://huggingface.co/datasets/bsaurav/biography
3. The traned model has been pushed to S3 after zipping as a tarball
4. Sagemaker has been chosen for model deployment.
5. The model has been deployed and exposed as an API




Table of Contents
-----------------
1. `Training Base model <#Training-Base-model>`__
2. `Package Model <#Package-Model>`__
3. `Setting right IAM role <#other-features>`__
4. `Deployment  <#Deployment>`__
5. `Expose As an API  <#Expose-As-an-API>`__
6. `Next Steps <#Next-Steps>`__

Training Base model
-------------------

Flan T5 base model has been chosen as this is less than 1 GB, has showed good model performance and easy to train with custom data set. Though Flan T5 is for test summierization, this can also be used for question-answering (though it may not be best in performance).
As per prereq, an example dataset has been created in https://huggingface.co/datasets/bsaurav/biography. the Seq2Seq trainer trains with multiple epochs, trains and stores in local folder. 
The trained model has been pushed to HF using git-lfs.

The trained model can be found https://huggingface.co/bsaurav/results.

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


Setting right IAM role
~~~~~~~~~~~~~~~~~~~~~~
 In order to deploy to sagemaker, it is very important to set up the right IAM roles. In this project, we have used custom script for deployment from local machine. hence we created a new IAM user and role that will be used to upload atifact to s3, validate file sizes for correctly assessing instance size and fianlly run deployment procedured.

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
The deployment script, used in this project, is a customized version of Ezsmdeploy (https://github.com/aws-samples/easy-amazon-sagemaker-deployments).

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

AWS Permissions
~~~~~~~~~~~~~~~
Ezsmdeploy uses the  Sagemaker python SDK.

As a managed service, Amazon SageMaker performs operations on your behalf on the AWS hardware that is managed by Amazon SageMaker.
Amazon SageMaker can perform only operations that the user permits.
You can read more about which permissions are necessary in the `AWS Documentation <https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html>`__.

The SageMaker Python SDK should not require any additional permissions aside from what is required for using SageMaker.
However, if you are using an IAM role with a path in it, you should grant permission for ``iam:GetRole``.


Expose As an API
~~~~~~~~~~~~~~~~




Next Steps
~~~~~~~~~~~~~~~~



