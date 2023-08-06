======================
Example and Test Files
======================

Legends
=======

- *orig/test_xx.dat* original sample file
- *test_xx/xx_assaved.dat* output file by mui.py, which should be tested and compatible *orig/test_xx.dat*
- *test_xx/xx_assaved.dat.json* output file by mui.py. The .json file can be loaded on mui.py and generates *xx_assaved.dat* directly.
- *test_xx/xx_patched.dat* modified from *xx_assaved.dat* in order to obtain same output as one from *orig/test_xx.dat* . If *xx_patched.dat* does not exist, *xx_assaved.dat* is confirmed to be compatible with its original example.

The differences between *xx_assaved* and *xx_patched* are following. The list indicates the insufficient points of current version of mui.py

test_a1
=======

::

  &MODL.RDNML(4)=T
  &VPAR.BPAR(1,1)=0.0738

test_a2
=======

::

  &MODL.RDNML(4)=T
  &VPAR.BPAR(1,1)=0.0738

test_b1
=======

::

  &MODL.RDNM(2)=T
  &FEHL LVAC=4,RVS=3*1.0,3*2.0,0.5,0.5,0.0,0.0,0.5,0.5,LVS=4*1,
        LINT=4,NS=2*0,3,4,RIS=3*0.5,1.5,0.5,0.5,LIS=2*5,2*4,LS=2*1/L
  &MODL.RDNM(4)=T
  &VPAR.BPAR(1,1)=0.0738

test_b2
=======

::

  &MODL.TIM(7)=F
  &PROJ.NGR=5

test_c1
=======

::

  &MODL.TIM=T,T,F,F,F
