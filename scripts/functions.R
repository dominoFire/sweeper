library(rvest)
library(dplyr)
library(ggplot2)

# returns string w/o leading or trailing whitespace
trim <- function (x) gsub("^\\s+|\\s+$", "", x)

pretty.colnames <- function(x) {
  xt = tolower(x)
  xt = gsub(' +', '_', xt)
  xt = gsub('[\\[\\]\\(\\)/\\\\]+', '', xt, perl=T)
  return(xt)
}

apply_pretty.colnames <- function(df) {
  colnames(df) = pretty.colnames(colnames(df))
  return(df)
}

get_azure_benchs <- function(x) {
  apply_pretty.colnames(x) %>% 
    dplyr::filter(service=='Microsoft Azure Virtual Machines') %>%
    dplyr::mutate(instance_genre = substr(instance_type, 1, 1)) %>%
    dplyr::mutate(instance_type=toupper(instance_type)) %>%
    dplyr::mutate(instance_type=factor(instance_type, levels=c('A6','A7','A8','A9','D1','D2','D3','D4','D11','D12','D13','D14','G1','G2','G3','G4','G5'), ordered=T))
}

