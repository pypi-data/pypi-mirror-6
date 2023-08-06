`Science VM <http://www.scivm.com>`_ is a scicloud-computing platform that integrates into the Python Programming Language. It enables you to leverage the computing power of your datacenter and/or your choice of scicloud providers without having to manage, maintain, or configure virtual servers.

When using this Python library known as *scicloud*, Science VM will integrate seamlessly into your existing code base. To offload the execution of a function to our servers, all you must do is pass your desired function into the *scicloud* library. ScienceVM will run the function on its high-performance cluster. As you run more functions, our cluster auto-scales to meet your computational needs. 

Before using this package, you will need to sign up a `Science VM <http://www.scivm.com>`_ account.

The *scicloud* library also features a simulator, which can be used without a Science VM account.  The simulator uses the  `multiprocessing <http://docs.python.org/library/multiprocessing.html>`_ library to create a stripped down version of the Science VM service.  This simulated service can then run jobs locally across all CPU cores.

Quick command-line example::
  
	>>> import scicloud
	>>> def square(x):
	...     return x*x
	...     
	>>> jid = scicloud.call(square,3)  #square(3) evaluated on Science VM
	>>> scicloud.result(jid)
	9

Full package documentation is available at http://docs.scivm.com.  Some dependencies may be required depending on your platform and Python version; see INSTALL for more information.

