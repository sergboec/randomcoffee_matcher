import logging
import itertools
import json
import os

from matching.games import HospitalResident
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

    # gathering already matched pairs
    history = []
    locations = set()
    langs = set()

    for user, userdata in userdata_this_time.items():
        history_pairs = [(user, i) for i in userdata['history']]
        history.extend(history_pairs)
        locations.add(userdata['location'])
        langs.update(userdata['lang'])
    clear_history = list({frozenset(c) for c in history})

    #match
    if algorithm == 'random':

        matching = []
        unmatched_users_by_location_and_lang_for_remote = []

        #first - local | lang
        #second - remote | lang
        for lang,location in list(itertools.product(langs, locations)):
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

        matching = []
        unmatched_users_by_location_and_lang_for_remote = []

        for lang,location in list(itertools.product(langs, locations)):
            #get suitable users for that lang and location
            users = get_users_for_lang_and_location(lang, location, userdata_this_time)
            pairs_by_interests = combinate_users_with_respect_interests_and_history(users, clear_history, userdata_this_time)

            matched_users = set()
            for item in pairs_by_interests:
                if item[0] in matched_users or item[1] in matched_users:
                    pass
                else:
                    matching.append((str(item[0]),str(item[1])))
                    matched_users.add(str(item[0]))
                    matched_users.add(str(item[1]))

            #need this for remote_coffee
            unmatched_users = set(users) - set(matched_users)
            unmatched_users_by_location_and_lang_for_remote.extend(list(unmatched_users))

            remote_users = []
            for user in set(unmatched_users_by_location_and_lang_for_remote):
                if userdata_this_time[user]['remote']:
                    remote_users.append(user)

            remote_combinations = combinate_users_with_respect_interests_and_history(remote_users, clear_history, userdata_this_time)
            matched_users = set()
            for item in remote_combinations:
                if item[0] in matched_users or item[1] in matched_users:
                    pass
                else:
                    matching.append((str(item[0]),str(item[1])))
                    matched_users.add(str(item[0]))
                    matched_users.add(str(item[1]))

            print(matching)

        result = {
            "result": "OK",
            "matched": matching
        }

    logging.info("@@##==================NEW MATCHES=======================================")
    logging.info(json.dumps(result))
    return result


def combinate_users_with_respect_interests_and_history(users, clear_history, userdata_this_time):
    user_prefs = {}
    user_for_interests = {}
    for user in users:
        user_prefs[user] = userdata_this_time[user]['interests']
        for interest in userdata_this_time[user]['interests']:
            if interest not in user_for_interests.keys():
                user_for_interests[interest] = []
            user_for_interests[interest].append(user)
    capacities = {hosp: 2 for hosp in user_for_interests}
    game = HospitalResident.create_from_dictionaries(user_prefs, user_for_interests, capacities)
    pairs_by_interests = [tuple(x) for x in game.solve().values() if len(tuple(x)) == 2]
    combinations_without_history = set(pairs_by_interests) - set(clear_history)
    return combinations_without_history