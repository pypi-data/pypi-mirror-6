"""
This file is part of SubDownloaderLite.

    SubDownloaderLite is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License.

    SubDownloaderLite is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""

import urllib2, StringIO, gzip, os, xmlrpclib, struct, errno, subdownloader.errors
from subdownloader.settings.matrix import videoSupportedFormat, iso639LangCode
from socket import error as socket_error
from subdownloader.utils.version import get_agent_version

xmlrpclib.Marshaller.dispatch[type(0L)] = lambda _, v, w: w("<value><i8>%d</i8></value>" % v)

class openSubtitles(object):
	userAgent = "Sub Downloader Lite v" + get_agent_version()
	username, password, res, token = "", "", "", ""
	language = "eng"
	server = None
	loggedin = 0
	selection = { 'enabled':False }

	def checkFormat(self,video):
		fileName, fileExtension = os.path.splitext(video)

		for extension in videoSupportedFormat:
			if '.' + extension == fileExtension:
				return True

		return False

	# 11 : Login error
	def LogIn(self):
		self.server = xmlrpclib.ServerProxy('http://api.opensubtitles.org/xml-rpc')
		try:
			self.res = self.server.LogIn(self.username, self.password, self.language, self.userAgent)
		except xmlrpclib.ProtocolError as err:
			return 6

		if self.res['status'] == '414 Unknown User Agent':
			self.LogOut()
			return 9

		if 'token' in self.res:
			if self.res['token'] != "":
				self.token = self.res['token']
				return 1
			else:
				return 11

		return 0

	def LogOut(self):
		try:
			self.res = self.server.LogOut ( self.token )
		except xmlrpclib.ProtocolError as err:
			return 6

		if self.res['status'] == '200 OK':
			self.token = ""
			self.selection = { 'enabled':False }
			return 1
		else:
			return 0	

	# 0 : No subtitles found
	# 1 : Subtitle selected
	# 2 : I/O Error
	# 3 : Login First
	# 5 : Format not supported
	# 6 : Protocol Error
	# 7 : Connection timed out
	# 8 : Connection Refused
	# 9 : 414 Unknown User Agent
	# 10: Unknown error
	def searchSubtitle(self,Location,language):
		self.selection = { 'enabled':False }

		if not self.checkFormat(Location):
			return 5

		video_hash = self.hashFile(Location)

		if video_hash['status'] == 0:
			return 2;
		if self.token == "":
			return 3

		try:
			self.res = self.server.SearchSubtitles(self.token,[ {"sublanguageid":language, "moviehash":video_hash['hash'], "moviebytesize":video_hash['size']} ])
		except xmlrpclib.ProtocolError as err:
			return 6
		except socket_error as serr:
			if serr.errno == errno.ECONNREFUSED:
				return 8
			else:
				return 7
		except:
			return 10

		if self.res['data'] == False:
			return 0

		self.selection = { 
			'enabled':True, 
			'SubDownloadLink':self.res['data'][0]['SubDownloadLink'],
			'SubFormat':self.res['data'][0]['SubFormat'],
			'SubLanguageID':self.res['data'][0]['SubLanguageID'],
			'OriginalVideoFile':Location
		}

		return 1

	# 2      : I/O Error
	# String : File name
	def downloadSubtitle(self,SubDownloadLink,SubFormat,SubLanguageID,video):
		try:
			video_path = os.path.dirname(os.path.realpath(video))
			video_basename = os.path.splitext(os.path.basename(video))[0]

			httpres = urllib2.urlopen(SubDownloadLink)
			compressedFile = StringIO.StringIO(httpres.read())
			decompressedFile = gzip.GzipFile(fileobj=compressedFile)
			outFilePath = video_path + '/' + video_basename + '.' + SubLanguageID + '.' + SubFormat

			with open(outFilePath, 'w') as outfile:
				outfile.write(decompressedFile.read())

			return outFilePath
		except(IOError):
			return 2

	# 4 : Not enabled
	def fetchSelection(self):
		if not self.selection['enabled']:
			return 4

		return self.downloadSubtitle(self.selection['SubDownloadLink'], self.selection['SubFormat'], self.selection['SubLanguageID'], self.selection['OriginalVideoFile'])

	def hashFile(self,name): 
		try: 
			longlongformat = 'q'  # long long 
			bytesize = struct.calcsize(longlongformat) 
			  
			f = open(name, "rb") 
			  
			filesize = os.path.getsize(name) 
			hash = filesize 
			  
			if filesize < 65536 * 2: 
				return {'status':0, 'error':"SizeError"}
		 
			for x in range(65536/bytesize): 
				buffer = f.read(bytesize) 
				(l_value,)= struct.unpack(longlongformat, buffer)  
				hash += l_value 
				hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
				 

			f.seek(max(0,filesize-65536),0) 
			for x in range(65536/bytesize): 
				buffer = f.read(bytesize) 
				(l_value,)= struct.unpack(longlongformat, buffer)  
				hash += l_value 
				hash = hash & 0xFFFFFFFFFFFFFFFF 
		 
			f.close() 
			returnedhash =  "%016x" % hash 
			return {'status':1, 'hash':returnedhash, 'size':filesize}

		except(IOError): 
			return {'status':0, 'error':"IOError"}
