from resources.State import State
from crud.db import get_cursor
from werkzeug.exceptions import Conflict
from crud.State_CRUD import StateCRUD
from crud.Territory_CRUD import TerritoryCRUD
from color_utils.color_utils import colours_roughly_equal
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
	def merge(to_merge_id, sovereign_state_id):
		assert isinstance(to_merge_id, int)
		assert isinstance(sovereign_state_id, int)
		with get_cursor() as cursor:
			to_merge = StateCRUD.get(cursor, to_merge_id)
			sovereign = StateCRUD.get(cursor, sovereign_state_id)
			if to_merge.validity_start < sovereign.validity_start or to_merge.validity_end > sovereign.validity_end:
				raise Conflict(f'The state to merge period {(to_merge.validity_start, to_merge.validity_end)} overflows the period of the sovereign state {(sovereign.validity_start, sovereign.validity_end)}')
			territories_to_change = TerritoryCRUD.get_by_state(cursor, to_merge_id)
			for territory in territories_to_change:
				
				# Color integrity check
				its_color = territory.color
				if not its_color:
					candidate_colors = [r.color for r in to_merge.representations if r.period_intersects(territory.validity_start, territory.validity_end)]
					# All representation matching with the territory have similar color => territory color can be determined (else too complex nothing is done)
					if all(colours_roughly_equal(candidate_colors[0], c) for c in candidate_colors[1:]):
						its_color = candidate_colors[0]
				if its_color:
					sovereign_color = [r.color for r in sovereign.representations if r.period_intersects(territory.validity_start, territory.validity_end)]
					if all(colours_roughly_equal(c, its_color) for c in sovereign_color):
						territory.color = None
					# Destination color is different => set the territory color to preserve it
					else :
						territory.color = its_color
					TerritoryCRUD.edit(cursor, territory, change_color=True)

				territory.state_id = sovereign_state_id
				TerritoryCRUD.edit(cursor, territory, change_state_id=True)
			StateCRUD.delete(cursor, to_merge_id)	
		return sovereign_state_id


	
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

