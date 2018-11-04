import pycutest

prob = 'NGONE'
bad_params = {'HNS':4}

# prob = 'ARGLALE'
# bad_params = {'N':10, 'M':19}

pycutest.clear_cache(prob, sifParams=bad_params)
# p = pycutest.import_problem(prob, sifParams=bad_params, quiet=False)
p = pycutest.import_problem(prob, sifParams=bad_params)
