from django.db import models
import datetime

class Task(models.Model):
	TYPE_CUT="TYPE_CUT"
	TYPE_RUNLDA="TYPE_RUNLDA"
	TYPE_CONVERT_RAW_TOKEN="TYPE_CONVERT_RAW_TOKEN"
	TYPE_CHOICES = (
		(TYPE_CUT, 'Cut the document to words'),
		(TYPE_RUNLDA, 'Run LDA to find topics.'),
		(TYPE_CONVERT_RAW_TOKEN, 'Convert to Raw data'),
	)
	task_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

	TASK_STATUS_NOT_START="STATUS_NOT_START"
	TASK_STATUS_STARTED="STATUS_STARTED"
	TASK_STATUS_SUCCESS="STATUS_SUCCESS"
	TASK_STATUS_FAIL="STATUS_FAIL"
	TYPE_STATUS_CHOICES = (
		(TASK_STATUS_NOT_START, 'Not Started'),
		(TASK_STATUS_STARTED, 'Started'),
		(TASK_STATUS_SUCCESS, "Task Success"),
		(TASK_STATUS_FAIL, "Task Failed"),
	)
	task_status = models.CharField(max_length=30, choices=TYPE_STATUS_CHOICES)

	infomation = models.CharField(max_length=30000)

	start_time = models.DateTimeField()

	end_time = models.DateTimeField()

	@staticmethod
	def get_date_time():
		return str(datetime.datetime.today())

	@staticmethod
	def fill_raw(t):
		t.start_time = Task.get_date_time()
		t.end_time = t.start_time
		t.task_status = Task.TASK_STATUS_NOT_START
		return t

	@staticmethod
	def create_new_convert_token_task(from_file, to):
		t = Task()
		t = Task.fill_raw(t)
		t.task_type = Task.TYPE_CONVERT_RAW_TOKEN		
		t.infomation = "from:" + from_file + ' to:' + to + ' '
		t.save()
		return t

	@staticmethod
	def create_new_cut_task(in_foler, out_folder):
		t = Task()
		t = Task.fill_raw(t)
		t.task_type = Task.TYPE_CUT
		t.infomation = "No results available"
		t.save()
		return t


	@staticmethod
	def finish_task(t, success=False):
		t.end_time = Task.get_date_time()
		t.task_status = Task.TASK_STATUS_SUCCESS if success else Task.TASK_STATUS_FAIL
		t.save()