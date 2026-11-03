# Random classifier baseline, independent of the target label. Uses only
# the native reproducible RNG, with no circuit and no learned parameters.
label random_prediction
call random_uniform
fset f21 0
fcmp f30 0.5
jlt random_prediction_ready
fset f21 1
label random_prediction_ready
ret
