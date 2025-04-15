from .models import CustomUser, User_interest, Interests, Event_interests, Event
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances


def user_interest(user):
    all_interests = Interests.objects.all()
    n_interests = len(all_interests)

    train_data_matrix = np.zeros(n_interests)
    for interest in User_interest.objects.filter(user=user):
        train_data_matrix[interest.interest.id-1] = interest.power

    user_events = Event.objects.filter(member=user)

    for event in user_events:
        for interest in Event_interests.objects.filter(event=event):
            train_data_matrix[interest.interest.id-1] += interest.power

    for i in range(all_interests.count()):
        train_data_matrix[i] = train_data_matrix[i] / (len(user_events)+1)

    return train_data_matrix


def similar_events(future_events, user, top):
    top += 1
    all_interests = Interests.objects.all()
    n_interests = len(all_interests)
    n_events = len(future_events)

    if n_interests == 0:
        return future_events

    train_data_matrix = np.zeros((n_events+1, n_interests))

    train_data_matrix[0] = user_interest(user)

    for i, event in enumerate(future_events, 1):
        for interest in Event_interests.objects.filter(event=event):
            train_data_matrix[i, interest.interest.id-1] = interest.power

    events_similarity = pairwise_distances(train_data_matrix, metric='cosine')
    top_sim_events = events_similarity[0].argsort()[1:top]
    sorted_events = [future_events[int(i)-1] for i in top_sim_events]

    return sorted_events


def similar_users_events(future_events, me, top):
    top += 1

    all_interests = Interests.objects.all()
    unique_users = CustomUser.objects.filter(
        members__in=future_events).distinct()
    n_interests = len(all_interests)
    n_events = len(unique_users)

    if n_interests == 0:
        return future_events

    if (n_events == 0):
        return []
    train_data_matrix = np.zeros((n_events+1, n_interests))

    train_data_matrix[0] = user_interest(me)

    for i, user in enumerate(unique_users, 1):
        for interest in User_interest.objects.filter(user=user):
            train_data_matrix[i, interest.interest.id-1] = interest.power
    user_similarity = pairwise_distances(train_data_matrix, metric='cosine')

    top_sim_users = user_similarity[0].argsort()[1:top]
    ids = [unique_users[int(i)-1].id for i in top_sim_users]

    sorted_users = CustomUser.objects.filter(id__in=ids)
    return list(future_events.filter(member__in=sorted_users).distinct())


def hybrid(future_events, me, top):
    event_based = similar_events(future_events, me, top)
    user_based = similar_users_events(future_events, me, top)
    return [i for i in event_based if i in user_based] + [i for i in event_based if i not in user_based]
