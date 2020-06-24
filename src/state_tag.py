from resources.State import State
from crud.db import get_cursor
from werkzeug.exceptions import Conflict
from crud.State_CRUD import StateCRUD
from crud.Territory_CRUD import TerritoryCRUD
class StateTag:
	@staticmethod
	def post(state):
		assert isinstance(state, State)
		with get_cursor() as cursor:
			StateTag.__check_name_conflicts(state, cursor)
			return StateCRUD.add(cursor, state)

	@staticmethod
	def get(state_id):
		assert isinstance(state_id, int)
		with get_cursor() as cursor:
			return StateCRUD.get(cursor, state_id)
	
	@staticmethod
	def delete(state_id):
		assert isinstance(state_id, int)
		with get_cursor() as cursor:
			return StateCRUD.delete(cursor, state_id)

	@staticmethod
	def put(state):
		assert isinstance(state, State)
		with get_cursor() as cursor:
			StateTag.__check_name_conflicts(state, cursor)
			its_territories = TerritoryCRUD.get_by_state(cursor, state.state_id)
			conflicting_territories = [t for t in its_territories if t.validity_start < state.validity_start or t.validity_end > state.validity_end]
			if len(conflicting_territories):
				raise Conflict(f'Cannot update : territories {[t.territory_id for t in conflicting_territories]} have range from {min(t.validity_start for t  in conflicting_territories)} to {max(t.validity_end for t in conflicting_territories)}')
			StateCRUD.edit(cursor, state)
			return state.state_id


	@staticmethod
	def search(pattern):
		assert isinstance(pattern, str)
		with get_cursor() as cursor:
			return StateCRUD.search(cursor, pattern)
	
	@staticmethod
	def __check_name_conflicts(state, cursor):
		assert isinstance(state, State)
		for rpz in [r for r in state.representations if r.name]:
			conflicts = StateCRUD.get_by_name(cursor, rpz.name, rpz.validity_start, rpz.validity_end)
			if state.state_id:
				conflicts = [c for c in conflicts if c.state_id != state.state_id]
			if len(conflicts):
				conflict = conflicts[0]
				raise Conflict(f'name {rpz.name} is already taken between {rpz.validity_start} and {rpz.validity_end} by state no {conflict.state_id}')

