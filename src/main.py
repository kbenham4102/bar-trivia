import base64
import requests
import numpy as np
import argparse
import time
import sys
from PIL import Image, ImageFont, ImageDraw



def parse_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-nqs',type = int, default=26, help="Number of questions to use for the 4 rounds of the game")
    parser.add_argument('-nteams',type = int, default=1, help="Number of teams")
    parser.add_argument('--ctdwn', type=int, default=10, help='seconds to countdown between questions')
    args = parser.parse_args()

    return args

def display_rules(nQs, rounds):
    print("Here are the rules for the game: \n")
    print(f"1. Every team has a set of possible wagers, a wager for each of the {nQs} questions in a round\n")
    print("2. Each wager can only be used once per round\n")
    print("3. At the bonus round question, the wager can be between 0 and the maximum allowed\n")
    print("4. If the bonus is correct, you get your wagered points. If not, you lose those points\n")
    input("Shall we begin? (press Enter)")

def logo_print(text, size):

    ShowText = text
    size = size
    image = Image.new('1', size, 1)  #create a b/w image
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), ShowText) #render the text to the bitmap
    for rownum in range(size[1]): 
    #scan the bitmap:
    # print ' ' for black pixel and 
    # print '#' for white one
        line = []
        for colnum in range(size[0]):
            if image.getpixel((colnum, rownum)): 
                line.append(' ')
            else: 
                line.append('#')
        print( ''.join(line))


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

def ask_question(data):
    """[summary]
    
    Arguments:
        question {str in base64 format} -- [output of data['results'][i] from the json given via API]
    """

    question = data['question']
    qtype = base64.decodebytes(data['type'].encode()).decode()
    question = base64.decodebytes(question.encode()).decode()

    if qtype == 'boolean':
        print("True or False")
    if qtype == 'multiple':
        print("Multiple choice")

    print(question)

    return question, qtype


def list_answer_choices(answers, corr_ans):
    """[summary]
    
    Arguments:
        answers {[type]} -- [description]
        corr_ans {[type]} -- [description]
    
    Returns:
        str -- correct label for the question a,b,c, or d
    """
    labels = ['a', 'b', 'c', 'd']
    for i in range(len(answers)):
        adec = base64.decodebytes(answers[i].encode()).decode()
        input(f"{labels[i]}. {adec}")
        if adec == corr_ans:
            correct_label = labels[i]

    return correct_label

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1
    print('Time is up!\n\n\n\n\n')
    
def get_team_wager(team):
    # Function to get wager for a team and enforce integer value
    # TODO tie in wager enforcement, no wager can be used twice per round

    while True:
        try:
            w = int(input(f"{team} enter your wager\n"))
            if w > 0:
                break
            
        except ValueError as e:
            print("Invalid wager entered")
            print(e)

    return w

def enter_answers(team_dict):

    for team in team_dict:
        team_dict[team]['answers'].append(input(f"{team} enter your answer\n"))
        w = get_team_wager(team)
        team_dict[team]['wagers'].append(w)

    return team_dict

def get_team_scores(team_dict, true_answers, bflags):

    bflag_inds = list(np.where(bflags)[0])

    for team in team_dict:
        mask = np.array(team_dict[team]['answers']) == np.array(true_answers)
        mask_bflag_inds = mask[bflag_inds]
        bonus_missed = list(np.where(mask_bflag_inds == False)[0])
        missed_bonuses = list(np.array(bflag_inds)[bonus_missed])
        mask = mask.astype(int)

        # Bonus wagers they get deducted if wrong
        mask[missed_bonuses] = -1
        team_dict[team]['scores'] = mask*np.array(team_dict[team]['wagers'])

        print(f"{team} has {np.sum(team_dict[team]['scores'])}")




if __name__ == "__main__":

    logo = 'WELCOME TO\nBAR TRIVIA'
    logo_print(logo, size = (70,25))

    

    args = parse_args()

    assert (args.nqs - 2)%4 == 0, "Number of questions minus 2 bonus questions isn't evenly divided into 4 rounds"

    

    qs_per_rd = int((args.nqs - 2)/4)
    rounds = [qs_per_rd, qs_per_rd + 1, qs_per_rd, qs_per_rd + 1]

    display_rules(qs_per_rd, 4)

    team_dict = {}
    print("Lets set the team names")

    for i in range(args.nteams):
        team_name = input(f"Enter {i+1} of {args.nteams} names\n")
        team_dict[team_name] = {}
        team_dict[team_name]['answers'] = []
        team_dict[team_name]['wagers'] = []
        team_dict[team_name]['scores'] = []

    token = get_session_token()
    true_answers = []
    bflags = []
    for i in range(len(rounds)):

        if i == 0:
            difficulty = 'easy'
        elif i > 0 and i < len(rounds):
            difficulty = np.random.choice(['medium', 'easy'])
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

            bflag = False
            if j+1 == rounds[i] and (i == 1 or i == 3):
                input("TIME FOR THE BONUS QUESTION!\n\n")
                if i ==1:
                    print("The maximum wager for this bonus is 10 pts")
                elif i == 3:
                    print("The maximum wager for this bonus is 20 pts")
                bflag = True
                time.sleep(3)
            bflags.append(bflag)

            q, qtype = ask_question(data['results'][j])
            input("\n")

            corr_ans = base64.decodebytes(data['results'][j]['correct_answer'].encode()).decode()

            if qtype == 'boolean':
                input("a. True")
                input("b. False")
                if corr_ans == "True":
                    corr_label = 'a'
                else:
                    corr_label = 'b'
            else:
                answers = np.array([data['results'][j]['correct_answer']] + 
                                    data['results'][j]['incorrect_answers'])
                answers = answers[np.random.permutation(len(answers))]
                corr_label = list_answer_choices(answers, corr_ans)

            countdown(args.ctdwn)
            enter_answers(team_dict)

            print("\nAnd the answer is...")
            time.sleep(3)

            print(f"***  {corr_label}. {corr_ans}  ***\n\n\n")
            true_answers.append(corr_label)

            time.sleep(3)

            if j+1 < rounds[i]:
                input("Are you ready for the next question? (Press Enter to continue...)\n\n")
            else:
                input(f"Thats the end of Round {i+1}! Press Enter to continue...")
        
        if i == 1 or i ==3:
            get_team_scores(team_dict, true_answers, bflags)
            input("Press enter to continue...")

    














