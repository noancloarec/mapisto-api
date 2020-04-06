from .postgresql_source import PostgreSQLDataSource
from resources.Scene import Scene
import functools
import numpy as np
from resources.Territory import Territory
from resources.BoundingBox import BoundingBox
from werkzeug.exceptions import NotFound

class VideoExtraction(PostgreSQLDataSource):
    def get_video(self, state_id):
        assert isinstance(state_id, int)
        scenes_many = self.get_all_viewboxes(state_id)
        if not scenes_many:
            raise NotFound(f"Cannot find state no {state_id}")
        for scene in scenes_many :
            scene.bbox = self.enlarge_viewBox(self.fit_viewbox_to_aspect_ratio(scene.bbox, 16/9), 1.2)
        scenes_merged = self.merged_scenes_with_similar_boxes(scenes_many)
        for scene in scenes_merged:
            scene.states = self.get_states_between(
                scene.validity_start, 
                scene.validity_end, 
                20,
                bbmin_x = scene.bbox.x,
                bbmin_y= scene.bbox.y,
                bbmax_x=scene.bbox.x+scene.bbox.width,
                bbmax_y =scene.bbox.y+scene.bbox.height,
                end_time_included=False
                )
        return scenes_merged

    def get_all_viewboxes(self, state_id):
        conn =  self.open_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT territories.validity_start, territories.validity_end, min_x, min_y, max_x, max_y
            FROM states INNER JOIN territories 
                ON territories.state_id=states.state_id
            WHERE states.state_id=%s
        ''', (state_id,))
        territory_rows = cur.fetchall()
        conn.close()
        territories = list(map(lambda row : 
            Territory(None, [], 
                BoundingBox(row[2], row[3], row[4] - row[2], row[5]-row[3]),
                row[0], row[1]) ,
            territory_rows
        ))
        changeDates = np.unique(np.array([[row[0], row[1]] for row in territory_rows]).reshape((2*len(territory_rows)))).tolist()
        bbox_list_by_period = [
                                    [t.bounding_box for t in territories if not t.is_outdated(changeDate)] 
                                for changeDate in changeDates[:-1]]
        bbox_by_period = [functools.reduce(lambda a,b : a.union(b), bbox_list ) for bbox_list in bbox_list_by_period]
        return [Scene(changeDates[i], changeDates[i+1], bbox) for i, bbox in enumerate(bbox_by_period)]


    def merged_scenes_with_similar_boxes(self, scenes):
        if len(scenes)<=1:
            return scenes
        else :
            if scenes[0].bbox.get_area_percentage_in_common(scenes[1].bbox) > 40:
                merged = Scene(
                    scenes[0].validity_start, 
                    scenes[1].validity_end, 
                    scenes[0].bbox.union(scenes[1].bbox)
                    ) 
                return self.merged_scenes_with_similar_boxes([merged]+scenes[2:])
            else:
                return scenes[:1] + self.merged_scenes_with_similar_boxes(scenes[1:])
    

    def enlarge_viewBox(self, bbox: BoundingBox, resize_factor: float):
        return BoundingBox(
            x= bbox.x - (resize_factor - 1) * bbox.width / 2,
            y= bbox.y - (resize_factor - 1) * bbox.height / 2,
            width= bbox.width * resize_factor,
            height= bbox.height * resize_factor
        )

    def fit_viewbox_to_aspect_ratio(self, bbox: BoundingBox, aspect_ratio:float ): 
        aspect = bbox.width / bbox.height
        if aspect < aspect_ratio :
            return BoundingBox(
                y = bbox.y,
                height = bbox.height,
                width= aspect_ratio * bbox.height,
                x= bbox.x - (aspect_ratio * bbox.height - bbox.width) / 2
            )
        elif aspect > aspect_ratio :
            return BoundingBox(
                width=bbox.width,
                x=bbox.x,
                height= bbox.width / aspect_ratio,
                y= bbox.y - (aspect_ratio / bbox.width - bbox.height) / 2
            )
        else :
            return bbox
    
