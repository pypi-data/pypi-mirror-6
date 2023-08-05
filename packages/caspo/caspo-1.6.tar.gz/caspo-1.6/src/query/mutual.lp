odnf(J,O) :- O = [inmodel(_,J)], dnf(I,J).
inmodel(N,J) :- model(N,I), dnf(I,J), formula(_,I).

notall(J) :- odnf(J,O), nmodels(N), O<N.

exclusive(J1,J2) :- notall(J1), notall(J2), 
                    not inmodel(N,J2) : inmodel(N,J1),
                    not inmodel(N,J1) : inmodel(N,J2),
                    J1 < J2,
                    odnf(J1,M1), odnf(J2,M2), 
                    M1+M2 == M, nmodels(M).

inclusive(J1,J2) :- inmodel(N,J2) : inmodel(N,J1) : N = 1..M, 
                    inmodel(N,J1) : inmodel(N,J2) : N = 1..M, 
                    J1 < J2, nmodels(M),
                    notall(J1), notall(J2).

#hide.
#show exclusive/2.
#show inclusive/2.
