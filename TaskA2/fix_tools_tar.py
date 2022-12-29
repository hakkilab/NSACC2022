with open('raw_tools.tar', 'rb') as fin:
    with open('tools.tar', 'wb') as fout:
        fout.write(fin.read()[85:])