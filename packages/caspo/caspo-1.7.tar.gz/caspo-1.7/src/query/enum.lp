#const maxsize = -1.
#const maxresidual = -1.
         
:- maxsize + 1 [dnf(I,J) : hyperedge(I,J,L) = L], maxsize >= 0.
:- maxresidual + 1 [active(E,V) : obs(E,V,D) : rss(D,V,1,W) = W,
                    not active(E,V) : obs(E,V,D) : rss(D,V,0,W) = W], maxresidual >= 0.
