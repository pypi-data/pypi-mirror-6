#https://stuffivelearned.org/doku.php?id=programming:python:albumcoverdl

import messages
import os.path
import urllib2

from lxml import etree

from amazonproduct import API
from longtang.actors import actors
from longtang.common import domain as common_domain

#http://aws-portal.amazon.com/gp/aws/developer/account/index.html
#http://python-amazon-product-api.readthedocs.org/en/latest/pagination.html

class AlbumCoverArtActor(actors.Actor):

    __api=API('AKIAIUHQBFQK7T2VSSTQ','KLoVSu3WB3n3Nj4pCjsIue1SOSE14ynO4WjffFCc','us')
    __SEARCH_GROUP='Music'
    __RESPONSE_GROUP='Images'

    def receive(self, message):
        if isinstance(message, messages.LookupCoverArt):
            self.logger().debug(u'Downloading album art from "{0} - {1}" .....'.format(message.artist(), message.album()), None)

            result=None

            try:
                result = self.__api.item_search('Music', ResponseGroup='Images', Keywords='{0} {1}'.format(message.artist() , message.album()), AssociateTag='ws')
            except Exception , e:
                # try just the album
                try:
                    result = self.__api.item_search('Music', ResponseGroup='Images', Keywords='{0}'.format(message.album()), AssociateTag='ws')
                except Exception, e:
                    self.logger().error(u'Album art search from "{0} - {1}" failed: {2}'.format(message.artist(), message.album(), e), None)                    

            if result is not None:

                target_local_file=os.path.join(message.target_dir_path(), 'cover.jpg')

                block_sz = 8192

                for item in result:

                    try:
                        url=str(item.ImageSets.ImageSet.LargeImage.URL)
                    except:
                        url=str(item.ImageSets.ImageSet.MediumImage.URL)

                    #print(etree.tostring(item, pretty_print=True))

                    with open(target_local_file, 'wb') as target:

                        try:
                            fh = urllib2.urlopen(url)

                            while True:
                                buffer = fh.read(block_sz)
                                
                                if not buffer:
                                    break

                                target.write(buffer)

                            fh.close()
                            
                            self.sender().tell(messages.CoverArtFound(message.artist(), message.album(), target_local_file), self.myself())

                            self.logger().info(u'Album art from "{0} - {1}" successfully downloaded.'.format(message.artist(), message.album()), None)

                        except urllib2.URLError, e:
                            self.logger().error(u'Album art retrieval from "{0} - {1}" failed: {2}'.format(message.artist(), message.album(), e), None)
                            self.sender().tell(messages.CoverArtRetrievalFailed(message.artist(), message.album()), self.myself())

                    break
            else:
                self.logger().error(u'Album art from "{0} - {1}" was not found.'.format(message.artist(), message.album()), None)
                self.sender().tell(messages.CoverArtRetrievalFailed(message.artist(), message.album()), self.myself())