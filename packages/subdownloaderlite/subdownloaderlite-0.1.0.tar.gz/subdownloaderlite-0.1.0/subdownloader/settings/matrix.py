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

iso639LangCode = [ 'aar', 'abk', 'ace', 'ach', 'ada', 'ady', 'afa', 'afh', 'afr', 'ain',
        'aka', 'akk', 'alb', 'ale', 'alg', 'alt', 'amh', 'ang', 'apa', 'ara', 'arc',
        'arg', 'arm', 'arn', 'arp', 'art', 'arw', 'asm', 'ast', 'ath', 'aus', 'ava',
        'ave', 'awa', 'aym', 'aze', 'bad', 'bai', 'bak', 'bal', 'bam', 'ban', 'baq',
        'bas', 'bat', 'bej', 'bel', 'bem', 'ben', 'ber', 'bho', 'bih', 'bik', 'bin',
        'bis', 'bla', 'bnt', 'bos', 'bra', 'bre', 'btk', 'bua', 'bug', 'bul', 'bur',
        'byn', 'cad', 'cai', 'car', 'cat', 'cau', 'ceb', 'cel', 'cha', 'chb', 'che',
        'chg', 'chi', 'chk', 'chm', 'chn', 'cho', 'chp', 'chr', 'chu', 'chv', 'chy',
        'cmc', 'cop', 'cor', 'cos', 'cpe', 'cpf', 'cpp', 'cre', 'crh', 'crp', 'csb',
        'cus', 'cze', 'dak', 'dan', 'dar', 'day', 'del', 'den', 'dgr', 'din', 'div',
        'doi', 'dra', 'dua', 'dum', 'dut', 'dyu', 'dzo', 'efi', 'egy', 'eka', 'elx',
        'eng', 'enm', 'epo', 'est', 'ewe', 'ewo', 'fan', 'fao', 'fat', 'fij', 'fil',
        'fin', 'fiu', 'fon', 'fre', 'frm', 'fro', 'fry', 'ful', 'fur', 'gaa', 'gay',
        'gba', 'gem', 'geo', 'ger', 'gez', 'gil', 'gla', 'gle', 'glg', 'glv', 'gmh',
        'goh', 'gon', 'gor', 'got', 'grb', 'grc', 'ell', 'grn', 'guj', 'gwi', 'hai',
        'hat', 'hau', 'haw', 'heb', 'her', 'hil', 'him', 'hin', 'hit', 'hmn', 'hmo',
        'hrv', 'hun', 'hup', 'iba', 'ibo', 'ice', 'ido', 'iii', 'ijo', 'iku', 'ile',
        'ilo', 'ina', 'inc', 'ind', 'ine', 'inh', 'ipk', 'ira', 'iro', 'ita', 'jav',
        'jpn', 'jpr', 'jrb', 'kaa', 'kab', 'kac', 'kal', 'kam', 'kan', 'kar', 'kas',
        'kau', 'kaw', 'kaz', 'kbd', 'kha', 'khi', 'khm', 'kho', 'kik', 'kin', 'kir',
        'kmb', 'kok', 'kom', 'kon', 'kor', 'kos', 'kpe', 'krc', 'kro', 'kru', 'kua',
        'kum', 'kur', 'kut', 'lad', 'lah', 'lam', 'lao', 'lat', 'lav', 'lez', 'lim',
        'lin', 'lit', 'lol', 'loz', 'ltz', 'lua', 'lub', 'lug', 'lui', 'lun', 'luo',
        'lus', 'mac', 'mad', 'mag', 'mah', 'mai', 'mak', 'mal', 'man', 'mao', 'map',
        'mar', 'mas', 'may', 'mdf', 'mdr', 'men', 'mga', 'mic', 'min', 'mis', 'mkh',
        'mlg', 'mlt', 'mnc', 'mni', 'mno', 'moh', 'mol', 'mon', 'mos', 'mwl', 'mul',
        'mun', 'mus', 'mwr', 'myn', 'myv', 'nah', 'nai', 'nap', 'nau', 'nav', 'nbl',
        'nde', 'ndo', 'nds', 'nep', 'new', 'nia', 'nic', 'niu', 'nno', 'nob', 'nog',
        'non', 'nor', 'nso', 'nub', 'nwc', 'nya', 'nym', 'nyn', 'nyo', 'nzi', 'oci',
        'oji', 'ori', 'orm', 'osa', 'oss', 'ota', 'oto', 'paa', 'pag', 'pal', 'pam',
        'pan', 'pap', 'pau', 'peo', 'per', 'phi', 'phn', 'pli', 'pol', 'pon', 'por',
        'pra', 'pro', 'pus', 'que', 'raj', 'rap', 'rar', 'roa', 'roh', 'rom', 'run',
        'rup', 'rus', 'sad', 'sag', 'sah', 'sai', 'sal', 'sam', 'san', 'sas', 'sat',
        'scc', 'scn', 'sco', 'sel', 'sem', 'sga', 'sgn', 'shn', 'sid', 'sin', 'sio',
        'sit', 'sla', 'slo', 'slv', 'sma', 'sme', 'smi', 'smj', 'smn', 'smo', 'sms',
        'sna', 'snd', 'snk', 'sog', 'som', 'son', 'sot', 'spa', 'srd', 'srr', 'ssa',
        'ssw', 'suk', 'sun', 'sus', 'sux', 'swa', 'swe', 'syr', 'tah', 'tai', 'tam',
        'tat', 'tel', 'tem', 'ter', 'tet', 'tgk', 'tgl', 'tha', 'tib', 'tig', 'tir',
        'tiv', 'tkl', 'tlh', 'tli', 'tmh', 'tog', 'ton', 'tpi', 'tsi', 'tsn', 'tso',
        'tuk', 'tum', 'tup', 'tur', 'tut', 'tvl', 'twi', 'tyv', 'udm', 'uga', 'uig',
        'ukr', 'umb', 'und', 'urd', 'uzb', 'vai', 'ven', 'vie', 'vol', 'vot', 'wak',
        'wal', 'war', 'was', 'wel', 'wen', 'wln', 'wol', 'xal', 'xho', 'yao', 'yap',
        'yid', 'yor', 'ypk', 'zap', 'zen', 'zha', 'znd', 'zul', 'zun', 'rum', 'pob',
        'mne' ]

videoSupportedFormat = ['3g2', '3gp', '3gp2', '3gpp', '60d', 'ajp', 'asf', 'asx', 'avchd', 'avi',  
	'bik', 'bix', 'box', 'cam', 'dat', 'divx', 'dmf', 'dv', 'dvr-ms', 'evo',  
	'flc', 'fli', 'flic', 'flv', 'flx', 'gvi', 'gvp', 'h264', 'm1v', 'm2p',  
	'm2ts', 'm2v', 'm4e', 'm4v', 'mjp', 'mjpeg', 'mjpg', 'mkv', 'moov', 'mov',
	'movhd', 'movie', 'movx', 'mp4', 'mpe', 'mpeg', 'mpg', 'mpv', 'mpv2', 'mxf',
	'nsv', 'nut', 'ogg', 'ogm', 'omf', 'ps', 'qt', 'ram', 'rm', 'rmvb', 'swf',  
	'ts', 'vfw', 'vid', 'video', 'viv', 'vivo', 'vob', 'vro', 'wm', 'wmv', 'wmx',  
	'wrap', 'wvx', 'wx', 'x264', 'xvid']

