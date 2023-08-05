#
# Copyright John Reid 2010, 2012
#

"""
Stores filenames for test data and potential starting seeds for each data set.
"""

import os
from cookbook.cache_decorator import cachedmethod

from pkg_resources import resource_filename
fasta_dir = resource_filename('stempy', 'test/fasta')


data_sets = [
    'T00759-tiny',
    'T00759-small',
    'dm01r',
    'yst09m',
    #'T00671',
    'T00759',
    'T99002',
    'T99003',
    'T99004',
    'T99005',
    'T99006',
]
"The data sets."


tiny_data_sets = [
    'T00759-tiny',
    'T00759-small',
]
"Tiny data sets."


small_data_sets = [
    'T00759-tiny',
    'T00759-small',
    'dm01r',
    'yst09m',
]
"Small data sets."


large_data_sets = [
    'T00759',
    'T99002',
    'T99003',
    'T99004',
    'T99005',
    'T99006',
]
"Large data sets."


encode_data_sets = [
    'SRF',  # 700Kb - see Jaspar
    'ZBTB33',  # 1600Kb - see UniProbe
    'RXRA',  # 8000Kb - see UniProbe
    'TCF12',  # 13000Kb - see UniProbe
    'CTCF',  # 13700Kb - see Jaspar
]
"Larger data sets from ENCODE."


fasta_filenames = {
    'T00759-tiny': os.path.join(fasta_dir, 'T00759-tiny.fa'),
    'T00759-small': os.path.join(fasta_dir, 'T00759-small.fa'),
    'dm01r': os.path.join(fasta_dir, 'dm01r.fasta'),
    'yst09m': os.path.join(fasta_dir, 'yst09m.fasta'),
    'T00671': '/home/john/Data/GappedPssms/apr-2009/T00671trimRM.fa',
    'T00759': '/home/john/Data/GappedPssms/apr-2009/T00759trimRM.fa',
    'T99002': '/home/john/Data/GappedPssms/apr-2009/T99002trimRM.fa',
    'T99003': '/home/john/Data/GappedPssms/apr-2009/T99003trimRM.fa',
    'T99004': '/home/john/Data/GappedPssms/apr-2009/T99004trimRM.fa',
    'T99005': '/home/john/Data/GappedPssms/apr-2009/T99005trimRM.fa',
    'T99006': '/home/john/Data/GappedPssms/apr-2009/T99006trimRM.fa',
    'SRF': '/home/john/Data/ENCODE/TF-ChIP/peaks/peaks-SRF.fa',
    'ZBTB33': '/home/john/Data/ENCODE/TF-ChIP/peaks/peaks-ZBTB33.fa',
    'RXRA': '/home/john/Data/ENCODE/TF-ChIP/peaks/peaks-RXRA.fa',
    'TCF12': '/home/john/Data/ENCODE/TF-ChIP/peaks/peaks-TCF12.fa',
    'CTCF': '/home/john/Data/ENCODE/TF-ChIP/peaks/peaks-CTCF.fa',
}
"The filenames of the FASTA files for the data sets."


