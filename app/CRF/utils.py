from sklearn.model_selection import train_test_split
import numpy
import pickle
import json

# Solve relative path problem.
import os
current_dir = os.path.dirname(__file__)

def read_json(file_name) -> list:
    '''
    load similar word lexicon and sort it in descending order(長詞優先)
    '''
    with open(f'{current_dir}/{file_name}', 'r', encoding='utf-8') as infile:
        lexicon = json.loads(infile.read())

    lexicon = sorted(lexicon, key=lambda x: len(x), reverse=True)
    return lexicon


    
def read_txt_file(file_name) -> list:
    with open(f'{current_dir}/{file_name}', 'r', encoding='utf-8') as infile:
        reuslt = infile.read().splitlines()


    return reuslt   
    


# get the labels of each tokens in train.data
# return a list of lists of labels
def Preprocess(data_list):
    label_list = list()
    for idx_list in range(len(data_list)):
        label_list_tmp = list()
        
        for idx_tuple in range(len(data_list[idx_list])):
            label_list_tmp.append(data_list[idx_list][idx_tuple][1])
            
        label_list.append(label_list_tmp)
        
    return label_list

def Feature(data_list, counting: numpy, tag2index: dict, word2index:dict):
    '''
    '''
    
    feature_list = list()
    for article_idx in range(len(data_list)):
        
        feature_list_tmp = list()
        
        for token_idx in range( len(data_list[article_idx]) ):
            
            feature_dict = dict()
            char, label = data_list[article_idx][token_idx]
            
            feature_dict['char'] =  char
            for tag, index in tag2index.items():
                feature_dict[tag] = counting[ word2index[char] ][ tag2index[tag] ]
            
            if token_idx == 0 : 
                feature_dict['prev_char'] = "<s>"
            else:
                prev_word,_ = data_list[article_idx][token_idx-1]
                feature_dict['prev_char'] = prev_word
                
            if token_idx != len(data_list[article_idx]) -1:
                next_word,_ = data_list[article_idx][token_idx+1]
                feature_dict['next_char'] = next_word
            else:
                feature_dict['next_char'] = "</s>"
            
            
            feature_list_tmp.append(feature_dict)
            
        feature_list.append(feature_list_tmp)
        
    return feature_list



def feature_embedding(sentence_list, counting: numpy, tag2index: dict, word2index:dict):
    '''
    feature embeedding for evealuation
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
    with open(f'{model_name}', 'rb') as model_file:
        crf_model = pickle.load(model_file)
    
    return crf_model


def save_model(crf_model):
    print("saving model...")
    import datetime
    # with open(f'model_{datetime.datetime.today().strftime("%Y%m%d%H%M")}.pkl','wb') as outfile:
        # pickle.dump(crf_model, outfile)
    with open(f'{current_dir}/model.pkl','wb') as outfile:
        pickle.dump(crf_model, outfile)       
        
        
        
def count_word_tag_pairs(train_data_list):
    '''
    Count the number of token marked as certain tag.
    Args:
        corpus : list of list of tuple
    
    Return:
        Counting :
        tag2index : 
        word2index : 
        
    '''
    tag2index = {}
    word2index = {}
    for article in train_data_list:
        for word, tag in article:
            tag2index[tag] = tag2index.get(tag, len(tag2index)) 
            word2index[word] = word2index.get(word, len(word2index))
    
    # print("tag2index: ", tag2index)
    # print("word2index: ", word2index)

    result = numpy.zeros((len(word2index), len(tag2index)), dtype=numpy.uint8)
    for article in train_data_list:
        for word, tag in article:
            result[ word2index[word] ][ tag2index[tag] ] += 1

    return result, tag2index, word2index



def save_dict(counting, tag2index, word2index):
    with open(f"{current_dir}/dict/tag2index.txt", "w", encoding="utf-8") as outfile:
        for key, value in tag2index.items():
            outfile.write(f"{key} {value}\n")
    
    with open(f"{current_dir}/dict/word2index.txt", "w", encoding="utf-8") as outfile:
        for key, value in word2index.items():
            outfile.write(f"{key} {value}\n")  
    

    with open(f"{current_dir}/dict/counting.npy", "wb") as outfile:
        numpy.save(outfile, counting)



def load_dict():
    tag2index = {}
    word2index = {}
    
    with open(f"{current_dir}/dict/tag2index.txt", "r", encoding="utf-8") as infile:
        line = infile.readline()
        while line:
            key, value = line.strip().split(" ")
            tag2index[key] = int(value)
            line = infile.readline()

    with open(f"{current_dir}/dict/word2index.txt", "r", encoding="utf-8") as infile:
        line = infile.readline()
        while line:
            key, value = line.strip().split(" ")
            word2index[key] = int(value)
            line = infile.readline()
    
    with open(f"{current_dir}/dict/counting.npy", "rb") as outfile:
        counting = numpy.load(outfile)
    
    return counting, tag2index, word2index



def load_corpus_file(file):
    with open(f"{current_dir}/{file}", "r", encoding="utf-8") as infile:
        raw_data = infile.read().splitlines()

    result = []
    sentence = []
    index = 0
    sentence_id_list = []
    for row in raw_data:
        if row:
            char, token = row.split(" ")
            sentence.append( (char, token) )
        else:
            result.append(sentence)
            sentence_id_list.append(index)
            index += 1
            sentence = []
        
    train_data, test_data, train_data_id, test_data_id = train_test_split(result, sentence_id_list, test_size=0.2, random_state=42)   
     
    return result, train_data, test_data, train_data_id, test_data_id



def check_word(word, counting, tag2index, word2index):
    
    result = {}
    count = counting[word2index[word]]
    
    for key, value in tag2index.items():
        result[key] = count[value]

    print("test; ", word)
    print(result)
    
    
    
    
