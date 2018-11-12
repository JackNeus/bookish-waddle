import os
from flask import current_app
from rq.job import Job
from tasks.worker import KillJob

from app.models import JobEntry

def get_job_entry(id):
    job = JobEntry.objects(id = id)
    if len(job) != 1:
        return None
    return job[0]

def get_rq_job(id):
	job = KillJob.fetch(id, connection = current_app.redis)
	return job

def kill_job(id):
	job = get_rq_job(id)
	print("Job: ", job)
	if job is None:
		return False
		
	try:
		job.kill()
		return True
	except:
		return False

def delete_job(id):
	job = get_job_entry(id)
	if job is None:
		return False
		
	try:
		job.delete()
	except:
		return False

	# Additional cleanup, but not a huge deal if it fails.
	try: 
		os.remove(current_app.config["TASK_RESULT_PATH"] + id)
		print("Results file (%s) removed." %id)
	except Exception as e:
		raise e
		pass

	return True

def get_job_results(id):
	job = get_job_entry(id)
	if not job:
		return None
	try:
		f = open(current_app.config["TASK_RESULT_PATH"] + id)
		data = f.read(-1)
		f.close()
		return data
	except FileNotFoundError:
		return "Results could not be found."

def get_seed_jobs():
	seed_tasks = ["ucsf_api_aggregate"]
	jobs = JobEntry.objects(task__in = seed_tasks, status = "Completed")
	jobs = list(map(lambda x: (x.id, "%s (%s)" % (x.name, x.task)), jobs))
	print(jobs)
	return jobs