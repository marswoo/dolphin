# -*- coding: utf-8 -*-
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage:', sys.argv[0], '<fn_input_rawdata><fn_output>'
    else:
        fin = open(sys.argv[1], 'r')
        fout = open(sys.argv[2], 'w')
        n_line_num = 0
        for line in fin:
            n_line_num += 1
            line = line.rstrip('\n')
            items = line.split('\t')
            if len(items) != 7:
                continue
            date = items[0]
            open = float(items[1])
            high = float(items[2])
            low = float(items[3])
            close = float(items[4])
            volume = float(items[5])
            cash = float(items[6])
            if n_line_num == 1:
                last_close = open
            increase = ((close - last_close)/last_close) * 100
            range = ((high - low)/last_close) * 100
            print >> fout, '\t'.join([date, str(increase), str(range)])
            last_close = close
        fin.close()
        fout.close()
