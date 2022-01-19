from crf import CRF
from sklearn.model_selection import train_test_split
from utils import Feature, Preprocess, feature_embedding, load_model, save_model, count_word_tag_pairs, save_dict, load_corpus_file, load_dict


    

def training():

    print("Loading corpus...")
    corpus, train_data, test_data, train_data_id, test_data_id = load_corpus_file("corpus.txt") # lists of list of tuple
    print("Loading dictionary ...")
    counting, tag2index, word2index = load_dict() 
    
    print("Generating Feature Vector...")
    # CRF - Train Data (Augmentation Data)
    x_train = Feature(train_data, counting, tag2index, word2index)
    y_train = Preprocess(train_data)
    
    # CRF - Test Data (Golden Standard)
    x_test = Feature(test_data, counting, tag2index, word2index)
    y_test = Preprocess(test_data)


    print("Start training CRF...")
    crf_model = CRF(counting, tag2index, word2index)
    pred, f1score = crf_model.training(x_train, y_train, x_test, y_test)
    print("F1 score: ", f1score)
    save_model(crf_model)
    





if __name__ == "__main__":
    training()
