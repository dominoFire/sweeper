source('scripts/functions.R')

#cloud_url = 'https://cloudharmony.com/benchmarks/compute/cpu'
#cloud_url = 'http://cc.bingj.com/cache.aspx?q=https%3a%2f%2fcloudharmony.com%2fbenchmarks%2fcompute%2fcpu&d=4725444764893446&mkt=es-MX&setlang=en-US&w=DhdSx-ksG7dk4ha0h6I-pwkjspmH_SMk'
cloud_url = 'http://cc.bingj.com/cache.aspx?q=https%3a%2f%2fcloudharmony.com%2fbenchmarks%2fcompute%2fcpu&d=4725444764893446&mkt=es-MX&setlang=en-US&w=DhdSx-ksG7dk4ha0h6I-pwkjspmH_SMk'


cloud_harmony = read_html(cloud_url)

benchs = cloud_harmony %>% html_nodes('table')

benchs.tables = sapply(benchs, function(x){ html_table(x) })
benchs.titles = cloud_harmony %>% html_nodes('h2') %>% html_text()  

benchs.azure = lapply(benchs.tables, get_azure_benchs)

bplot = function(x) x + geom_bar(stat='identity') + geom_errorbar()

bplot(ggplot(benchs.azure[[1]], 
             aes(x=instance_type, 
                 y=specint_estimate, 
                 fill=instance_genre,
                 ymin=specint_estimate - specint_stdev,
                 ymax=specint_estimate + specint_stdev))) +
  ggtitle(benchs.titles[1])

bplot(ggplot(benchs.azure[[2]], 
             aes(x=instance_type, 
                 y=specfp_estimate, 
                 fill=instance_genre,
                 ymin=specfp_estimate - specfp_stdev,
                 ymax=specfp_estimate + specfp_stdev))) +
  ggtitle(benchs.titles[2])

bplot(ggplot(benchs.azure[[3]], 
             aes(x=instance_type, 
                 y=score,
                 fill=instance_genre,
                 ymin=score - score_stdev,
                 ymax=score + score_stdev))) +
  ggtitle(benchs.titles[3])

bplot(ggplot(benchs.azure[[4]],
             aes(x=instance_type, 
                 y=multicore_score,
                 fill=instance_genre,
                 ymin=multicore_score - multicore_score_stdev,
                 ymax=multicore_score + multicore_score_stdev))) +
  ggtitle(benchs.titles[4])

bplot(ggplot(benchs.azure[[5]],
             aes(x=instance_type, 
                 y=score,
                 fill=instance_genre,
                 ymin=score - score_stdev,
                 ymax=score + score_stdev))) +
  ggtitle(benchs.titles[[5]])

bplot(ggplot(benchs.azure[[6]],
             aes(x=instance_type, 
                 y=multicore_score,
                 fill=instance_genre,
                 ymin=multicore_score - multicore_score_stdev,
                 ymax=multicore_score + multicore_score_stdev))) +
  ggtitle(benchs.titles[[6]])

for(i in 1:length(benchs.titles)) {
  write.csv(benchs.azure[[i]], file=sprintf("data/%s.csv", benchs.titles[i]), row.names=F)
}
