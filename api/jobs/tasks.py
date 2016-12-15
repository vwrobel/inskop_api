from __future__ import absolute_import

import json
import logging
import time

import os
import yaml
from channels import Channel
from inskop.celery import app
from inskop.scene_manager.models import Video, Selection, Window, WindowType
from cvtools import CompFilter, SelectionWindow, CompTracker, process_vid

import cv2
from .models import Job

log = logging.getLogger(__name__)


@app.task
def sec3(job_id, reply_channel):
    # time sleep represent some long running process
    time.sleep(3)
    # Change task status to completed
    job = Job.objects.get(pk=job_id)
    log.debug("Running job_name=%s", job.name)

    job.status = "completed"
    job.save()

    # Send status update back to browser client
    if reply_channel is not None:
        Channel(reply_channel).send({
            "text": json.dumps({
                "action": "completed",
                "job_id": job.id,
                "job_name": job.name,
                "job_status": job.status,
            })
        })


@app.task
def process_vid_from_id(
        job_id,
        reply_channel,
        vid_id):

    # Change task status to completed
    job = Job.objects.get(pk=job_id)
    log.debug("Running job_name=%s", job.name)

    # vid = Video.objects.get(pk=vid_id)
    # orig_vid = vid.analysis.scene.orig_vid
    # orig_path = orig_vid.get_path(with_mediaroot=True)
    # cap = cv2.VideoCapture(orig_path)
    # _, frame = cap.read()
    # cv2.imwrite('test.png', frame)

    vid = Video.objects.get(pk=vid_id)
    orig_vid = vid.analysis.scene.orig_vid
    orig_path = orig_vid.get_path(with_mediaroot=True)
    processed_path = vid.get_path(with_mediaroot=True)
    process_yaml = yaml.load(vid.process.process)
    try:
        os.remove(processed_path)
    except OSError:
        pass
    filtered_path = processed_path.replace('.mp4', '_filter.mp4')
    filter_names = [item['filter']['name'] for item in process_yaml[0]['filters']]
    filter_params = [item['filter']['param'] for item in process_yaml[0]['filters']]

    temp_path = orig_path
    comp_process = CompFilter('filter', filter_names, filter_params)
    process_vid(temp_path, filtered_path, comp_process)

    job.status = "progress"
    job.save()

    # Send status update back to browser client
    if reply_channel is not None:
        Channel(reply_channel).send({
            "text": json.dumps({
                "action": "vid filtered",
                "job_id": job.id,
                "job_name": job.name,
                "job_status": job.status,
            })
        })

    temp_path = filtered_path
    tracked_path = processed_path.replace('.mp4', '_tracked.mp4')

    tracker_names = [item['tracker']['name'] for item in process_yaml[1]['trackers']]
    tracker_params = [item['tracker']['param'] for item in process_yaml[1]['trackers']]
    tracker_selections = [item['tracker']['selection'] for item in process_yaml[1]['trackers']]
    selection_list = [Selection.objects.get(name=selection_name, analysis=vid.analysis) for selection_name in
                      tracker_selections]
    window_list = [Window.objects.get(selection=selection, type__name='manual').selection_dict for
                   selection in selection_list]
    selection_windows = [SelectionWindow(
        x=sel['x'],
        y=sel['y'],
        w=sel['w'],
        h=sel['h'],
        t=sel['t'],
        color=sel['color'],
        name=sel['name'],
        type=sel['type']
    ) for sel in window_list]
    comp_process = CompTracker('tracker', tracker_names, tracker_params, selection_windows)
    computed_selection_list = process_vid(temp_path, tracked_path, comp_process)

    # Send status update back to browser client
    if reply_channel is not None:
        Channel(reply_channel).send({
            "text": json.dumps({
                "action": "vid tracked",
                "job_id": job.id,
                "job_name": job.name,
                "job_status": job.status,
            })
        })

    os.rename(tracked_path, processed_path)
    try:
        os.remove(filtered_path)
    except OSError:
        pass

    for sindex, csl in enumerate(computed_selection_list):
        for cs in csl:
            selection = selection_list[sindex]
            item = Window.objects.get(selection=selection, type__name='manual').item
            item['x'] = round(cs.x, 3)
            item['y'] = round(cs.y, 3)
            item['width'] = round(cs.w, 3)
            item['height'] = round(cs.h, 3)
            Window.objects.create(
                selection=selection,
                camera=vid.camera,
                t=cs.t,
                type=WindowType.objects.get(name='computed'),
                video=vid,
                json_item=json.dumps(item)
            )

    job.status = "completed"
    job.save()

    # Send status update back to browser client
    if reply_channel is not None:
        Channel(reply_channel).send({
            "text": json.dumps({
                "action": "completed",
                "video_slug": vid.slug,
                "job_id": job.id,
                "job_name": job.name,
                "job_status": job.status,
            })
        })
