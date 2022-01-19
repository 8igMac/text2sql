import pickle
import numpy
from .utils import load_dict

# Solve relative path problem.
import os
current_dir = os.path.dirname(__file__)

def feature_embedding(sentence_list, counting: numpy, tag2index: dict, word2index:dict):
    '''
    feature embeedding for evaluation
    '''
    
    feature_list = list()
    for sentence in sentence_list:
        feature_list_tmp = list()
        
        for token_idx in range(len(sentence)):
            
            char = sentence[token_idx]
            feature_dict = dict()
            feature_dict['char'] =  char
            
            for tag,_ in tag2index.items():
                feature_dict[tag] = counting[ word2index[char] ][ tag2index[tag] ]
            
            
            if token_idx == 0 : 
                feature_dict['prev_char'] = "<s>"
            else:
                feature_dict['prev_char'] = sentence[token_idx-1]
                
            if token_idx != len(sentence) -1:
                feature_dict['next_char'] = sentence[token_idx+1]
            else:
                feature_dict['next_char'] = "</s>"
            
            
            feature_list_tmp.append(feature_dict)
            
        feature_list.append(feature_list_tmp)
        
    return feature_list



def load_model(model_name):
    with open(f'{current_dir}/{model_name}', 'rb') as model_file:
        crf_model = pickle.load(model_file)

    return crf_model



def show_prediction_result(test_sentence, prediction):
    
    for idx, sentence in enumerate(test_sentence):
        print(sentence)
        print(prediction[idx])
        print("\n")
        
        
        

def predict(input_="找出去年在食物裡面花費最高的項目", model="model.pkl", extra_dict=True) -> tuple:

    
    crf_model = load_model(model)
    input_list = [input_]
    
    if extra_dict:
        counting, tag2index, word2index = load_dict()
        
        test_embedding = feature_embedding(input_list, counting, tag2index, word2index)
    
    else:
        test_embedding = feature_embedding(input_list, crf_model.counting, crf_model.tag2index, crf_model.word2index) 
    prediction = crf_model.model.predict(test_embedding)
    
    print((input_, prediction[0]))
    return (input_, prediction[0])


# def check_word(word, counting, tag2index, word2index):   
    # result = {}
    # count = counting[word2index[word]]
    # for key, value in tag2index.items():
        # result[key] = count[value]
    # print("test; ", word)
    # print(result)

if __name__ == "__main__":
    # counting, tag2index, word2index = load_dict()     
    # check_word("忘", counting, tag2index, word2index)
    # exit()
    
    predict()
