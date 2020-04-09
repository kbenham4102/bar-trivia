import base64
import requests
import numpy as np
import argparse
import time

def parse_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-nqs',type = int, default=26, help="Number of questions to use for the 4 rounds of the game")
    parser.add_argument('--ctdwn', type=int, default=10, help='seconds to countdown between questions')
    args = parser.parse_args()

    return args


def get_session_token():

    res = requests.get('https://opentdb.com/api_token.php?command=request')

    token = res.json()['token']

    return token


def gen_category_labels(total_nQs):

    # Generate labels to avoid the Anime category = 31

    cats = list(np.arange(9,31))
    cats += [32]

    game_cats = np.random.choice(cats, size = total_nQs)

    return game_cats

def build_request(nQs, category, difficulty, token, q_type = 'any'):
    """[summary]
    
    Arguments:
        nQs {int} -- number of questions
        category {int} -- integer corresponding to category
        difficulty {str} -- "easy", "medium", or "hard"
    
    Keyword Arguments:
        q_type {str} -- ["multiple", "boolean", or "any"] (default: {'any'})
    
    Returns:
        [str] -- output to send to requests
    """
    if q_type == "any":
        s = f'https://opentdb.com/api.php?amount={nQs}&category={category}&difficulty={difficulty}&encode=base64&token={token}'
    else:
        s = f'https://opentdb.com/api.php?amount={nQs}&category={category}&difficulty={difficulty}&type={q_type}&encode=base64&token={token}'
    
    return s

def build_general_request(nQs, difficulty, token):
    # Build like above just with any category

    s = f'https://opentdb.com/api.php?amount={nQs}&difficulty={difficulty}&encode=base64&token={token}'

    return s

def display_categories(nQs, data):
    """[summary]
    
    Arguments:
        nQs {int} - [number of questions]
        data {type} -- [dict from json returned via API request]
    
    Returns:
        [None] -- [description]
    """

    for i in range(nQs):
        print(base64.decodebytes(data['results'][i]['category'].encode()).decode())
        time.sleep(1.5)
    
    return None

def ask_question(question):
    """[summary]
    
    Arguments:
        question {str in base64 format} -- [output of data['results'][i]['question'] from the json given via API]
    """

    question = base64.decodebytes(question.encode()).decode()

    print(question)

    return question


def list_answer_choices(answers):
    """[summary]
    
    Arguments:
        answers {list} -- list of possible answer strings in base64 format
    """
    for a in answers:
        
        input(base64.decodebytes(a.encode()).decode())

    return None

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1
    print('Time is up!\n\n\n\n\n')
    input("And the answer is...")


if __name__ == "__main__":

    token = get_session_token()

    args = parse_args()

    # categories = gen_category_labels(args.nqs)

    assert (args.nqs - 2)%4 == 0, "Number of questions minus 2 bonus questions isn't evenly divided into 4 rounds"

    qs_per_rd = int((args.nqs - 2)/4)
    rounds = [qs_per_rd, qs_per_rd + 1, qs_per_rd, qs_per_rd + 1]

    # rounds.append(categories[:qs_per_rd])
    # rounds.append(categories[qs_per_rd:(2*qs_per_rd)+1])
    # rounds.append(categories[(2*qs_per_rd)+1:(3*qs_per_rd)+1])
    # rounds.append(categories[(3*qs_per_rd)+1:])


    for i in range(len(rounds)):

        if i == 0:
            difficulty = 'easy'
        elif i > 0 and i < len(rounds):
            difficulty = np.random.choice(['medium', 'hard'])
        else:
            difficulty = 'hard'

        url_req = build_general_request(rounds[i], difficulty, token)

        res = requests.get(url_req)
        data = res.json()

        print(f"Time for Round {i+1}! Your categories are...\n")
        time.sleep(2)

        display_categories(rounds[i], data)

        print("Time for the first question:\n\n")
        input()

        for j in range(rounds[i]):

            if j+1 == rounds[i] and (i == 1 or i == 3):
                input("TIME FOR THE BONUS QUESTION!\n\n")
            
            
            
            ask_question(data['results'][j]['question'])
            input("\n")

            answers = np.array([data['results'][j]['correct_answer']] + 
                                data['results'][j]['incorrect_answers'])
            answers = answers[np.random.permutation(len(answers))]

            list_answer_choices(answers)
            countdown(args.ctdwn)

            corr_ans = base64.decodebytes(data['results'][j]['correct_answer'].encode()).decode()
            print(f"***  {corr_ans}  ***\n\n\n")

            time.sleep(3)

            input("Are you ready for the next question?\n\n")













