# PseudoPy

PseudoPy computes and visualizes the pseudospectrum of a matrix. It is a Python version of the original [eigtool](http://www.cs.ox.ac.uk/pseudospectra/eigtool/) by Thomas G. Wright. The algorithms used in this package can be found in the book [Spectra and pseudospectra](http://press.princeton.edu/titles/8113.html) by [Nick Trefethen](http://www.maths.ox.ac.uk/people/profiles/nick.trefethen) and [Mark Embree](http://www.caam.rice.edu/~embree/).

## Example
The pseudospectrum of the Grcar matrix looks like this:

![Pseudospectrum of Grcar matrix](grcar.png)

The above figure can be created with the following lines of code:
```python
from pseudopy import compute, demo, visualize
from matplotlib import pyplot
from scipy.linalg import eigvals

A = demo.grcar(32).todense()

X, Y, Z = compute.evaluate_meshgrid(A,
                                    real_min=-1, real_max=3, real_n=400,
                                    imag_min=-3.5, imag_max=3.5, imag_n=400)

visualize.contour_meshgrid(X, Y, Z,
                           levels=[10**k for k in range(-4, 0)],
                           spectrum=eigvals(A))

pyplot.show()
```
