#! /usr/bin/python

# Script para correr los benchmarks de Perfkit sobre Microsoft Azure
import os
import sys


perfkit_home = '/home/microkid/github/PerfKitBenchmarker'
perfkit_benchmarks = ['coremark', 'bonie++', 'unixbench', 'wrk']
azure_role_sizes = ['ExtraSmall', 'Small', 'Medium', 'Large', 'ExtraLarge']
options = {
	'cloud': 'Azure',
	'machine_type': None,
	'benchmarks': None,
	'archive_bucket': 'gs://sweeper-benchmarks',
	'os_type': 'ubuntu_container',
	'json_path': None
}
n_trials = 30  # Para tener resultados estadisticamente validos


def parse_opts(opt):
	opt_list = ['--' + str(k) + '=' + str(options[k]) for k in options]
	return ' '.join(opt_list)


if __name__ == '__main__':
	for i in range(n_trials):
		for bench in perfkit_benchmarks:
			for role in azure_role_sizes:
				options['machine_type'] = role
				options['benchmarks'] = bench
				path_pkb = os.path.join(perfkit_home, 'pkb.py')
				out_base = 'perfkit_{0}_{1}_{2:02d}'.format(bench, role, (i+1))
				options['json_path'] = out_base + '.json'				

				print('Testing {0}'.format(out_base))

				cmd = '{0} {1} > {2}.out 2> {2}.err'.format(path_pkb, parse_opts(options), out_base)
				os.system(cmd)

