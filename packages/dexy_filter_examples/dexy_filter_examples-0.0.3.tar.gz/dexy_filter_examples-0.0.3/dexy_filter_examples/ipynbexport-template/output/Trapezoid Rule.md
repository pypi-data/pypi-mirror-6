## Basic Numerical Integration: the Trapezoid Rule

A simple illustration of the trapezoid rule for definite integration:

$$
\int_{a}^{b} f(x)\, dx \approx \frac{1}{2} \sum_{k=1}^{N} \left( x_{k} - x_{k-1} \right) \left( f(x_{k}) + f(x_{k-1}) \right).
$$
<br>
First, we define a simple function and sample it between 0 and 10 at 200 points

Choose a region to integrate over and take only a few points in that region

Plot both the function and the area below it in the trapezoid approximation

![Description](cell-7-output-0.png)

Compute the integral both at high accuracy and with the trapezoid approximation
The integral is: 680.0 +/- 7.54951656745e-12
The trapezoid approximation with 6 points is: 621.286411141
