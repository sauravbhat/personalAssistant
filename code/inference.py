from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, GenerationConfig



def model_fn(model_dir: str):
    print("in model_fn")
    model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
    print("in model_fn 1")
    tokenizer = AutoTokenizer.from_pretrained(model_dir, use_fast=False, trust_remote_code=True)
    print("in model_fn 2")
    model_dict = {'model':model, 'tokenizer':tokenizer}
    print("in model_fn 3")
    return model_dict

def trainthemachine(prompt):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    original_model_outputs = model.generate(input_ids=input_ids, generation_config=GenerationConfig(max_new_tokens=200, num_beams=1))
    #print(f'original_model_outputs MODEL:\n{original_model_outputs}')
    original_model_text_output = tokenizer.decode(original_model_outputs[0], skip_special_tokens=True)
    return original_model_text_output


def predict_fn(input_data, model_dict) :

    """
    Make a prediction with the model
    """
    print("in predict_fn")
    tokenizer = model_dict['tokenizer']
    print("in predict_fn 1")
    print(tokenizer)
    model = model_dict['model']
    print("in predict_fn 2")
    #print(model)
    print(input_data["inputs"])

    input_ids = tokenizer(input_data["inputs"], return_tensors="pt").input_ids
    print("in predict_fn 3")
    original_model_outputs = model.generate(input_ids=input_ids, generation_config=GenerationConfig(max_new_tokens=200, num_beams=1))
    print("in predict_fn 4")
    original_model_text_output = tokenizer.decode(original_model_outputs[0], skip_special_tokens=True)
    print("in predict_fn 5")
    return original_model_text_output
    # return dictionary, which will be json serializable
