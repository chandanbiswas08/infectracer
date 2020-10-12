import sys
def rearrange_nn(infile):
    fp = open(infile, 'r')
    lines = fp.readlines()
    fp.close()
    data = {}
    for i in range(len(lines)):
        line = lines[i].split(sep='\t')
        data[int(line[0])] = line[1]
        # if i % 10000 == 0:
        #     print('Reading data %d' % i)

    fp_out = open(infile, 'w')
    for i in range(len(data)):
        fp_out.write('%d\t%s' % (i,data[i]))
        # if i % 10000 == 0:
        #     print('Writing data %d' % i)
    fp_out.close()


if __name__ == "__main__":
    rearrange_nn(sys.argv[1])