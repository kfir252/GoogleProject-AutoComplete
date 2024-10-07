import os
import re
from rapidfuzz import process, fuzz
from collections import defaultdict

DATA_PATH = 'Data'

# Cleans up a single line by removing extra spaces, trimming, etc.
def line_cleaner(line: str):
    sentence = re.sub(' +', ' ', line)
    sentence = sentence.strip()  # Strip leading and trailing spaces
    return sentence

# Preprocess the line_contains dictionary by grouping words by their length
def preprocess_line_contains(line_contains):
    length_dict = defaultdict(list)
    for word in line_contains.keys():
        length_dict[len(word)].append(word)
    return length_dict

# Loads and processes all text files from the specified directory
def load_all_files(path):
    line_contains = dict()

    for root, dirs, files in os.walk(path):
        for file_name in files:
            if file_name.endswith('.txt'):
                full_path = os.path.join(root, file_name)
                process_file(full_path, line_contains)

    return line_contains

# Tries opening a file with multiple encodings until one succeeds
def try_open_file_with_encoding(file_path):
    encodings = ['utf-8', 'latin-1', 'utf-16', 'cp1252']
    for encoding in encodings:
        try:
            return open(file_path, 'r', encoding=encoding)
        except (UnicodeDecodeError, FileNotFoundError) as e:
            print(f"Failed to open {file_path} with encoding {encoding}: {e}")
    return None

# Processes each file and populates the line_contains dictionary
def process_file(full_path, line_contains):
    file = try_open_file_with_encoding(full_path)
    if file:
        try:
            line_offset = 0
            for line in file:
                sentence = line_cleaner(line)
                if not sentence:
                    continue
                update_word_dict(sentence, full_path, line_offset, line_contains)
                line_offset += 1
        except Exception as e:
            print(f"Error processing file {full_path}: {e}")
        finally:
            file.close()

# Updates the word dictionary with the entire sentence and its metadata
def update_word_dict(sentence, file_name, line_offset, line_contains):
    words = sentence.split(' ')
    for word in words:
        word = word.lower()
        if word in line_contains:
            line_contains[word].append((sentence, file_name, line_offset))
        else:
            line_contains[word] = [(sentence, file_name, line_offset)]

# Finds exact matches for the search query in line_contains
def find_least_popular_word(Google_search, line_contains):
    unknown_words = []
    found_words = []
    word_matches = {}
    
    for word in Google_search.split(' '):
        word = word.lower()
        if word in line_contains:
            found_words.append(word)
            word_matches[word] = line_contains[word]
        else:
            unknown_words.append(word)
    
    return word_matches, unknown_words

# Find similar words based on Levenshtein distance, prioritizing exact length matches
def find_similar_word(word, length_dict):
    similar_length_words = length_dict[len(word)] + length_dict[len(word) - 1] + length_dict[len(word) + 1]
    return process.extract(word, similar_length_words, scorer=fuzz.ratio, limit=3)

# Scoring function based on match quality and length
def calculate_score(Google_search, matched_sentence):
    max_score = len(Google_search) * 2  # Maximum score is twice the length of the search phrase
    match_ratio = fuzz.ratio(Google_search, matched_sentence) / 100
    score = max_score * match_ratio
    return round(score, 2)

# Finds the lines that fully contain the search query or similar words
def find_fully_containing_lines(word_matches, line_contains, unknown_words, length_dict, Google_search):
    fully_containing_lines = []
    
    if word_matches:
        first_word = next(iter(word_matches))
        candidates = word_matches[first_word]

        for candidate in candidates:
            sentence = candidate[0].lower()

            if all(word in sentence for word in word_matches.keys()):
                if unknown_words:
                    for unknown_word in unknown_words:
                        similar_words = find_similar_word(unknown_word, length_dict)
                        if any(similar_word[0] in sentence for similar_word in similar_words):
                            score = calculate_score(Google_search, sentence)
                            fully_containing_lines.append((candidate[0], candidate[1], candidate[2], score))
                            break
                else:
                    score = calculate_score(Google_search, sentence)
                    fully_containing_lines.append((candidate[0], candidate[1], candidate[2], score))
    
    # Sort the lines by score in descending order
    fully_containing_lines.sort(key=lambda x: x[3], reverse=True)
    return fully_containing_lines

# Prints the results with a limit of 5 lines
def print_results(fully_containing_lines):
    for i in range(min(len(fully_containing_lines), 5)):
        print(f"Line: {fully_containing_lines[i][0]}, File: {fully_containing_lines[i][1]}, Offset: {fully_containing_lines[i][2]}, Score: {fully_containing_lines[i][3]}")

# Main function orchestrates the search process
def main():
    line_contains = load_all_files(DATA_PATH)
    length_dict = preprocess_line_contains(line_contains)
    while True:
        Google_search = line_cleaner(input('Google: '))
        
        word_matches, unknown_words = find_least_popular_word(Google_search, line_contains)

        fully_containing_lines = find_fully_containing_lines(word_matches, line_contains, unknown_words, length_dict, Google_search)
        if fully_containing_lines:
            print_results(fully_containing_lines)
        else:
            print('No results found.')

if __name__ == '__main__':
    main()