import json
import logging
from channels import Channel
from channels.sessions import channel_session
from graphql_relay import from_global_id

from .models import Job
from .tasks import sec3, process_vid_from_id

log = logging.getLogger(__name__)


@channel_session
def ws_connect(message):
    message.reply_channel.send({
        "text": json.dumps({
            "action": "reply_channel",
            "reply_channel": message.reply_channel.name,
        })
    })


@channel_session
def ws_receive(message):
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("ws message isn't json text=%s", message['text'])
        return

    if data:
        reply_channel = message.reply_channel.name

        if data['action'] == "start_sec3":
            start_sec3(data, reply_channel)
        if data['action'] == "start_process_vid":
            start_process_vid(data, reply_channel)


def start_sec3(data, reply_channel):
    log.debug("job Name=%s", data['job_name'])
    # Save model to our database
    job = Job(
        name=data['job_name'],
        status="started",
    )
    job.save()

    # Start long running task here (using Celery)
    sec3_task = sec3.delay(job.id, reply_channel)

    # Store the celery task id into the database if we wanted to
    # do things like cancel the task in the future
    job.celery_id = sec3_task.id
    job.save()

    # Tell client task has been started
    Channel(reply_channel).send({
        "text": json.dumps({
            "action": "started",
            "job_id": job.id,
            "job_name": job.name,
            "job_status": job.status,
        })
    })


def start_process_vid(data, reply_channel):
    log.debug("job Name=%s", data['job_name'])
    # Save model to our database
    job = Job(
        name=data['job_name'],
        status="started",
    )
    job.save()

    vid_id = from_global_id(data['vid_id'])[1]
    process_vid_task = process_vid_from_id.delay(job.id, reply_channel, vid_id)

    # Store the celery task id into the database if we wanted to
    # do things like cancel the task in the future
    job.celery_id = process_vid_task.id
    job.save()

    # Tell client task has been started
    Channel(reply_channel).send({
        "text": json.dumps({
            "action": "started",
            "job_id": job.id,
            "job_name": job.name,
            "job_status": job.status,
        })
    })
