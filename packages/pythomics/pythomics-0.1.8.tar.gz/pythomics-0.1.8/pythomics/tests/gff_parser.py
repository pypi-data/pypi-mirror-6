__author__ = 'chris'

gff = GFFReader('/home/chris/Dropbox/Pycharm/pythomics/pythomics/tests/sample_gff.gff3')
feature = gff.get_attribute('Name', 'EDEN.1', features=True)[0]
print feature.get_children()

gff = GFFReader('/media/chris/ChrisSSD/Individualome/rnaSeq/transcripts.gtf', key_delimiter=' ', quotechar='"')
feature = gff.get_attribute('gene_id', 'TCONS_00000120')
for i in feature:
    print i
