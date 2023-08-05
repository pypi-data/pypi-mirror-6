exp(E) :- exp(E,_,_).
free(E,V,I) :- formula(V,I), dnf(I,_), exp(E),
               not stimulus(V), not exp(E,V,0). 
             

active(E,V) :- exp(E,V,1), stimulus(V).
active(E,V) :- exp(E), free(E,V,I), dnf(I,J),
               active(E,W) : clause(J,W,1), 
               not active(E,W) : clause(J,W,-1). 

rss(D,V,1,#pow(F-D,2)) :- obs(E,V,D), dfactor(F).
rss(D,V,0,#pow(D,2))   :- obs(E,V,D).
