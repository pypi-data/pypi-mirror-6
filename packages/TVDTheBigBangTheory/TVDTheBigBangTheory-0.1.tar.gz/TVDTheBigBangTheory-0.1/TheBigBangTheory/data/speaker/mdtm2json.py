#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN -- http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""Convert MDTM file into TVD Annotation Graph JSON format

Usage:
    mdtm2json <mdtm> <json>

Parameters:
    <mdtm>   Path to MDTM file.
    <json>  Path to JSON file.
"""

from tvd import AnnotationGraph, TAnchored, TStart, TEnd
from pyannote.parser.mdtm import MDTMParser

def mdtm2json(path_to_mdtm, path_to_json):

	# load MDTM
	speech = set(['howard', 'leonard', 'other', 'penny', 'raj', 'sheldon'])
	annotation = MDTMParser().read(path_to_mdtm)().subset(speech)

	# create empty annotation graph
	g = AnnotationGraph()

	# create start node
	t = TStart()

	for segment, _, label in annotation.itertracks(label=True):

		t1 = TAnchored(segment.start)
		t2 = TAnchored(segment.end)

		# in case there is a gap with previous speech turn
		# add an empty edge
		data = {}
		if t < t1:
			g.add_annotation(t, t1, {})

		# add edge
		data['speaker'] = label
		g.add_annotation(t1, t2, data)

		# keep track of last timestamp
		t = t2

	# connect last timestamp with episode end
	g.add_annotation(t, TEnd(), {})

	# dump to JSON
	g.save(path_to_json)


if __name__ == '__main__':

    from docopt import docopt
    ARGUMENTS = docopt(__doc__, version='mdtm2json 0.1')
    mdtm2json(ARGUMENTS['<mdtm>'], ARGUMENTS['<json>'])
