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

import os
from subdownloader.opensubtitles import openSubtitles as openSubtitles
from subdownloader.settings.matrix import videoSupportedFormat, iso639LangCode

class downloadManager(openSubtitles):
#	def connect(self):
#	def disconnect(self):
	lastLangCheckStatus = { 'code':'eng', 'status':True }

	def checkIfSubtitleIsNeeded(self,video,lang):
		video_path = os.path.dirname(os.path.realpath(video))
		video_basename = os.path.splitext(os.path.basename(video))[0]
		video_subtitle_file = video_path + '/' + video_basename + '.' + lang + '.srt'

		return not os.path.isfile(video_subtitle_file)

	def DownloadSingle(self,Video,Language):
		for lan in Language:
			if not self.checkLanguage(lan):
				print "Language " + lan + " not supported"

			elif not self.checkIfSubtitleIsNeeded(Video,lan):
				print Video + " already have " + lan + " subtitle"
			else:
	        		print "Serching subtitle for file (" + lan + "): " + Video

				retVal = self.searchSubtitle(Video,lan)
				if retVal == 0:
					print "\tNo subtitle found"
					return 0
				if retVal == 7:
					print "\tConnection timed out"
					return 0
				if retVal == 6:
					print "\tService Unaviable"
					return 0
				if retVal == 8:
					print "\tConnection Refused"
					return 0
				if retVal != 1:
        		        	print "\tUnknown Error : ", retVal
        		        	return 10

        			print "\tFetching subtitle...\n\tResult - " , self.fetchSelection()
	
		return 1

	def DownloadFolder(self,Folder,Language):
		for lan in Language:
			if not self.checkLanguage(lan):
				print "Language " + lan + " not supported"
				Language.remove(lan)

		if len(Language) == 0:
			return 0

		filecount = 0
		for root, dirs, files in os.walk(Folder):
			for file in files:
				for ext in videoSupportedFormat:
					filename = os.path.join(root, file)
					if file.endswith(ext):
						self.DownloadSingle(filename,Language)
						filecount += 1

		print "Download completed." \
			"File processed : " , filecount

	def checkLanguage(self,Language):
		if self.lastLangCheckStatus['code'] == Language:
			return self.lastLangCheckStatus['status']

		for lang in iso639LangCode:
			if lang == Language:
				self.lastLangCheckStatus = { 'code':Language, 'status':True }
				return True

		lastLangCheckStatus = { 'code':Language, 'status':False }
		return False
