{exp(V)} :- input(V).

mapped(V,M) :- formula(V,I), dnf(I,_), model(M,I).
free(V,M) :- not stimulus(V), not exp(V), mapped(V,M).

active(M,V) :- exp(V), stimulus(V), model(M).
active(M,V) :- model(M,I), free(V,M), formula(V,I), dnf(I,J),
               active(M,W) : clause(J,W,1), not active(M,W) : clause(J,W,-1). 

diff :- active(I1,V), not active(I2,V), I1 != I2, readout(V), model(I1;I2).

#hide.
