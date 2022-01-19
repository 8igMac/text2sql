import re 
import json
import os
import random
from xml.dom.expatbuilder import parseString
from utils import count_word_tag_pairs, load_corpus_file, save_dict, read_json, read_txt_file

import os
current_dir = os.path.dirname(__file__)

QUESTIONS = []
CORPUS = []

def write_file(file_name):
    with open(f"{current_dir}/{file_name}", 'a', encoding='utf-8') as outfile:
        for sentence in CORPUS:
            for char, label in sentence:
                outfile.write(f"{char} {label}\n")
                
            outfile.write("\n")



def search_from_list(question, _list):
    result = []
    for word in _list:
        index = question.find(word)
        if index != -1:
            match_iter = re.finditer(word, question)
            for match in match_iter:
                result.append((match.start(), match.end()))
                 
    result = sorted(result, key=lambda x: len(x), reverse=True) 
    return result





def generate_corpus(intent_type):
    
    TIMES_DICT = read_txt_file("./dataset/word_time.txt")
    intent_type_list = read_json(f"dataset/intent_{intent_type}.json")
        
    with open(f"{current_dir}/dataset/template_{intent_type}.txt", 'r', encoding='utf-8') as infile:
        template_list = infile.read().splitlines()
    

    for time_word in TIMES_DICT:

        for i in range(3):
            template = random.choice(template_list)
            
            

            containTime = template.find("time")
            containClass = template.find("class")
            containItem = template.find("item")
            
            
            if containClass != -1 and containTime != -1:
                class_list = ["交通", "服飾", "食物"]
                
                for class_word in class_list:
                    question = template.replace("time", time_word)
                    question = question.replace("class", class_word)
                    
                    class_start = question.find(class_word)
                    time_start = question.find(time_word)
                    result = search_from_list(question, intent_type_list)
                    
                    
                    label_data(question,
                               time_start=time_start, 
                               time_length=len(time_word),
                               class_start=class_start,
                               class_length=len(class_word),
                               amount_iter=result,
                               intent_type=intent_type
                            )
    
                    QUESTIONS.append(question)  
                    
            elif containTime != -1:
                question = template.replace("time", time_word)
                time_start = question.find(time_word)
                result = search_from_list(question, intent_type_list)
                
                
                label_data(question,
                           time_start=time_start, 
                           time_length=len(time_word),
                           class_start=-1,
                           class_length=None,
                           amount_iter=result,
                           intent_type=intent_type
                        )

                QUESTIONS.append(question)              
            
            
    write_file("corpus.txt")
    



def label_data(question, 
               time_length, 
               time_start,
               class_length,
               class_start,
               amount_iter,
               intent_type):
    
    '''
    Generate CRF format data
    '''
    result = []
    label_list = ["O" for i in range(len(question))]
    
    # ========= time  =========
    if time_start != -1:
        label_list[time_start] = "B-time"
        
        for index in range(1, time_length-1):
            label_list[time_start + index] = "I-time"
            
        if time_length != -1:
            label_list[ time_start + time_length-1 ] = "E-time"
    
    # ========= class  =========
    if class_start != -1:
        label_list[class_start] = "B-class"
        
        for index in range(1, class_length-1):
            label_list[class_start + index] = "I-class"
        
        if class_length != -1:
            label_list[ class_start + class_length-1 ] = "E-class"   
    
    
    # ========= amount  =========
    if amount_iter != -1:
        
        for match_obj in amount_iter:

            amount_start = match_obj[0]
            amount_length = match_obj[1] - match_obj[0]

            label_list[amount_start] = "B-" + intent_type

            for index in range(1, amount_length-1):
                label_list[amount_start + index] = "I-" + intent_type

            if amount_length != 1 :
                label_list[ amount_start + amount_length-1] = "E-" + intent_type




    assert len(question) == len(label_list); "'label_list' and 'question' is not matched."
    result = []
    
    for index in range(len(question)):
        result.append( (question[index], label_list[index]) )
        # print(question[index], label_list[index])
    # print("\n")
    
    
    CORPUS.append(result)
    

