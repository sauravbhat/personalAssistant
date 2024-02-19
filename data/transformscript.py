import sklearn
from joblib import load
import numpy as np
import os

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
    clf = load(os.path.join(modelpath,f"22-01-2024-12-03-54/pytorch_model.bin"))
    print("loaded")
    return clf

# return prediction based on loaded model (from the step above) and an input payload
def predict(model, payload):
    print(type(payload))
    try:
        print(np.frombuffer(payload))
        print(np.frombuffer(payload).reshape((1,64)))
        print( model.predict(np.frombuffer(payload).reshape((1,64))) )

        out = model.predict(np.frombuffer(payload).reshape((1,64)))

    except Exception as e:
        out = [type(payload),str(e)] #useful for debugging!

    return out
