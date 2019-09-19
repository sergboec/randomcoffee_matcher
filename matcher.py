import logging
import itertools
import json
import os


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_users_for_lang_and_location(lang, location, userdata):
    users = set()
    for user, data in userdata.items():
        if data['location'] == location and lang in data['lang']:
            users.add(user)
    return users

#returns list of tuples
def combinate_users_with_respect_history(users, history):

    # gatheting all possible combinations
    combinations = [i for i in itertools.combinations(users, 2)]
    clear_combinations = list({frozenset(c) for c in combinations})

    # removing combinations that been in a history
    combinations_without_history = set(clear_combinations) - set(history)
    combinations_without_history_t = [tuple(x) for x in combinations_without_history]
    return combinations_without_history_t

def matcher_handler(event, context):

    #get configuration
    algorithm = os.environ['algorithm']

    #get input data
    #in users we have a list of users
    users_this_time = []
    #in userdata we have a dict of preferences for users
    userdata_this_time = {}
    #inside userdata -
    #{
    # userid:{
    # history: [userid,userid...] ([string])
    # interests: [interest1,interest2...] ([string])
    # remote: bool
    # lang: string [ru,en]
    # }
    # }

    for key,item in event.items():
        users_this_time.append(key)
        userdata_this_time[key] = item

    result = {
        "result": "FAIL"
    }

    #match
    if algorithm == 'random':

        #gathering already matched pairs
        history = []
        locations = set()
        langs = set()

        for user, userdata in userdata_this_time.items():
            history_pairs = [ (user,i) for i in userdata['history'] ]
            history.extend(history_pairs)
            locations.add(userdata['location'])
            langs.update(userdata['lang'])
        clear_history = list({frozenset(c) for c in history})

        matching = []
        unmatched_users_by_location_and_lang_for_remote = []

        #first - remote | lang
        #second - local | lang
        for lang,location  in list(itertools.product(langs, locations)):
            #get suitable users for that lang and location
            users = get_users_for_lang_and_location(lang, location, userdata_this_time)
            #get all combinations for that users with respect of history
            combinations = combinate_users_with_respect_history(users, clear_history)

            matched_users = set()
            for item in combinations:
                if item[0] in matched_users or item[1] in matched_users:
                    pass
                else:
                    matching.append(item)
                    matched_users.add(item[0])
                    matched_users.add(item[1])

            #need this for remote_coffee
            unmatched_users = users - matched_users
            unmatched_users_by_location_and_lang_for_remote.extend(list(unmatched_users))

        remote_users = []
        for user in set(unmatched_users_by_location_and_lang_for_remote):
            if userdata_this_time[user]['remote']:
                remote_users.append(user)

        remote_combinations = combinate_users_with_respect_history(remote_users,clear_history)
        matched_users = set()
        for item in remote_combinations:
            if item[0] in matched_users or item[1] in matched_users:
                pass
            else:
                matching.append(item)
                matched_users.add(item[0])
                matched_users.add(item[1])

        result = {
            "result": "OK",
            "matched": matching
        }
    elif algorithm == 'marriage':

        result = {
            "result": "OK"
        }

    logging.info("@@##==================NEW MATCHES=======================================")
    logging.info(json.dumps(result))
    return json.dumps(result)