class FilePackagingConfiguration():
	
	def __init__(self):
		self.__offline_mode=None
		self.__is_enable=None

	@property
	def cover_art_enabled(self):
		return self.__is_enable

	@cover_art_enabled.setter
	def cover_art_enabled(self, value):
		self.__is_enable = value

	@property
	def offline_mode(self):
		return self.__offline_mode

	@offline_mode.setter
	def offline_mode(self, value):
		self.__offline_mode = value

class FilePackagingConfigurationBuilder():

	def __init__(self):
		self.__offline_mode=False
		self.__enabled=True

	def offline_mode(self, value):
		self.__offline_mode=value
		return self

	def cover_art_enabled(self, value):
		self.__enabled=value
		return self

	def build(self):
		config = FilePackagingConfiguration()

		config.offline_mode=self.__offline_mode
		config.cover_art_enabled=self.__enabled

		return config