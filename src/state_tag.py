from resources.State import State
from crud.db import get_cursor
from werkzeug.exceptions import Conflict
from crud.State_CRUD import StateCRUD
class StateTag:
	@staticmethod
	def post(state):
		assert isinstance(state, State)
		with get_cursor() as cursor:
			for rpz in [r for r in state.representations if r.name]:
				conflicts = StateCRUD.get_by_name(cursor, rpz.name, rpz.validity_start, rpz.validity_end)
				if len(conflicts):
					conflict = conflicts[0]
					raise Conflict(f'name {rpz.name} is already taken between {rpz.validity_start} and {rpz.validity_end} by state no {conflict.state_id}')
			return StateCRUD.add(cursor, state)

	@staticmethod
	def get(state_id):
		assert isinstance(state_id, int)
		with get_cursor() as cursor:
			return StateCRUD.get(cursor, state_id)



