from celery import states


RERUNNED = 'RERUNNED'

ALL_STATES = frozenset(list(states.ALL_STATES) + [RERUNNED])