def generate_topN_corpus():
    intent_type = "topN"
    
    TIMES_DICT = read_txt_file("./dataset/word_time.txt")
    intent_type_list = read_json(f"dataset/intent_{intent_type}.json")
    item_list = read_txt_file("./dataset/word_item.txt")
    
    with open(f"dataset/template_{intent_type}.txt", 'r', encoding='utf-8') as infile:
        template_list = infile.read().splitlines()   

    class_list = ["交通", "服飾", "食物"]

    for template in template_list:

        for topN in range(2, 6):
            
            time_start = -1           
            class_start = -1
            item_start = -1
            topN_start = -1
            
            question = template.replace("N", str(topN))
            
            word_time = random.choice(TIMES_DICT)
            question = question.replace("time", word_time)  
                     
            
            word_class = random.choice(class_list)
            question = question.replace("class", word_class)
            
            
            time_start = question.find(word_time)
            class_start = question.find(word_class)                
            topN_start = question.find("前"+str(topN)+"名")


                

            if question.find("item") != -1:
                
                for word_item in item_list:

                    question = question.replace("item", word_item)
                    item_start = question.find(word_item)
                    label_topN_data(question, 
                                    time_start=time_start,
                                    time_length=len(word_time),
                                    class_start=class_start,
                                    class_length=len(word_class),
                                    topN_start=topN_start,
                                    topN_length=3,
                                    item_start=item_start,
                                    item_length=len(word_item))
                    
            else:

                                
                label_topN_data(question, 
                    time_start=time_start,
                    time_length=len(word_time),
                    class_start=class_start,
                    class_length=len(word_class),
                    topN_start=topN_start,
                    topN_length=3,
                    item_start=-1,
                    item_length=0)


def label_topN_data(question, 
                    time_start, 
                    time_length, 
                    class_start, 
                    class_length, 
                    topN_start, 
                    topN_length,
                    item_start,
                    item_length):
    
    result = []
    label_list = ["O" for i in range(len(question))]
    
    # ========= time  =========
    if time_start != -1:
        label_list[time_start] = "B-time"
        
        for index in range(1, time_length-1):
            label_list[time_start + index] = "I-time"
            
        if time_length != -1:
            label_list[ time_start + time_length-1 ] = "E-time"
    
    # ========= class  =========
    if class_start != -1:
        label_list[class_start] = "B-class"
        
        for index in range(1, class_length-1):
            label_list[class_start + index] = "I-class"
        
        if class_length != -1:
            label_list[ class_start + class_length-1 ] = "E-class"   
    
    
    # ========= topN  =========
    if topN_start != -1:
        label_list[topN_start] = "B-topN"
        
        for index in range(1, topN_length-1):
            label_list[topN_start + index] = "I-topN"
        
        if topN_length != -1:
            label_list[ topN_start + topN_length-1 ] = "E-topN" 
    
    
    # ========= item  =========
    if item_start != -1:
        label_list[item_start] = "B-item"
        
        for index in range(1, item_length-1):
            label_list[item_start + index] = "I-item"
        
        if item_length != -1:
            label_list[ item_start + item_length-1 ] = "E-item"     
    

    assert len(question) == len(label_list); "'label_list' and 'question' is not matched."
    result = []
    
    for index in range(len(question)):
        result.append( (question[index], label_list[index]) )
        print(question[index], label_list[index])
    print("\n")
    
    
    CORPUS.append(result)  


     
def load_extra_corpus(repeat=3):
    with open(f"{current_dir}/extra_data.txt", "r", encoding="utf-8") as infile:
        data  = infile.read()


    with open(f"{current_dir}/corpus.txt", "a", encoding="utf-8") as outfile:
        for i in range(repeat):
            outfile.write(data)




if __name__ == "__main__":
    
    
    if os.path.exists("corpus.txt"): 
        os.remove("corpus.txt")
    print("Start generating question type: amount...")
    generate_corpus("amount")
    print("Start generating question type: ratio")
    generate_corpus("ratio")
    print("Start generating question type: detail")
    generate_corpus("detail")
    # print("Start generating question type: topN")
    # generate_topN_corpus()

    load_extra_corpus()

    # ========= Generating question.txt =========
    if os.path.exists(f"{current_dir}/question.txt"): 
        os.remove(f"{current_dir}/question.txt")
        
    print("Generating 'question.txt' ...")
    with open(f"{current_dir}/question.txt", "a", encoding="utf-8") as outfile:
        for sentence in QUESTIONS:
            outfile.write(f"{sentence}\n")

    # ========= Counting (word,tag) pairs ... =========

    print("Counting (word,tag) pairs ...")
    corpus, train_data, test_data, train_data_id, test_data_id = load_corpus_file("corpus.txt")
    counting, tag2index, word2index = count_word_tag_pairs(corpus)
    
    print("save dict...")
    save_dict(counting, tag2index, word2index)
