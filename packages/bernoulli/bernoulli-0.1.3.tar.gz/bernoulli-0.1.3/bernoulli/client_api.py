import requests, os


BASE_URL = 'https://bernoulli.herokuapp.com/client/api/experiments/'

def get_experiments(client_id, experiment_ids=None, user_id=None, bucket_if_necessary=True, user_data=None):
    """
    Retrieve the experiments the user is a part of
    @param client_id : Bernoulli Client ID
    @param experiment_ids : Either a single or list of experiment ids to retreive
    @param user_id : An identifier for the user
    @param bucket_if_necessary : Choose a variant for the user if one has not been chosen
    @param user_data : Dictionary of user information to be used by the segment filters
    """

    if not client_id:
        raise Exception("client_id is required")

    if type(experiment_ids) is dict:
        experiment_ids = ','.join(experiment_ids)

    params = {
        'clientId': client_id,
        'experimentIds': experiment_ids,
        'userId': user_id,
        'bucketIfNecessary': bucket_if_necessary,
    }

    if user_data is None:
        user_data = {}

    try:
        response = requests.get(BASE_URL, params=dict(params.items() + user_data.items()))
    except requests.ConnectionError:
        raise Exception("Unable to access service")

    val = response.json()
    if val['status'] != 'ok':
        raise Exception(val['message'])

    return val['value']

def record_goal_attained(client_id, experiment_id, user_id):
    """
    Record that a variant was successful for a user
    @param client_id : Bernoulli Client ID
    @param experiment_id : A single experiment id
    @param user_id : An identifier for the user
    """

    try:
        response = requests.post(BASE_URL, data={
            'clientId': client_id,
            'userId': user_id,
            'experimentId': experiment_id,
        })
    except requests.ConnectionError:
        raise Exception("Unable to access services")

    val = response.json()
    if val['status'] != 'ok':
        raise Exception(val['message'])

    return val['value'] # Should be True