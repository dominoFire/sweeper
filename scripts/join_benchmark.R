source('scripts/functions.R')

fnames = file('data/names.txt')
benchs.names = readLines(fnames, n = -1)
close(fnames)
benchs = lapply(benchs.names, function(x) read.csv(sprintf('data/%s.csv', x)))
benchs.azure = lapply(benchs, get_azure_benchs)

roles = read.csv('data/azure_role_pricing.csv')
specfp = benchs.azure[[2]]

joined = roles %>% dplyr::inner_join(specfp, by = c('Instance'='instance_type'))

write.csv(joined, 'data/azure_role_pricing_bench.csv')
