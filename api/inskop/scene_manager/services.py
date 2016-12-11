import requests
import os
import yaml
import json
from .models import Selection, Window, WindowType


def process_vid(vid):
    cv_address = os.environ['CV_ADDRESS']
    orig_vid = vid.analysis.scene.orig_vid
    orig_vid_path = orig_vid.get_path()
    temp_vid_path = orig_vid_path
    processed_vid_path = vid.get_path()
    process_yaml = yaml.load(vid.process.process)
    if not os.path.isfile(processed_vid_path):

        # Apply filters
        filtered_vid_path = processed_vid_path.replace('.mp4', '_filter.mp4')
        filter_names = [item['filter']['name'] for item in process_yaml[0]['filters']]
        filter_params = [item['filter']['param'] for item in process_yaml[0]['filters']]
        payload = {'temp_path': temp_vid_path,
                   'processed_path': filtered_vid_path,
                   'names': json.dumps(filter_names),
                   'params': json.dumps(filter_params)}
        if filter_names:
            requests.post(cv_address + '/filter', data=payload)
            temp_vid_path = filtered_vid_path

        # Apply trackers
        tracked_vid_path = processed_vid_path.replace('.mp4', '_tracker.mp4')
        tracker_names = [item['tracker']['name'] for item in process_yaml[1]['trackers']]
        tracker_params = [item['tracker']['param'] for item in process_yaml[1]['trackers']]
        tracker_selections = [item['tracker']['selection'] for item in process_yaml[1]['trackers']]
        if tracker_names:
            selection_list = [Selection.objects.get(name=selection_name, analysis=vid.analysis) for selection_name in tracker_selections]
            window_list = [Window.objects.get(selection=selection, type__name='manual').selection_dict for
                           selection in selection_list]
            payload = {'temp_path': temp_vid_path,
                       'processed_path': tracked_vid_path,
                       'names': json.dumps(tracker_names),
                       'params': json.dumps(tracker_params),
                       'selections': json.dumps(window_list)}
            res = requests.post(cv_address + '/tracker', data=payload)
            temp_vid_path = tracked_vid_path
            computed_selection_list = json.loads(json.loads(res.text)['computed_selection_list'])
            for sindex, csl in enumerate(computed_selection_list):
                for cs in csl:
                    selection = selection_list[sindex]
                    item = Window.objects.get(selection=selection, type__name='manual').item
                    item['x'] = round(cs['x'], 3)
                    item['y'] = round(cs['y'], 3)
                    item['width'] = round(cs['w'], 3)
                    item['height'] = round(cs['h'], 3)
                    Window.objects.create(
                        selection=selection,
                        camera=vid.camera,
                        t=cs['t'],
                        type=WindowType.objects.get(name='computed'),
                        video=vid,
                        json_item=json.dumps(item)
                    )

        # Convert to mp4 and remove temp vids
        payload = {'processed_path': processed_vid_path,
                   'temp_path': temp_vid_path}
        requests.post(cv_address + '/clean', data=payload)
