from longtang.actors import messages

class LookupCoverArt(messages.ActorMessage):

	def __init__(self, artist, album, target_dir_path):
		messages.ActorMessage.__init__(self)
		self.__artist=artist
		self.__album=album
		self.__target_dir_path=target_dir_path

	def artist(self):
		return self.__artist

	def album(self):
		return self.__album

	def target_dir_path(self):
		return self.__target_dir_path

class CoverArtFound(messages.ActorMessage):

	def __init__(self, artist, album, cover_path):
		messages.ActorMessage.__init__(self)
		self.__artist=artist
		self.__album=album
		self.__cover_path=cover_path

	def artist(self):
		return self.__artist

	def album(self):
		return self.__album

	def cover_path(self):
		return self.__cover_path

class CoverArtRetrievalFailed(messages.ActorMessage):

	def __init__(self, artist, album):
		messages.ActorMessage.__init__(self)
		self.__artist=artist
		self.__album=album

	def artist(self):
		self.__artist

	def album(self):
		self.__album
