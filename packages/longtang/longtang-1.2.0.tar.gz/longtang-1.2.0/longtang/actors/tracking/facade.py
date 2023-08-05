import messages
import tracking

from longtang.actors import domain as actor_domain
from longtang.common import interactions
from longtang.common.mediatracking import events as mt_events

class MediaTrackingFacade():

	def __init__(self, system_ref, mediatracking_actor_ref):
		self.__actor_ref=mediatracking_actor_ref
		self.__system_ref=system_ref

	@staticmethod
	def from_system(system_ref):
		actor_ref = system_ref.get_by_id('mediatracking-actor')
		return MediaTrackingFacade(system_ref, actor_ref)

	@staticmethod
	def from_context(context_ref):
		return MediaTrackingFacade.from_system(context_ref._system_ref())

	@staticmethod
	def create_within(system_ref):

		system_ref_tmp = system_ref

		#Actors domain
		if isinstance(system_ref, actor_domain.SystemRefWrapper):
			system_ref_tmp = system_ref._system_ref()
			actor_ref = system_ref.from_type(tracking.TrackingActor,'mediatracking-actor')
		else:
			actor_ref = system_ref_tmp.from_type(tracking.TrackingActor,'mediatracking-actor', None)

		return MediaTrackingFacade(system_ref_tmp, actor_ref)

	def create_audio_tracking(self, mediapath):
		response = interactions.InteractionPatterns.ask(self.__system_ref,self.__actor_ref, messages.CreateTrackingEntry(mediapath))
		return response.tracking_id()

	def create_compressed_audio_tracking(self, mediapath, parent_mediapath):
		response = interactions.InteractionPatterns.ask(self.__system_ref,self.__actor_ref, messages.CreateCompressedAudioFileTrackingEntry(mediapath, parent_mediapath))
		return response.tracking_id(), response.parent_tracking_id()

	def create_compressed_file_tracking(self, mediapath):
		response = interactions.InteractionPatterns.ask(self.__system_ref,self.__actor_ref, messages.CreateCompressedFileTrackingEntry(mediapath))
		return response.tracking_id()

	def lookup(self, tracking_id):
		response = interactions.InteractionPatterns.ask(self.__system_ref,self.__actor_ref, messages.LookupTrackingEntry(tracking_id))
		return response.tracking_info()

	def notify(self, tracking_id, event):
		self.__actor_ref.tell(messages.RegisterTrackingEvent(tracking_id,event), None)

	def notify_inflate_failure(self, tracking_id):
		self.__actor_ref.tell(messages.RegisterCompressedFileTrackingEvent(tracking_id,mt_events.FileCouldNotBeInflated()), None)

	def retrieve_summary(self):
		response = interactions.InteractionPatterns.ask(self.__system_ref,self.__actor_ref, messages.GenerateSummary())
		return response.summary()		