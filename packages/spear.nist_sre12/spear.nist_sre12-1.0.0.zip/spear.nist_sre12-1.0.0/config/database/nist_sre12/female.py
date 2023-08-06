#!/usr/bin/env python

import xbob.db.nist_sre12

# 0/ The database to use
name = 'sre12'
# put the full path to the database filelist
db = xbob.db.nist_sre12.Database()
protocol = 'female'

# put the full path to the folder that contains the audio files
wav_input_dir = "/idiap/temp/ekhoury/NIST_DATA/"
wav_input_ext = ".sph"

