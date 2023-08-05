model(I) :- model(I,_).

input(V) :- stimulus(V), clause(_,V,_).
input(V) :- inhibitor(V), clause(_,V,_).

noeffect(V) :- stimulus(V), not input(V).
noeffect(V) :- inhibitor(V), not input(V).
