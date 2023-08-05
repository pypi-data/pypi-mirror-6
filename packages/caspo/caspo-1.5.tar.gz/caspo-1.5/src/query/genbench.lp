%size
:- not minsize [dnf(I,J) : hyperedge(I,J,L) = L] maxsize.
%and gates
:- not minnand [dnf(I,J) : L > 1 : hyperedge(I,J,L)] maxnand.

%reach all readouts
%reach(V) :- stimulus(U), dnf(I,J), clause(J,U,_), formula(V,I).
%reach(V) :- reach(U), dnf(I,J), clause(J,U,_), formula(V,I).
reach(V) :- path(_,V).
:- readout(V), not reach(V).

%force pathways starting in stimuli and ending in readouts
:- formula(V,_), not path(U,V) : stimulus(U).
:- path(_,V), not readout(V), not path(V,U) : readout(U).

%minimize unused stimulus
breach(U) :- readout(V), dnf(I,J), clause(J,U,_), formula(V,I).
breach(U) :- breach(V), dnf(I,J), clause(J,U,_), formula(V,I).
unbreach(V) :- stimulus(V), not breach(V).

#minimize[unbreach(_)].
