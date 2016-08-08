#!/usr/bin/env python2
# Copyright 2016 The Fontbakery Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
__author__="The Font Bakery Authors"

import os, sys, argparse, glob, logging, requests, subprocess
from fontTools import ttLib
from fontTools.ttLib.tables._n_a_m_e import NameRecord

#=====================================
# GLOBAL CONSTANTS DEFINITIONS

NAMEID_VERSION_STRING = 5

def parse_version_string(s):
    """ Tries to parse a version string as used
        in ttf versioning metadata fields.
        Example of expected format is:
          'Version 01.003; Comments'
    """
    try:
        suffix = ''
        if ';' in s:
            fields = s.split(';')
            s = fields[0]
            fields.pop(0)
            suffix = ';'.join(fields)
        substrings = s.split('.')
        minor = substrings[-1]
        if ' ' in substrings[-2]:
            major = int(substrings[-2].split(' ')[-1])
        else:
            major = int(substrings[-2])
        return major, minor, suffix
    except:
        print ("ER: failed to detect major and minor version numbers" +\
               " in '{}' utf8 encoding: {}".format(s, [s.encode('utf8')]))

# set up some command line argument processing
parser = argparse.ArgumentParser(description="Compare TTF files when upgrading families.")
parser.add_argument('arg_filepaths', nargs='+', 
                    help='font file path(s) to check.'
                         ' Wildcards like *.ttf are allowed.')
parser.add_argument('-v', '--verbose', action='count', default=0, help="increase output verbosity")
parser.add_argument('-b', '--versionbump', action="store_true", help="increment font files' minor version number")

#=====================================
# Main sequence of checkers & fixers

def main():
  # set up a basic logging config
  # to include timestamps
  # log_format = '%(asctime)s %(levelname)-8s %(message)s'
  global font
  log_format = '%(levelname)-8s %(message)s  '
  logger = logging.getLogger()
  handler = logging.StreamHandler()
  formatter = logging.Formatter(log_format)
  handler.setFormatter(formatter)
  logger.addHandler(handler)

  args = parser.parse_args()
  if args.verbose == 1:
    logger.setLevel(logging.INFO)
  elif args.verbose >= 2:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.ERROR)

  #------------------------------------------------------
  import magic
  logging.debug("Checking each file is a ttf")
  fonts_to_check = []
  for arg_filepath in sorted(args.arg_filepaths):
    # use glob.glob to accept *.ttf
    for fullpath in glob.glob(arg_filepath):
      file_path, file_name = os.path.split(fullpath)
      mime = magic.Magic(mime=True)
      mimetype = mime.from_file(fullpath)
      if mimetype == 'application/x-font-ttf':
        logging.debug("'{}' has a ttf mimetype".format(file_name))
        fonts_to_check.append(fullpath)
      else:
        logging.warning("Skipping '{}' as mime was '{}', should be 'application/x-font-ttf')".format(filename, mimetype))
  fonts_to_check.sort()

 #------------------------------------------------------
  for new_file in fonts_to_check:
    logging.debug("Comparison of filesizes")
    old_file = new_file + "-old"
    new_filesize = os.path.getsize(new_file)
    old_filesize = os.path.getsize(old_file)
    delta = new_filesize - old_filesize
    percentage = float(delta) / old_filesize
    if delta>0:
      logging.warning("New font file '{}' is {} bytes larger".format(
                      new_file, delta))
    elif delta<0:
      logging.warning("New font file '{}' is {} bytes smaller".format(
                      new_file, -delta))
    else:
      logging.info("New font file '{}' preserves filesize.".format(new_file))

    new_font = ttLib.TTFont(new_file)
    old_font = ttLib.TTFont(old_file)

    #----------------------------------------------------
    logging.debug("Checking font version fields")
    old_version = parse_version_string(str(old_font['head'].fontRevision))
    if old_version == None:
        logging.error("Could not parse TTF version string on the 'head' table."+\
                      " Please fix it. Current value is '{}'".format(str(old_font['head'].fontRevision)))
    else:
        if args.versionbump:
            minor = old_version[1]
            num_digits = len(minor)
            minor = str(int(minor) + 1)
            minor = '0' * (num_digits - len(minor)) + minor
            incremented_version = [old_version[0], minor, old_version[2]]

            new_version = parse_version_string(str(new_font['head'].fontRevision))
            if new_version != incremented_version:
                logging.warning("Auto-incrementing fontRevision from {}.{} to {}.{}".format(new_version[0], new_version[1],
                                                                                        incremented_version[0], incremented_version[1]))
                new_font['head'].fontRevision = "{}.{}".format(incremented_version[0], incremented_version[1])
            else:
                logging.info("OK: fontRevision is {}.{}".format(new_version[0], new_version[1]))

            for name in new_font['name'].names:
                if name.nameID == NAMEID_VERSION_STRING:
                    encoding = name.getEncoding()
                    s = name.string.decode(encoding)
                    s = "Version {}.{};{}".format(incremented_version[0],
                                                  incremented_version[1],
                                                  incremented_version[2])
                    new_string = s.encode(encoding)
                    if name.string != new_string:
                        logging.info("NAMEID_VERSION_STRING from {} to {}".format(name.string, new_string))
                        name.string = new_string
            if 'CFF ' in new_font.keys():
                major, minor, _ = incremented_version
                if new_font["CFF "].cff.major != major:
                    new_font["CFF "].cff.major = major
                if new_font["CFF "].cff.minor != minor:
                    new_font["CFF "].cff.minor = minor

    new_font.close()
    old_font.close()

if __name__=='__main__':
    main()

