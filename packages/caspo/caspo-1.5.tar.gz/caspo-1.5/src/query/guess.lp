{dnf(I,J) : hyperedge(I,J,N)} :- formula(V,I).

path(U,V) :- formula(V,I), dnf(I,J), clause(J,U,_).
path(U,V) :- path(U,W), path(W,V).
:- path(V,V).

:- formula(V,I), hyperedge(I,J1,N), hyperedge(I,J2,M), N < M,
   dnf(I,J1), dnf(I,J2), clause(J2,U,S) : clause(J1,U,S).
   
:- formula(V,I), dnf(I,J), clause(J,U,S), clause(J,U,-S).

:- dnf(I,J), clause(J,V,_), not stimulus(V),
   not path(U,V) : stimulus(U).

:- path(_,V), not readout(V), not path(V,U) : readout(U).
