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
			conflicts = StateTag.__get_name_conflicts(state, cursor)
			if len(conflicts):
				report = ', by '.join([f'{c.state_id} from {c.validity_start.year} to {c.validity_end.year}' for c in conflicts])
				raise Conflict(f'names are already taken by {report} ')
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
	def put(state, absorb_conflicts):
		assert isinstance(state, State)
		with get_cursor() as cursor:
			conflicts = StateTag.__get_name_conflicts(state, cursor)
			if len(conflicts):
				if absorb_conflicts:
					start_conflicts = min(s.validity_start for s in conflicts)
					end_conflicts = max(s.validity_end for s in conflicts)
					StateCRUD.edit(cursor, state, change_validity_start=True, change_validity_end=True)
					if start_conflicts < state.validity_start or end_conflicts > state.validity_end:
						raise Conflict(f'Cannot absorb conflicts : they go from {start_conflicts.isoformat()} to {end_conflicts.isoformat()}')
					for c in conflicts:
						StateTag.__merge_with_cursor(cursor, c.state_id, state.state_id)
				else:
					report = ', by '.join([f'{c.state_id} from {c.validity_start.year} to {c.validity_end.year}' for c in conflicts])
					raise Conflict(f'names are already taken by {report} ')

			its_territories = TerritoryCRUD.get_by_state(cursor, state.state_id)
			conflicting_territories = [t for t in its_territories if t.validity_start < state.validity_start or t.validity_end > state.validity_end]
			if len(conflicting_territories):
				raise Conflict(f'Cannot update : territories {[t.territory_id for t in conflicting_territories]} have range from {min(t.validity_start for t  in conflicting_territories)} to {max(t.validity_end for t in conflicting_territories)}')
			StateCRUD.edit(cursor, state, change_representations=True, change_validity_start=True, change_validity_end=True)
			return state.state_id


	@staticmethod
	def search(pattern):
		assert isinstance(pattern, str)
		with get_cursor() as cursor:
			return StateCRUD.search(cursor, pattern)

	@staticmethod
	def merge(to_merge_id, sovereign_state_id):
		with get_cursor() as cursor:
			StateTag.__merge_with_cursor(cursor, to_merge_id, sovereign_state_id)
		return sovereign_state_id

	@staticmethod
	def __merge_with_cursor(cursor, to_merge_id, sovereign_state_id):
		assert isinstance(to_merge_id, int)
		assert isinstance(sovereign_state_id, int)
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
	def __get_name_conflicts(state, cursor):
		assert isinstance(state, State)
		res = []
		res_ids = []
		for rpz in [r for r in state.representations if r.name]:
			conflicts = StateCRUD.get_by_name(cursor, rpz.name, rpz.validity_start, rpz.validity_end)
			if state.state_id:
				conflicts = [c for c in conflicts if c.state_id != state.state_id and c.state_id not in res_ids]
			for c in conflicts:
				res.append(c)
				res_ids.append(c.state_id)
		return res
	

