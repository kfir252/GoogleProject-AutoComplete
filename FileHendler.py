import os
import re
 
DATA_PATH = 'Data'

'''
    clean lines from the filesystem to be saved in a clean form
'''
def line_cleaner(line:str):
    sentence = re.sub(' +', ' ', line)
    if sentence and sentence[0] == ' ':
        sentence = sentence[1::]
    if sentence and sentence.endswith('\n'):
        sentence = sentence[:-2:]
    if sentence and sentence[-1] == ' ':
        sentence = sentence[:-1:]
    return sentence

'''
    run on all the files and set the in the dataset to be used in time efficient way
'''
def load_all_files(path):
    # Walk through the directory and process text files
    line_contains = dict()
    
    for root, dirs, files in os.walk(path):
        for file_name in files:
            if file_name.endswith('.txt'):  # Only process text files
                full_path = os.path.join(root, file_name)  # Join root and file name to get the full path
                try:
                    with open(full_path, 'r') as file:
                        line_offset = 0
                        for line in file:
                            sentence = line_cleaner(line)
                            if not sentence:
                                continue
                            for word in sentence.split(' '):
                                if word.lower() in line_contains:
                                    line_contains[word.lower()].append((sentence, file_name, line_offset))
                                else:
                                    line_contains[word.lower()] = [(sentence, file_name, line_offset)]
                            line_offset += 1
                except:
                    pass
    return line_contains

def main():
    line_contains = load_all_files(DATA_PATH)

    while True:
        Google_search = input('Google: ').strip()
        
        # search for the least popular word
        least_popular_word_containers = None
        for word in Google_search.split(' '):
            word = word.lower()
            
            #setup the first to be the least_popular_word
            if word in line_contains:
                if least_popular_word_containers is None:
                    least_popular_word_containers = line_contains[word]
            
                if len(line_contains[word]) < len(least_popular_word_containers):
                    least_popular_word_containers = line_contains[word]
        
        
        # search for all the lines that contains all the words from the search string
        fully_containing_lines = []
        if least_popular_word_containers:
            for containing_line in least_popular_word_containers:
                if Google_search.lower() in containing_line[0]:
                    fully_containing_lines.append(containing_line)

        for i in range(min(len(fully_containing_lines),5)):
            print(fully_containing_lines[i], len(Google_search)*2)

        

        # for line in fully_containing_lines:
        #     print(line, 2 * len(Google_search))
    
if __name__ == '__main__':
    main()