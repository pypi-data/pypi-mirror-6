# -*- coding: utf-8 -*-
# Copyright © 2013 Carl Chenet <chaica@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import os.path
import stat

from brebis.generatelist.generatelist import GenerateList
from brebis.checkhashes import get_hash

# Generate a list of files from a tree
'''Generate a list of files from a tree'''

class GenerateListForTree(GenerateList):
    '''Generate a list of files from a tree'''

    def __init__(self, __genparams):
        '''The constructor for the GenerateListForTree class'''
        __arcpath = __genparams['arcpath']
        __delimiter = __genparams['delimiter']
        self._genfull = __genparams['genfull']
        self.__listoutput = __genparams['listoutput']
        self.__confoutput = __genparams['confoutput']
        self.__fulloutput = __genparams['fulloutput']
        __listoffiles = ['[files]\n']
        __oneline = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value}\n'.format(value='{}', delimiter=__delimiter)
        __onelinewithhash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} md5{delimiter}{value}\n'.format(value='{}', delimiter=__delimiter)
        __onelinewithtarget = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} md5{delimiter}{value} target{delimiter}{value}\n'.format(value='{}', delimiter=__delimiter)
        
        for __dirpath, __dirnames, __filenames, in os.walk(__arcpath):
            # ignoring the uppest directory
            if os.path.relpath(__dirpath, __arcpath) != '.':
                # studying directories
                __dirinfo = os.lstat(__dirpath)
                __dirmode = oct(stat.S_IMODE(__dirinfo.st_mode)).split('o')[-1]
                # translate file type in brebis intern file type
                __type = self.__translate_type(__dirinfo.st_mode)
                # extract file data
                __listoffiles.append(__oneline.format(
                                        os.path.relpath(__dirpath, __arcpath),
                                        str(__dirinfo.st_size),
                                        str(__dirinfo.st_uid),
                                        str(__dirinfo.st_gid),
                                        __dirmode,
                                        __type,
                                        str(__dirinfo.st_mtime)))
            # studying files
            for __filename in __filenames:
                __filepath = os.path.join(__dirpath, __filename)
                __filepath = self._normalize_path(__filepath)
                self.__fileinfo = os.lstat(__filepath)
                __filemode = oct(stat.S_IMODE(self.__fileinfo.st_mode)).split('o')[-1]
                __type = self.__translate_type(self.__fileinfo.st_mode)
                if __type == 'f': 
                    # extract hash sum of the file inside the archive
                    __hash = get_hash(open(__filepath, 'rb'), 'md5')
                    # extract file data and prepare data
                    __listoffiles.append(__onelinewithhash.format(
                                            os.path.relpath(__filepath, __arcpath),
                                            str(self.__fileinfo.st_size),
                                            str(self.__fileinfo.st_uid),
                                            str(self.__fileinfo.st_gid),
                                            __filemode,
                                            __type,
                                            str(self.__fileinfo.st_mtime),
                                            __hash))
                elif __type == 's':
                    # extract hash sum of the file inside the archive
                    __hash = get_hash(open(__filepath, 'rb'), 'md5')
                    # extract file data and prepare data
                    __listoffiles.append(__onelinewithtarget.format(
                                            os.path.relpath(__filepath, __arcpath),
                                            str(self.__fileinfo.st_size),
                                            str(self.__fileinfo.st_uid),
                                            str(self.__fileinfo.st_gid),
                                            __filemode,
                                            __type,
                                            __hash,
                                            str(self.__fileinfo.st_mtime),
                                            os.readlink(__filepath)))
                else:
                    # if file is not regular file, ignoring its hash sum
                    __listoffiles.append(__oneline.format(
                                            os.path.relpath(__filepath, __arcpath),
                                            str(self.__fileinfo.st_size),
                                            str(self.__fileinfo.st_uid),
                                            str(self.__fileinfo.st_gid),
                                            __filemode,
                                            __type,
                                            str(__fileinfo.st_mtime)))
                                            
        # include custom paths for output conf files
        __reparc = os.path.split(__arcpath)[-1]
        if self.__listoutput:
            __arclistpath = os.path.join(self.__listoutput, ''.join([__reparc, '.list']))
        elif self.__fulloutput:
            __arclistpath = os.path.join(self.__fulloutput, ''.join([__reparc, '.list']))
        else:
            __arclistpath = ''.join([__arcpath, '.list'])
        __listconfinfo = {'arclistpath': __arclistpath,
                            'listoffiles':  __listoffiles}
        # call the method to write information in a file
        self._generate_list(__listconfinfo)
        # call the method to write the configuration file if --gen-full was required
        if self._genfull:
            if self.__confoutput:
                __arcconfpath = os.path.join(self.__confoutput, ''.join([__reparc, '.conf']))
            elif self.__fulloutput:
                __arcconfpath = os.path.join(self.__fulloutput, ''.join([__reparc, '.conf']))
            else:
                __arcconfpath = ''.join([__arcpath, '.conf'])
            # generate the hash sum of the list of files
            __listhashsum = self._get_list_hash(__listconfinfo['arclistpath'])
            __arcname =  os.path.basename(__arcpath)
            # include custom paths for output conf files
            __confinfo = {'arcname': __arcname,
                            'arcpath': __arcpath,
                            'arcconfpath': __arcconfpath,
                            'arclistpath':  __arclistpath,
                            'arctype': 'tree',
                            'sha512': __listhashsum}
            self._generate_conf(__confinfo)

    def __translate_type(self, __mode):
        '''Translate the type of the file to a generic name'''
        if stat.S_ISREG(__mode):
            if self.__fileinfo[stat.ST_NLINK] > 1:
                return 'l'
            else:
                return 'f'
        elif stat.S_ISDIR(__mode):
            return 'd'
        elif stat.S_ISCHR(__mode):
            return 'c'
        elif stat.S_ISLNK(__mode):
            return 's' 
        elif stat.S_ISBLK(__mode):
            return 'b'
        elif stat.S_ISSOCK(__mode):
            return 'k'
        elif stat.S_ISFIFO(__mode):
            return 'o'
        pass
