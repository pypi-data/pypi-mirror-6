from ua2.table3.plugin import BasePlugin
from django.template import loader, RequestContext


class ActionsState(object):
    def __init__(self, obj, table, request):
        self.obj = obj
        self.table = table
        self.request = request

    @property
    def label(self):
        return self.obj.label

    @property
    def actions(self):
        action_dict = dict(self.obj.actions)
        for action_key in self.build_auctions():
            yield (action_key, action_dict[action_key])

    def build_auctions(self):
        return [ item[0] for item in self.obj.actions ]


class PostAction(BasePlugin):
    def __init__(self, label, actions, state_cls=None):
        self.label = label
        self.actions = actions
        self.state_cls = state_cls or ActionsState

    def process_request(self, table, request):
        state = self.state_cls(self, table, request)
        plugins = table.features.get('postaction', [])
        plugins.append(state)
        table.features['postaction'] = plugins

        if request.REQUEST.get('postaction', '') in state.build_auctions():
            state.process(request.REQUEST.get('postaction', ''))
