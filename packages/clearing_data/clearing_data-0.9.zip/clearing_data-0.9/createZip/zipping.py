import gzip
f_in = open(r'C:\Users\ama\Desktop\data2014\Saronikos_Ready\Saronikos_5_1_Dorousa', 'r')
f_out = gzip.open(r'C:\Users\ama\Desktop\file.txt.gz', 'wb')
f_out.writelines(f_in)
f_out.close()
f_in.close()