starts = {
    'T00759-tiny': [
        ('AAAATA', 2, 13.15),
        ('AATTTA', 4, 30.45),
        ('GGAGGA', 8, 57.26),
        ('GGAGGA', 16, 95.46),
        ('GGAGGA', 20, 114.04),
        ('ATAAATTT', 2, 17.53),
        ('AGTCAGAG', 4, 32.81),
        ('AGTCAGAG', 8, 64.43),
        ('CGGGAGGA', 16, 99.18),
        ('CTGTGACT', 20, 112.37),
        ('GAGAATTTAAG', 2, 20.48),
        ('GTGAATTTAAG', 4, 39.61),
        ('CCGAGTCAGGG', 8, 68.66),
        ('CCTCCCCAGCC', 16, 107.11),
        ('CCTCCCCAGCC', 20, 117.90),
        ('ATAGTCCACATAAAA', 2, 25.95),
        ('ATAGTCTCAATGTAT', 4, 49.70),
        ('CAGAGGCTTGGCAAG', 8, 75.79),
        ('TCACCTGTGACTCGG', 16, 103.62),
        ('CTAGTCAGAGTAAAC', 20, 117.82),
    ],
    'T00759-small': [
        ('AAAAAA', 2, 13.04),
        ('AAAAAA', 4, 30.24),
        ('AAAAAT', 8, 64.64),
        ('AAGCAG', 16, 128.27),
        ('TTTCTX', 32, 215.00),
        ('AAGCAG', 50, 290.81),
        ('AAAATTAA', 2, 17.39),
        ('TAAAATTA', 4, 40.32),
        ('TGAATTAA', 8, 73.73),
        ('CAGCCCTG', 16, 132.22),
        ('CAGCACTG', 32, 228.50),
        ('CAGCACTG', 50, 302.61),
        ('TAAATAAAATT', 2, 22.75),
        ('TAATTTTAAAT', 4, 46.68),
        ('AAAAATTCTGA', 8, 85.56),
        ('GGGGCGGGGCT', 16, 141.18),
        ('GTCAGCCCTGA', 32, 227.92),
        ('AGGGGCCAGGG', 50, 318.04),
        ('ATGCAGAAAAATTAA', 2, 28.29),
        ('CCACCCACACACCTT', 4, 54.32),
        ('CAGGGTCAGGGGAGG', 8, 100.66),
        ('CAGGGTCAGGGGAGG', 16, 168.40),
        ('CCTCCTCTCTCCCTG', 32, 248.18),
        ('CCTCCTCTCTCCCTG', 50, 334.39),
    ],
    'dm01r': [
        ('CCCGGC', 2, 14.64),
        ('CCGGCG', 4, 33.45),
        ('CAGCGC', 8, 68.28),
        ('AGCAGC', 16, 126.80),
        ('AGCAGC', 20, 145.67),
        ('CAGGCGCC', 2, 18.45),
        ('GCGCTGCC', 4, 43.05),
        ('CGCAGGCG', 8, 78.86),
        ('GCTGCTGC', 16, 138.27),
        ('CGCTGCCG', 20, 158.53),
        ('CAGCGGCTGCG', 2, 24.70),
        ('CAGCGGCTGCG', 4, 50.68),
        ('CGCCGCCGCCG', 8, 90.47),
        ('GTCGCGACCGC', 16, 145.54),
        ('CGCTGCCACCG', 20, 165.35),
        ('GCGCCGCCGCCGCCG', 2, 32.12),
        ('GCTGCCGTCGCCGGC', 4, 62.27),
        ('GCGCCGCCGCCGCCG', 8, 109.69),
        ('GCGCCGCCGCCGCCG', 16, 170.41),
        ('CGCCGCCGCCGCCGA', 20, 179.56),
    ],
    'yst09m': [
        ('CCGCCG', 2, 15.59),
        ('CCGCCG', 4, 35.34),
        ('CCGCCG', 8, 74.70),
        ('GCCGCC', 16, 130.83),
        ('GAAGAA', 32, 246.56),
        ('GAAAAA', 50, 370.14),
        ('CCGGCGGC', 2, 20.79),
        ('AGCCGCCG', 4, 45.11),
        ('CCGGCGGC', 8, 85.70),
        ('TAGCCGCC', 16, 147.87),
        ('AAAAGGGT', 32, 244.84),
        ('AAAGAAGA', 50, 346.85),
        ('CGGTGAGGAGC', 2, 24.82),
        ('TAGCCGCCGAA', 4, 50.48),
        ('TAGCCGCCGAA', 8, 93.58),
        ('AAAGAGGGCAG', 16, 151.32),
        ('TGAAAAAGAAA', 32, 248.60),
        ('GAAAAGAAAAA', 50, 340.18),
        ('CTAGCCGCCGACGAC', 2, 29.38),
        ('TAGCCGCCGAAACGG', 4, 58.31),
        ('AGCCGCCGAAAACAA', 8, 97.48),
        ('CATTCTTTTTTTCAC', 16, 155.01),
        ('AGAAGAACAAGAAAG', 32, 245.39),
        ('AATTTTCTGTCGTTG', 50, 336.60),
    ],
    'T00759': [
        ('AAAAAAAT', 2, 1.86),
        ('AAAAAAAT', 4, 1.86),
        ('AAAAAAAT', 8, 5.45),
        ('AAAAAAAT', 16, 1.71),
        ('AAAGAAAA', 32, 4.39),
        ('GGGAGGGA', 64, 2.30),
        ('XCAGGGAG', 128, 0.08),
        ('CTCTGCXX', 256, 8.79),
        ('XXXAAAAG', 500, 0.00),
        ('AAAAAATAAAA', 2, 6.11),
        ('AAATAAAATTA', 4, 3.57),
        ('AAATAAAATTA', 8, 5.47),
        ('ATCCTGTTCTC', 16, 1.47),
        ('AGATGGACTGG', 32, 1.92),
        ('CTCCCTGCCCC', 64, 5.10),
        ('CTCCCTGCCCC', 128, 1.03),
        ('TCCCTGCCCCA', 256, 3.47),
        ('XXXXXXAAAAG', 500, 3.76),
        ('AAATAATATTTAAAA', 2, 4.84),
        ('AAATAATATTTAAAA', 4, 4.76),
        ('AAAAAATTAGAAACT', 8, 1.34),
        ('GCATCCTGTTCTCCA', 16, 3.42),
        ('GGGTGAGCACAGGCA', 32, 4.33),
        ('GGTGCAGGGAGAGGG', 64, 1.74),
        ('GGGGGCGGGGCTGGG', 128, 1.70),
        ('CCACCCCCTTCTCCC', 256, 2.18),
        ('XXXXXXXXXXAAAAG', 500, 5.43),
        ('AAATAATATTTAAAAATGAA', 2, 4.01),
        ('AAATAATATTTAAAAATGAA', 4, 1.07),
        ('AAAAAATTAGAAACTATGTA', 8, 2.22),
        ('ACAGGTGGCCTGGAAAGATC', 16, 1.03),
        ('CTCTGCCTCCTCTGGTCTCA', 32, 2.34),
        ('CACCTGAGGGCGCCCCAAGC', 64, 2.41),
        ('TTCCTCCTCTCTCCCTGCCC', 128, 6.68),
        ('CTCCCTXXXXXXXXXXXXXX', 256, 1.01),
        ('TCCTGCCCCGCCCCCTCCTC', 500, 1.37),
    ],
    'T99002': [
        ('AAAAAAAA', 2, 8.96),
        ('AAAAAAAA', 4, 8.96),
        ('AAAAAAAA', 8, 8.96),
        ('AAAAAAAA', 16, 8.96),
        ('AAAAGGAA', 32, 1.19),
        ('AACTACAA', 64, 2.11),
        ('ACAGGAAG', 128, 5.01),
        ('AGGAAGTG', 256, 1.13),
        ('CACTTCCX', 500, 3.44),
        ('AAAAAAAAAAA', 2, 0.00),
        ('AAAAAAAAAAA', 4, 0.00),
        ('AAAAAAAAAAA', 8, 0.00),
        ('AAAAAAAAAAA', 16, 0.00),
        ('ACTACAACTCC', 32, 2.51),
        ('ACTACAACTCC', 64, 1.86),
        ('ACTACAATTCC', 128, 0.00),
        ('ACTACAATTCC', 256, 0.00),
        ('CACTTCCXXXX', 500, 0.00),
        ('AAAAAAAAAAAAAAA', 2, 0.00),
        ('AAAAAAAAAAAAAAA', 4, 0.00),
        ('AGAAAAAAAAAAAAA', 8, 0.00),
        ('GAACTACATTTCCCA', 16, 0.00),
        ('GAACTACATTTCCCA', 32, 0.00),
        ('AACTACAACTCCCAG', 64, 0.00),
        ('AACTACAATTCCCAG', 128, 0.00),
        ('GAACTACAATTCCCA', 256, 0.00),
        ('CACTTCCXXXXXXXX', 500, 0.00),
        ('AATTTCAAAAAAAAAAAAAA', 2, 0.00),
        ('AGTAGGAAGTGTGTCATGAT', 4, 0.00),
        ('AGTAGGAAGTATGTCATGAT', 8, 0.00),
        ('ACAGTAGGAAGTGTGTCATG', 16, 0.00),
        ('AACTACAAGTCCCAGGAGGC', 32, 0.00),
        ('GCCTTCTGGGAGTTGTAGTT', 64, 0.00),
        ('GCATTCTGGGAATTGTAGTT', 128, 0.00),
        ('GCATTCTGGGAATTGTAGTT', 256, 0.00),
        ('GACTACAACTCCCAGAAGGC', 500, 0.00),
    ],
    'T99003': [
        ('AAAAAAAA', 2, 6.32),
        ('AAAAAAAA', 4, 6.32),
        ('AAAAAAAA', 8, 4.15),
        ('AAAAAAAA', 16, 4.28),
        ('AAAAAAAA', 32, 1.73),
        ('ATTCAGCA', 64, 0.00),
        ('TGCTGAAA', 128, 0.00),
        ('TGCTGAAA', 256, 0.00),
        ('GTGCTGAA', 500, 0.00),
        ('AAAAAAAAAAA', 2, 1.28),
        ('AAAAAAAAAAA', 4, 3.58),
        ('AAAAAAAAAAA', 8, 1.30),
        ('AGTGCTGAAAT', 16, 0.00),
        ('AAGGTGCTGAA', 32, 0.00),
        ('TGGTGCTGAAA', 64, 0.00),
        ('ACCATGGACAG', 128, 0.00),
        ('ACCATGGACAG', 256, 0.00),
        ('ACCAGGGACAG', 500, 0.00),
        ('AAAAAAAAAAAAAAT', 2, 5.94),
        ('TCCAAGGTTCTGAAA', 4, 0.00),
        ('ACTGTCCATGGTTCT', 8, 0.00),
        ('TCAGAACCATGGACA', 16, 0.00),
        ('TCAGCACCAAGGACA', 32, 0.00),
        ('CAGCACCATGGACAG', 64, 0.00),
        ('CAGCACCACGGACAG', 128, 0.00),
        ('CAGCACCAGGGACAG', 256, 0.00),
        ('CAGCACCATGGACAG', 500, 0.00),
        ('AGAAAACAAACAAACAAAAA', 2, 3.13),
        ('CTCTGTCCTTGGTGCTGAAA', 4, 0.00),
        ('GGCGCTGTCCGCGGTGCTGA', 8, 0.00),
        ('GGCGCTGTCCGCGGTGCTGA', 16, 0.00),
        ('GGCGCTGTCCGCGGTGCTGA', 32, 0.00),
        ('TCAGCACCACGGACAXXXXX', 64, 0.00),
        ('GGCGCTGTCCCTGGTGCTGA', 128, 0.00),
        ('GGCGCTGTCCTCGGTGCTGA', 256, 0.00),
        ('GGCGCTGTCCATGGTGCTGA', 500, 0.00),
    ],
    'T99004': [
        ('AAAAAAAA', 2, 1.54),
        ('AAAAAAAA', 4, 1.54),
        ('AAAAAAAA', 8, 2.36),
        ('AAAAAAAA', 16, 1.38),
        ('AAAAAAAA', 32, 3.52),
        ('AAAAAAAA', 64, 5.20),
        ('AGGAAATG', 128, 1.26),
        ('TCCAGGAA', 256, 6.14),
        ('TCCAGGAA', 500, 5.37),
        ('AAAAAAAAAAA', 2, 2.66),
        ('AAAAAAAAAAA', 4, 1.63),
        ('AAAAAAAAAAA', 8, 4.38),
        ('AAAAAAAAAAA', 16, 2.00),
        ('ATTTCCAGGAA', 32, 0.00),
        ('ATTTCCAGGAA', 64, 0.00),
        ('ACTTCCAGGAA', 128, 0.00),
        ('TTTCCTGGAAA', 256, 0.00),
        ('TTTCCCGGAAT', 500, 0.00),
        ('AAAAAAAAAAAAAAA', 2, 5.89),
        ('AAAAAAAAAAAAAAA', 4, 3.64),
        ('AAAAAAAAAAAAAAA', 8, 3.47),
        ('AAAAAAAAAAAAAAA', 16, 3.70),
        ('GCCATCTGGTGGCCA', 32, 6.88),
        ('GCCCCCTGGTGGCCA', 64, 1.21),
        ('GTGCCCTCTGGTGGC', 128, 1.63),
        ('GCCCCCTGGTGGCCA', 256, 3.61),
        ('GACTTCCGGGAAATG', 500, 0.00),
        ('ATCTTTTTTTTTTTTTTAAA', 2, 8.61),
        ('GGATAAAAAAAAAAAAAAAA', 4, 9.27),
        ('ACTACAGTTCCCAGCATGCC', 8, 0.00),
        ('GACTACACTTCCCAGGAGGC', 16, 0.00),
        ('GCATGCTGGGACTTGTAGTC', 32, 0.00),
        ('ATGGTGCCCCCTGGTGGCCA', 64, 0.00),
        ('TGGTGCCCCCTGGTGGCCAA', 128, 0.00),
        ('TGGTGCCCCCTGGTGGCCAA', 256, 1.16),
        ('XXXXXXXXXXXTTCTGGAAA', 500, 0.00),
    ],
    'T99005': [
        ('CCCCCCCC', 2, 9.38),
        ('CCCCGCCC', 4, 2.29),
        ('CCCACCCC', 8, 6.19),
        ('CCCACCCC', 16, 2.87),
        ('CCAGGAAA', 32, 2.08),
        ('TCCAGGAA', 64, 0.00),
        ('TCTCAGAA', 128, 0.00),
        ('TCCAGGAA', 256, 0.00),
        ('TCCAAGAA', 500, 0.00),
        ('CCCCCACCCCC', 2, 1.56),
        ('AGGGGTGGGGG', 4, 1.25),
        ('AGTTCCTGGAA', 8, 0.00),
        ('ATTTCCTGGAA', 16, 0.00),
        ('ATTTCCTGGAA', 32, 0.00),
        ('GTTCCAGGAAA', 64, 0.00),
        ('ATTTCTAAGAA', 128, 0.00),
        ('GTTCCTAGAAA', 256, 0.00),
        ('ATTTCCAAGAA', 500, 0.00),
        ('CCCCCCCCCCACCCC', 2, 3.11),
        ('CCCCCCCCCCACCCC', 4, 4.88),
        ('TCCCCCCCCCCACCC', 8, 5.83),
        ('CAGTTCCTAGAACTG', 16, 0.00),
        ('GAGTTCCTAGAAATG', 32, 0.00),
        ('CTGAGTTCCTAGAAA', 64, 0.00),
        ('CTTTTCTAAGAACTG', 128, 0.00),
        ('TTTTCTAAGAACTGA', 256, 0.00),
        ('TTTCTAAGAAGTCCG', 500, 0.00),
        ('GGGGCTGAGCTTTGTCAGGG', 2, 6.53),
        ('ACTGAGTTCCTAGAAATGCC', 4, 0.00),
        ('ACACAAAGCAACTGAGTTCC', 8, 9.04),
        ('AACCGGGTTCCAGGAAATGC', 16, 0.00),
        ('CAACCGGGTTCCAGGAAATG', 32, 0.00),
        ('ACTGAGTTCCTAGAAATGCC', 64, 0.00),
        ('CTGAGTTCCTAGAAATGCCT', 128, 0.00),
        ('AAAGGATTTCTCAGAAAAGA', 256, 0.00),
        ('GATTTCTTAGAAATGAGCTC', 500, 0.00),
    ],
    'T99006': [
        ('CCCCGCCC', 2, 2.06),
        ('CCCCGCCC', 4, 4.19),
        ('CCTGGAAC', 8, 3.21),
        ('TCTCAGAA', 16, 1.24),
        ('TCTGAGAA', 32, 1.47),
        ('TCTGAGAA', 64, 6.99),
        ('TCTCAGAA', 128, 1.19),
        ('TCCGAGAA', 256, 1.90),
        ('XXXXXTGG', 500, 3.61),
        ('GCCGCGCGCGC', 2, 0.19),
        ('CTTCTCAGAAG', 4, 1.33),
        ('TTCTCAGAAAA', 8, 8.64),
        ('TGTTCTGAGAA', 16, 4.25),
        ('TTCTCAGAAAA', 32, 6.08),
        ('TTTCTCAGAAA', 64, 1.41),
        ('TTCTACGAAAC', 128, 7.79),
        ('ATTTCCCAGAA', 256, 5.26),
        ('TTTCCCAGAAA', 500, 1.89),
        ('GCCCTCCCGGCCGGC', 2, 0.00),
        ('CTGCTTCTGAGAAGA', 4, 6.12),
        ('TAATTCTCAGAAGAG', 8, 2.46),
        ('TTCTCTTCTCAGAAG', 16, 5.45),
        ('CTTTTCTGAGAAAAG', 32, 3.83),
        ('CGCTTTTCTAAGAAG', 64, 2.78),
        ('CCGCTTTTCTAAGAA', 128, 1.63),
        ('CCGCTTTTCTAAGAA', 256, 1.02),
        ('CTGXXXXXXXXXXXX', 500, 8.52),
        ('GCGGCGCGCTCCGCAGCGCC', 2, 0.00),
        ('TTTTTCTGGGAAATGGCTGG', 4, 7.31),
        ('TCTGATTTCTCAGAAAATAA', 8, 1.78),
        ('TGTGCTCATTTCTCAGAACA', 16, 7.56),
        ('TTCTTAGAAATGCCAACTCA', 32, 1.02),
        ('CCCCGCTTTTCTAAGAAGTC', 64, 3.29),
        ('TTTCTCAGAACAGAGGGAAA', 128, 7.51),
        ('TTCTGAGAAAAGGAAGAAAA', 256, 1.71),
        ('XXXXXXXXXXXXXXXXXCAG', 500, 1.24),
    ],
    'SRF': [
        ('AAAAAAAA', 2, 553.49),
        ('AAAGGAAA', 4, 7342.66),
        ('CCATATAA', 8, 0.49),
        ('CCATATAA', 16, 0.49),
        ('ATAAGGAA', 32, 16092.09),
        ('ATAAGGAA', 64, 1912604.72),
        ('ACAGGAAG', 128, 5224144.99),
        ('ACAGGAAG', 256, 5224144.99),
        ('TCAGGGAA', 500, 2633253.49),
        ('AAATAGGTAAA', 2, 9.73),
        ('ATATAAGGTAA', 4, 9.73),
        ('CATATAAGGCA', 8, 1.12),
        ('CATATAAGGTA', 16, 1.09),
        ('TTCCTTATTAG', 32, 4.57),
        ('AAATAAGGAAG', 64, 0.03),
        ('TTTCCCTGTCT', 128, 7855386.54),
        ('AGAGACAGGAA', 256, 6939143.85),
        ('AAATTTACCATATAA', 2, 0.03),
        ('TACCATATAAGGTAA', 4, 2.45),
        ('TTGCCTTATATGGTA', 8, 9.05),
        ('TGCCTTATTTGGCAA', 16, 1.42),
        ('TTTCCAAATAAGGAA', 32, 4.21),
        ('TTACCATATAAGGTA', 64, 2.43),
        ('TGCCCAAATAAGGCA', 128, 2.95),
        ('CCCTGCCCCAGCTGG', 256, 1.47),
        ('AATTTACCATATAAGGTAAA', 2, 1.49),
        ('ATTTACCATATAAGGTAAAT', 4, 10.00),
        ('CTTGCCTTATATGGTAGCAC', 8, 4.45),
        ('TTCCCGTATAAGGCAATTTA', 16, 1.30),
        ('ACATTTCCAAATAAGGAAGA', 32, 1.93),
        ('TGTCTTTGCTTTGCTTCCAC', 64, 1809588.61),
        ('CCATATAAGGCAGTGAACTT', 128, 12.18),
    ],
    'ZBTB33': [
        ('AAAAAAAT', 2, 2569925.90),
        ('AAAAACTA', 4, 6.02),
        ('AATGGAAT', 8, 3.47),
        ('AACCCTAA', 16, 8.32),
        ('AACCCTAA', 32, 3.07),
        ('AACCCTAA', 64, 2.12),
        ('CCCTAACC', 128, 1.53),
        ('CCCTAACC', 256, 1.95),
        ('CCCTAACC', 500, 1.23),
        ('AAAAAAATAAA', 2, 1129982.84),
        ('AATGGAATGGA', 4, 5.58),
        ('AATGGAATGGA', 8, 5.58),
        ('CCTAACCCTAA', 16, 4.44),
        ('CCTAACCCTAA', 32, 1.21),
        ('CCTAACCCTAA', 64, 3.10),
        ('AACCCTAACCC', 128, 0.00),
        ('ACCCTAACCCT', 256, 0.00),
        ('ACCCTAACCCT', 500, 0.00),
        ('TTAATTAATTAATGC', 2, 731213.32),
        ('AACCCTAACCCTTAA', 4, 9.30),
        ('TAACCCTAACCCTAA', 8, 8.26),
        ('TAACCCTAACCCTAA', 16, 1.67),
        ('TAACCCTAACCCTAA', 32, 1.98),
        ('CCCTAACCATAACCC', 64, 0.00),
        ('CCCTAACCCCAACCC', 128, 0.00),
        ('ACCCTAACCCTAACC', 256, 0.00),
        ('CCTAACCCTAACCCT', 500, 4.27),
        ('ATACTTCCTTTTCCACCATA', 2, 5.30),
        ('AACCCTAACCCTAACCCTAA', 4, 0.00),
        ('AACCCTAACCCTAACCCTAA', 8, 0.00),
        ('AACCCTAACCCTAACCCTAA', 16, 0.00),
        ('AACCCTAACCCTAACCCTAA', 32, 0.00),
        ('CCCTAACCCGAACCCGAACC', 64, 0.00),
        ('ACCTAACCCTAACCCTAACC', 128, 0.00),
        ('CCTAACCCTAACCCTCACCC', 256, 3.12),
        ('TCTCCACCCTTATCACAACA', 500, 0.00),
    ],
    'RXRA': [
        ('AAAAAAAA', 2, 1388.79),
        ('AAAAAAAA', 4, 287.95),
        ('AATGGAAT', 8, 5.14),
        ('AATGGAAT', 16, 5.14),
        ('CAGGGGTC', 32, 1.42),
        ('CAGGGGTC', 64, 1.67),
        ('CAGGGGTC', 128, 4.60),
        ('GCAGGGGC', 256, 47061772.34),
        ('CCCCTGCT', 500, 25611645.39),
        ('AAAAAAAAAAA', 2, 4.28),
        ('AAAAAAAAAAA', 4, 7.39),
        ('AATGGAATGGA', 8, 3.69),
        ('CCAGGGGTCAC', 16, 1.22),
        ('CCAGGGGTCAT', 32, 1.32),
        ('ACCAGGGGTCA', 64, 3.16),
        ('ACCAGGGGTCA', 128, 1.69),
        ('CCAGGGGTCAC', 256, 2.40),
        ('CCTCTTGCTCA', 500, 4.09),
        ('AAAAAAAAAAAAAAA', 2, 1.27),
        ('AAAAAAAAAAAAAAA', 4, 1.81),
        ('GAATGGAATGGAATG', 8, 7.70),
        ('CCAGGGGTCACGGCT', 16, 5.50),
        ('CCAGGGGTCACAGCT', 32, 2.30),
        ('GGGGTCACGGCTGTG', 64, 1.26),
        ('GCCCCCTGCTGGCAG', 128, 1.10),
        ('CCTCTTGCTCACAGT', 256, 5.63),
        ('CCTCTTGCTCACAGT', 500, 6.49),
        ('AAAAAAAAAAAAAAACCAAA', 2, 9.61),
        ('GAATGGAATGGAATGGAAAG', 4, 1.27),
        ('ACCCAAGGGTCATGGCTGTG', 8, 5.46),
        ('GGCAGGGCATCCAGGGGTCA', 16, 2.69),
        ('ACCCAGGGGTCACGGCTGTG', 32, 2.06),
        ('ATCCAGGGGTCACGGCTGTG', 64, 2.06),
        ('ACCCAGGGGTCACGGCTGTG', 128, 6.60),
        ('CATGGCTGTGTGGTGGGGGC', 256, 4.09),
    ],
    'TCF12': [
        ('AATTTTAT', 2, 1667471.52),
        ('AACAAAAA', 4, 82311.21),
        ('AATGGAAT', 8, 3.99),
        ('CCATTCCA', 16, 2.05),
        ('CTCTTGCT', 32, 4.75),
        ('CCTCCTGC', 64, 1.02),
        ('TGCTGACA', 128, 1.73),
        ('CAGCAGGG', 256, 8.23),
        ('TGCAGGGG', 500, 16.04),
        ('AAACAAACAAA', 2, 0.03),
        ('ATTGTGACATA', 4, 2.21),
        ('TTGTGACATAT', 8, 2.66),
        ('CCTCTTGCTGA', 16, 5.26),
        ('CCTGCAGGCAG', 32, 8.12),
        ('CCTGCTGGCAG', 64, 8.12),
        ('CCTGCTGGCAG', 128, 8.04),
        ('TGCTTGCAGTG', 256, 4.22),
        ('TGGTGGCAGTG', 500, 3.03),
        ('AAACAAACAAAAAAA', 2, 9.99),
        ('TTGTGACATATCTCT', 4, 7.53),
        ('ACATAACTCTGCACT', 8, 1.19),
        ('CAGGGCCCTCTTGCT', 16, 3.54),
        ('CAGGGCCCTCTTGCT', 32, 3.54),
        ('CCCGCCTGCTGGCAG', 64, 5.34),
        ('CCACCTGCTGGCAGC', 128, 2.84),
        ('TGCCTACAGGGGAAT', 256, 2.57),
        ('AAAAAACAAACAAACAAAAA', 2, 1.97),
        ('ACATATCTCTGCACTGATCA', 4, 2.46),
        ('AGACATATCTCTGCACTGAT', 8, 3.02),
        ('CCTGCTGGCAGCTGGAGACA', 16, 1.03),
        ('CACTGCAGGGCCCTGTTGCT', 32, 1.42),
        ('CCTCTTGCTTACAGTGGTGG', 64, 2.21),
        ('CCCTCTTGCTTGCAGTGTAG', 128, 5.85),
        ('CCCTCTTGCTCACAGTATAG', 256, 4.47),
    ],
    'CTCF': [
        ('AAAAAATT', 2, 35682.52),
        ('AAAATAAT', 4, 68708.09),
        ('AGTGTAGT', 8, 5.87),
        ('CTCTTGCT', 16, 1.32),
        ('CTCTTGCT', 32, 2.59),
        ('CCCTTGCT', 64, 2.59),
        ('CCCTTGCT', 128, 1.14),
        ('CCCCTGCT', 256, 7.86),
        ('CCCCTGCT', 500, 1.61),
        ('AATTATTTAAA', 2, 199.31),
        ('TAATCTGAAAA', 4, 4.54),
        ('AGTGTAGTGGC', 8, 8.45),
        ('TGCTGGCAGCT', 16, 2.06),
        ('GTTCTCTTGCT', 32, 2.99),
        ('CCCCCTGCTGG', 64, 1.61),
        ('GCCCCCTGCTG', 128, 1.14),
        ('GCCCCCTGCTG', 256, 7.30),
        ('GCCCCCTGCTG', 500, 4.68),
        ('AAATAATTATTTAAA', 2, 0.61),
        ('CTTGCTCACAGTGTA', 4, 3.68),
        ('CCTGCTGGCAGCTGG', 8, 8.22),
        ('TGGCAGCTAAGGACA', 16, 3.18),
        ('CAGGGCCCTGTTACT', 32, 4.80),
        ('TCTCTTGCTCGCAGT', 64, 1.79),
        ('CCCCTTGCTTGCAGC', 128, 6.49),
        ('CCTCTTGCTTGCAGT', 256, 1.75),
        ('AGATTAACTCTGTTCTGTTT', 2, 9.45),
        ('TGGCAGCTAGGGACATTGCA', 4, 1.52),
        ('GCTGGCAGCTGGGGACACTG', 8, 4.11),
        ('CCTCCTGGCAGCTAAGGACA', 16, 2.23),
        ('AACTGCAGGGTTCTCTTGCT', 32, 2.39),
        ('CACTGCAGGGCCCTCTTGCT', 64, 2.39),
        ('CCCCTTGCTTGCAGCCGGGC', 128, 4.88),
        ('CCTCTTGCTTGCAGTATAGT', 256, 5.94),
    ],
}
"The starts that MEME finds in the data sets."


@cachedmethod
def get_data_set_size(data_set):
    "@return: # seqs, # bases."
    import corebio.seq
    import corebio.seq_io.fasta_io as F
    alphabet = corebio.seq.reduced_nucleic_alphabet
    num_bases = num_seqs = 0
    for seq in F.iterseq(
        open(fasta_filenames[data_set], 'r'),
        alphabet
    ):
        num_seqs += 1
        num_bases += len(seq)
    return num_seqs, num_bases


def get_num_w_mers(data_set, W):
    "@return: # W-mers in the data set."
    num_seqs, num_bases = get_data_set_size(data_set)
    return num_bases - num_seqs * (W - 1)


def add_options(parser):
    parser.add_option(
        "-d", "--data-sets", action="append", help="Run on this data set.")
    parser.add_option(
        "-g", "--groups", action="append", help="Run on this data set group.")


def data_sets_for_options(options):
    if options.data_sets:
        data_set_names = set(options.data_sets)
    else:
        data_set_names = set()
    if options.groups:
        for group in options.groups:
            data_set_names.update(eval('%s_data_sets' % group))
    return data_set_names
