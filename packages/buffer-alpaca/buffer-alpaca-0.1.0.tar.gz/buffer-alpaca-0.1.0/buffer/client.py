from .http_client import HttpClient

# Assign all the api classes
from .api.info import Info
from .api.user import User
from .api.link import Link
from .api.profile import Profile
from .api.schedule import Schedule
from .api.update import Update

class Client():

	def __init__(self, auth = {}, options = {}):
		self.http_client = HttpClient(auth, options)

	# Returns api instance to get auxilary information about Buffer useful when creating your app.
	#
	def info(self):
		return Info(self.http_client)

	# Returns authenticated user api instance.
	#
	def user(self):
		return User(self.http_client)

	# Returns api instance to get information about links shared through Buffer.
	#
	def link(self):
		return Link(self.http_client)

	# Returns a social media profile api instance.
	#
	# id - Identifier of a social media profile
	def profile(self, id):
		return Profile(id, self.http_client)

	# Returns scheduling api instance for social media profile.
	#
	# id - Identifier of a social media profile
	def schedule(self, id):
		return Schedule(id, self.http_client)

	# Returns a social media update api instance.
	#
	# id - Identifier of a social media update
	def update(self, id):
		return Update(id, self.http_client)

