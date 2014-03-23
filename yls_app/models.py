from django.db import models
import datetime

class WeiboUser(models.Model):
	''' Represent a user in QQWeibo '''
	name = models.CharField(max_length=30, primary_key = True)
	nick = models.CharField(max_length=30)
	head = models.CharField(max_length=100, null=True, blank=True)
	sex = models.IntegerField() # 1 male, 2 female, 0 not typed in
	country_code = models.CharField(max_length=5, null=True, blank=True)
	province_code = models.CharField(max_length=5, null=True, blank=True)
	city_code = models.CharField(max_length=5, null=True, blank=True)
	fansnum = models.IntegerField()
	idolnum = models.IntegerField()

class UserIdolList(models.Model):
	name = models.ForeignKey(WeiboUser, related_name="user_idol_list")
	idol_name = models.ForeignKey(WeiboUser, related_name="user_idol_name")

class Tweet(models.Model):
	tweet_id = models.CharField(primary_key=True, max_length=100)
	text = models.CharField(max_length=700)
	origtext = models.CharField(max_length=300)
	count = models.CharField(max_length=10) # the number of being retweeted
	mcount = models.CharField(max_length=10) # the number of being commented
	image = models.CharField(max_length=500, null=True, blank=True) # the url of pictures
	name = models.ForeignKey(WeiboUser, related_name="user_tweet")	


class Task(models.Model):
	TYPE_CUT="TYPE_CUT"
	TYPE_RUNLDA="TYPE_RUNLDA"
	TYPE_CONVERT_RAW_TOKEN="TYPE_CONVERT_RAW_TOKEN"
	TYPE_GENERATE_RELATION_IMAGE="TYPE_GEN_RELATION_IMAGE"
	TYPE_CHOICES = (
		(TYPE_CUT, 'Cut the document to words'),
		(TYPE_RUNLDA, 'Run LDA to find topics.'),
		(TYPE_CONVERT_RAW_TOKEN, 'Convert to Raw data'),
		(TYPE_GENERATE_RELATION_IMAGE, 'generate relation image'),
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
	def create_new_lda_task():
		t = Task()
		t = Task.fill_raw(t)
		t. task_type = Task.TYPE_RUNLDA
		t.infomation = "Started!"
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

	def create_new_image_task(in_foler, out_folder):
		t = Task()
		t = Task.fill_raw(t)
		t.task_type = Task.TYPE_GENERATE_RELATION_IMAGE
		t.infomation = "No results available"
		t.save()
		return t

	@staticmethod
	def finish_task(t, success=False):
		t.end_time = Task.get_date_time()
		t.task_status = Task.TASK_STATUS_SUCCESS if success else Task.TASK_STATUS_FAIL
		t.save()

# TO save the databases
class Goods(models.Model):
	product_html = models.CharField(primary_key=True, max_length=50)
	product_name = models.CharField(max_length = 200)
	product_category = models.CharField(max_length = 30)