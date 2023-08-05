maidenhair
=============
A plugin based data load and manimupulate library.

Usage
---------
Assume that there are three kinds of samples and each samples have 5 indipendent
experimental results.
All filenames are written as the following format::

    sample-type<type number>.<experiment number>.txt

And files are saved in `data` directory like::

    +- data
        |
        +- sample-type1.001.txt
        +- sample-type1.002.txt
        +- sample-type1.003.txt
        +- sample-type1.004.txt
        +- sample-type1.005.txt
        +- sample-type2.001.txt
        +- sample-type2.002.txt
        +- sample-type2.003.txt
        +- sample-type2.004.txt
        +- sample-type2.005.txt
        +- sample-type3.001.txt
        +- sample-type3.002.txt
        +- sample-type3.003.txt
        +- sample-type3.004.txt
        +- sample-type3.005.txt

Then, the code for plotting the data will be::

    >>> import matplotlib.pyplot as plt
    >>> import maidenhair
    >>> import maidenhair.statistics
    >>> dataset = []
    >>> dataset += maidenhair.load('data/sample-type1.*.txt', unite=True)
    >>> dataset += maidenhair.load('data/sample-type2.*.txt', unite=True)
    >>> dataset += maidenhair.load('data/sample-type3.*.txt', unite=True)
    >>> nameset = ['Type1', 'Type2', 'Type3']
    >>> for name, (x, y) in zip(nameset, dataset):
    ...     xa = maidenhair.statistics.average(x)
    ...     ya = maidenhair.statistics.average(y)
    ...     ye = maidenhair.statistics.confidential_interval(y)
    ...     plt.errorbar(xa, ya, yerr=ye, label=name)
    ...
    >>> plt.show()

