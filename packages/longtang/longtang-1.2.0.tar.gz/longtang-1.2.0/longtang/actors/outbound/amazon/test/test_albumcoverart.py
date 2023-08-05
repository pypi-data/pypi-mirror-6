import unittest
import os

from longtang.actors import actorstestutils
from longtang.actors.outbound.amazon import albumcoverart, messages
from longtang.common import domain as common_domain
from hamcrest import *


class TestAlbumCoverArtActor(unittest.TestCase):

	def setUp(self):

		global tmpdir

		tmpdir=actorstestutils.create_tmp_dir(suffix='_albumart')

	def tearDown(self):
		actorstestutils.remove_dir_content(tmpdir)

	def test_single_file_match(self):

		coverart_tester = actorstestutils.TestActorBuilder().with_type(albumcoverart.AlbumCoverArtActor) \
															.verbosity(None) \
															.build()

		coverart_tester.tell(messages.LookupCoverArt('Carcass', 'Swansong', tmpdir))

		assert_that(coverart_tester.inspector().num_instances(messages.CoverArtFound), is_(equal_to(1)), 'Total amount of CoverArtFound messages received is wrong')

		message = coverart_tester.inspector().first(messages.CoverArtFound)
		assert_that(os.path.isfile(message.cover_path()), is_(equal_to(True)),'Cover file does not exist')		