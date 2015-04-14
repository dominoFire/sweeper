#! /usr/bin/Rscript

# Validation
args <- commandArgs(TRUE)
if(length(args)<1) {
    cat('Please provide a csv filename')
    q(save = 'no', status = 1)
}

library(plotrix)
fname = args[1]

inf = read.csv(fname, stringsAsFactors=F)

i_ini = floor(min(inf$starts))
i_fin = ceiling(max(inf$ends))
pseq = i_ini:i_fin

gantt.chart(x=inf,
            vgridpos=pseq,
            vgridlab=pseq,
            taskcolors=rainbow(nrow(inf)),
            main='Gantt chart')
text(x=inf$starts,
     y=inf$y_coord,
     labels=inf$task_name,
     cex=0.7,
     pos=4)
