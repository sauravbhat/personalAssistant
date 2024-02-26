from sagemaker.huggingface.model import HuggingFaceModel
import os
import boto3

#Return loaded model
def load_model(modelpath):
    print(modelpath)
    words = modelpath.split('/')
    print(words)

    print('Loop over dirs and files:')
    path = words[0] + '/' + words[1] + '/' +words[2] + '/'
    for root, dirs, files in os.walk(path):
       print(root)
       for _dir in dirs:
           print('directory = ' + _dir)
       for _file in files:
           print('file = ' +_file)

    #clf = load(os.path.join(modelpath,'model.joblib'))
    #token2id_file = path.join(modelpath, f"model/vocab_token2id.bin")
    #vocab_file = path.join(modelpath, f"model/vocab.nb")
    #pretrained_model = path.join(modelpath, f"model/checkpoint-500/pytorch_model.bin")
    #pretrained_config = path.join(modelpath, f"model/checkpoint-500/config.json")
    #clf = load(os.path.join(modelpath,f"22-01-2024-12-03-54/pytorch_model.bin"))
    #print("loaded")
    #return clf

def main():
    role_name = 'arn:aws:iam::xxxxxxx:role/xxxxxxx'
    #iam_client = boto3.client('iam')
    #role = iam_client.get_role(RoleName='personaltrainersagemaker')
    #print(role)
    #sess = sagemaker.Session()
    hub = {
      #'HF_MODEL_ID':'distilbert-base-uncased-distilled-squad', # model_id from hf.co/models
      'HF_TASK':'question-answering'                           # NLP task you want to use for predictions
    }
    # create Hugging Face Model Class
    huggingface_model = HuggingFaceModel(
       entry_point='inference.py',
       model_data="s3://xxxxxxx/deploy/test-model.tar.gz",  # path to your trained SageMaker model
       env=hub,
       role=role_name,                                            # IAM role with permissions to create an endpoint
       transformers_version="4.26",                           # Transformers version used
       pytorch_version="1.13",                                # PyTorch version used
       py_version='py39',                                    # Python version used
    )

    # deploy model to SageMaker Inference
    predictor = huggingface_model.deploy(
       initial_instance_count=1,
       instance_type="ml.m5.xlarge"
    )
    #load_model(modelpath)
    # example request: you always need to define "inputs"
    #data = {
    #"inputs": {
    #	"question": "What is your name?",
    #	"context": "My Name is Saurav Bhattacharyya."
    #	}
    #}


    # request
    #predictor.predict("question: what is your name? answer:")


main()
