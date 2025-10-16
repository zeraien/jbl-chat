from django.utils import timezone
from viewflow import fsm

from chat.enums import MSG_STATE


class MessageFlow:
    state = fsm.State(MSG_STATE, default=MSG_STATE.DRAFT)

    def __init__(self, object):
        self.object = object

    @state.setter()
    def _set_object_state(self, value):
        self.object.state = value

    @state.getter()
    def _get_object_state(self):
        return self.object.state

    @state.transition(source=MSG_STATE.DRAFT, target=MSG_STATE.SENT)
    def mark_sent(self):
        self.object.created = timezone.now()
