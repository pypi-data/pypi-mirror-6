from bernoulli import record_goal_attained
from django.conf import settings

def record_variant_goal(request, experiment_id):
    user_id = request.user.id

    if request.user.is_anonymous():
        user_id = request.session.get('bernoulli_id', None)

    return record_goal_attained(client_id=settings.BERNOULLI_CLIENT_ID, experiment_id=experiment_id, user_id=user_id)
