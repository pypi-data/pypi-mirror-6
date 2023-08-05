PyPrind
=============
The PyPrind (Python Progress Indicator) module provides a progress bar and a percentage indicator  
object that let you track the progress of a loop structure or other iterative computation.  
Typical applications include the processing of large data sets to provide an intuitive estimate 
at runtime about the progress of the computation.



Installation
=============
You can use the following command to install PyPrind:  
`pip install pyprind`  
 or    
`easy_install pyprind`  

Alternatively, you download the package manually from the Python Package Index [https://pypi.python.org/pypi/PyPrind](https://pypi.python.org/pypi/PyPrind), unzip it, navigate into the package, and use the command:

`python setup.py install`  
or  
`python3 setup.py install`  



Documentation
=============
PyPrind consists of two class objects that can visualize the progress of a computation on the output screen.  
Progress bars are visualized via  a `ProgBar()` object, and alternatively, the progress can be tracked and shown as percentage via a `ProgPercent()` object.  

The general usage of `ProgBar()` and `ProgPercent()` consists of three steps:

1) initialize a new `ProgBar()` or `ProgPercent()` object with the number of iterations of the computation that is to be performed  
2) update the `ProgBar()` or `ProgPercent()`  object for each iteration via the `.update() `method  
3) complete the progress visualization via the `.finish()` method after the computation is completed  

<pre>n = 10000000
my_prbar = pyprind.ProgBar(n)   # 1) initialization with number of iterations
for i in range(n):	
    # do some computation
    my_prbar.update()           # 2) update the progress visualization
my_prbar.finish()               # 3) complete the progress visualization
</pre>


Optional parameters :
--------------------------

##### Setting the width of the progress bar
`my_prog = pyprind.ProgBar(n, width=70)	# default = 50`


##### Set whether CPU time should be reported or not 
The optional `cpu_time` parameter can be set for both `ProgBar()` and `ProgPercent()` objects.  
<pre>
my_prbar = pyprind.ProgBar(n)  
 ...
my_prbar.finish(cpu_time=False) # default = True  
</pre>


Examples
=============

The following examples shall illustrate the typical usage of the PyPrind package.  
A visualization can be viewed on YouTube: [http://youtu.be/gjj5K8OWo7U](http://youtu.be/gjj5K8OWo7U)


Example 1 - Progress Bar
--------------------------

<pre>import pyprind

n = 10000000
my_prbar = pyprind.ProgBar(n)
for i in range(n):
    # do some computation
    my_prbar.update()
my_prbar.finish() 
</pre>

**Screen Output**  

<pre>sebastian > python3 examples/ex_progress_bar.py 
0%                                    100%
[########################################]
Time elapsed: 0.7829 sec
</pre>


Example 2 - Percentage Indicator
--------------------------

<pre>import pyprind

n = 1000000
my_perc = pyprind.ProgPercent(n)
for i in range(n):
    # do some computation
    my_perc.update()
my_perc.finish()
 </pre>

**Screen Output**  

<pre>sebastian > ./python3 examples/ex_percentage_indicator.py 
[100 %]
Time elapsed: 2.6364 sec
</pre>

 


 Contact
=============

If you have any questions or comments about PyPrind, please feel free to contact me via  
eMail: [se.raschka@gmail.com](mailto:se.raschka@gmail.com)  
or Twitter: [@rasbt](https://twitter.com/rasbt)
