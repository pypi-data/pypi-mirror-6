import filepackaging

from longtang.system import domain

class FilePackagingSupervisorFactory(domain.ActorFactory):
	def __init__(self, config):
		self.__config = config

	def create(self, unique_id, system_ref):
		return filepackaging.FilePackagingSupervisor(self.__config, system_ref, unique_id)