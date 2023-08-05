%%% "assign-vars"
a = 6
b = 8

%%% "multiply"
a*b

%%% "image"
x = 0:pi/100:2*pi;
y = cos(x);
plot(x,y)
title('plot of the cosine function')
print -dpng 'matlab-plot.png'
