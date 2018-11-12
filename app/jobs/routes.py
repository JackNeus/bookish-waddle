from flask import current_app, flash, redirect, render_template, url_for
from flask_security import login_required
from flask_login import current_user

from app.jobs import bp, scheduler, controllers as controller
from app.jobs.forms import ScheduleForm
from tasks import tasks

@bp.route('/jobs')
@login_required
def jobs_index():
	return render_template("jobs/jobs.html", jobs=scheduler.get_user_jobs(current_user.get_id()))

@bp.route('/schedule', methods=["GET", "POST"])
@login_required
def schedule():
	form = ScheduleForm()
	if form.validate_on_submit():
		task = tasks.resolve_task(form.task_name.data)
		job_name = form.job_name.data
		param_count = int(form.param_count.data);
		params = []
		for i in range(1, param_count+1):
			params.append(form["param%d" % i].data)
		
		try:
			scheduler.schedule_job(task, params, job_name)
		except Exception as e:
			if current_app.config["DEBUG"]:
				raise e
			flash("Something went wrong.")
			return render_template("jobs/schedule.html", form=form)
		return redirect(url_for("jobs.jobs_index"))
	return render_template("jobs/schedule.html", form=form)

	#print(str(tasks.ucsf_api_aggregate))
	#scheduler.schedule_job(tasks.ucsf_api_aggregate, ['author:glantz'], 'test1')
	#return redirect(url_for('jobs.jobs_index'))

@bp.route('jobs/kill/<id>')
@login_required
def kill(id):
	# TODO: Prevent users from cancelling each other's jobs
	job = controller.get_job_entry(id)
	if job is None:
		flash("Job does not exist.")
	if not controller.kill_job(id):
		flash("Failed to cancel job. Job may still be running.")
	return redirect(url_for("jobs.jobs_index"))