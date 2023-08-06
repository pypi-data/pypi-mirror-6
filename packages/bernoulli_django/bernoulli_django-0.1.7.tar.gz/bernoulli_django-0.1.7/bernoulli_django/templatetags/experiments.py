from django import template
from django.conf import settings
import bernoulli
import re

register = template.Library()

@register.tag
def experiment(parser, token):
    """
    Setup the context and handle variant blocks
    """
    try:
        args = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("experiment tag requires experiment_id and variant_id as arguments")

    if len(args) < 3:
        raise template.TemplateSyntaxError("experiment tag takes at least 2 arguments")

    experiment_id = args[1]
    request = args[2]
    # should_bucket = args[3]

    # FIXME: handle custom dimensions

    nodelist = parser.parse(('variant', 'endexperiment'))
    variant_nodelists = [(None, nodelist, False)]
    token = parser.next_token()
    while not token.contents.startswith('endexperiment'):
        split = token.split_contents()
        if split[0] == 'variant':
            nodelist = parser.parse(('endvariant'))
            is_control = len(split) == 3 and split[2] == "control"
            variant_nodelists.append((split[1], nodelist, is_control))
            parser.delete_first_token()
        else:
            variant_nodelists.append((None, nodelist, False))

        nodelist = parser.parse(('variant', 'endexperiment'))
        if nodelist:
            variant_nodelists.append((None, nodelist, False))
        token = parser.next_token()

    return ExperimentNode(experiment_id, request, variant_nodelists)


class ExperimentNode(template.Node):
    def __init__(self, experiment_id, request, variant_nodelists):
        self.experiment_id = experiment_id
        self.request = template.Variable(request)
        self.variant_nodelists = variant_nodelists
        self.bot_regex = re.compile(r"(spider|crawl|slurp|bot)", re.I)

    def render(self, context):
        #if self not in context.render_context:
        # Get variant from server
        request = self.request.resolve(context)
        is_a_bot = False
        user_id = request.session.get('bernoulli_id', None) if request.user.is_anonymous() else request.user.id
        experiment = None

        if not user_id:
            is_a_bot = self.is_bot(request.META['HTTP_USER_AGENT'])

        if not is_a_bot:
            experiments = bernoulli.get_experiments(
                settings.BERNOULLI_CLIENT_ID,
                self.experiment_id,
                user_id,
            )


            experiment = None
            for e in experiments:
                if e['id'] == self.experiment_id:
                    experiment = e
                    break


            if user_id is None and experiment is not None:
                # save user id to session for use later
                request.session['bernoulli_id'] = experiment['user_id']

        output = ''
        for variant, nodelist, is_control in self.variant_nodelists:
            if variant is None:
                # Just render this, it is not in a variant block
                output += nodelist.render(context)
            elif is_control and is_a_bot:
                output += nodelist.render(context)
            elif experiment is not None and variant == experiment['variant']:
                output += nodelist.render(context)

        return output

    def is_bot(self, user_agent):
        return self.bot_regex.search(user_agent)
