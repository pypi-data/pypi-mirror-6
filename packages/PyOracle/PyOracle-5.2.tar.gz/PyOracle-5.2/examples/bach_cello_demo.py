'''
bach_cello_demo.py
example of symbolic oracle generation

Copyright (C) 12.02.2013 Cheng-i Wang

This file is part of PyOracle.

PyOracle is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyOracle is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyOracle.  If not, see <http://www.gnu.org/licenses/>.
'''

import Resources.PyOracle.FactOracle as fo
import Resources.generate as gen
import music21
import sys
import os

def main():
    filename = os.path.abspath('') + '/Suite_No_1_for_Cello_M1_Prelude.mxl'
    s = music21.converter.parse(filename)
    c = s.getElementById('Violoncello')
    m = c.flat.notes
    note_obj_seq = [x for x in m if type(x) is music21.note.Note]    
    bo = fo.build_oracle(note_obj_seq, 'f')
    
    if len(sys.argv) == 1:
        b, kend, ktrace = gen.generate(bo, len(note_obj_seq), 0.0, 0, LRS = 2, weight='weight')
    else:
        seq_len = int(sys.argv[1])
        if seq_len == 0:
            seq_len = len(note_obj_seq)
        p = float(sys.argv[2])
        k = int(sys.argv[3])
        LRS = int(sys.argv[4])
        weight = sys.argv[5]
        b, kend, ktrace = gen.generate(bo, seq_len, p, k, LRS = LRS, weight = weight)

    stream1 = music21.stream.Stream()
    x = [bo.data[i] for i in b]
    for i in range(len(x)):
        _n = music21.note.Note(x[i].nameWithOctave)
        _n.duration.type = x[i].duration.type
        _n.duration = x[i].duration 
        stream1.append(_n)

    s.show()
    stream1.show()
    
if __name__ == '__main__':
    main()
