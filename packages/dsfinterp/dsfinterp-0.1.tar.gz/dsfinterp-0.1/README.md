dsfinterp
=========

Summary
=======
Cubic Spline Interpolationf of Dynamics Structure Factors S(Q,E,f) as a function of a parameter "f".

Details
=======

Given a discrete series of Dynamics Structure Factors S_i(Q,E) that
depends on an extra parameter "f", S_i(Q,E) = S(Q,E,f_i), construct
and object that returns S(Q,E) for any value of f in the range 
[min({f_i} }, max( {f_i} )].

Parameter "f" can be an environment variable such as Temperature or an
"internal" parameter, such as a component of a force-field.

This interpolator is geared towards determination of S(Q,E,f) using a
series { S_i(Q,E) } computed from molecular dynamics simulations,
although the series could be generated from experiments, too.

If the { S_i(Q,E) } do not have associated errors, as it is the case
when computed from simulations, an error will be estimated by a
running regression of the S_i(Q,E) versus f. Thus, the object will
return S(Q,E) and and associated error(Q,E) any value of f in the
allowed range.
