library(rvest)

azure_linux = 'http://azure.microsoft.com/en-us/pricing/details/virtual-machines/#Linux'
azure = html(azure_linux)

tbs = azure %>% html_nodes('table') %>% .[[1]]
tds = tbs %>% html_nodes('tr') %>% html_nodes('td') %>% html_nodes('.active .price-data') %>% html_text()
df = tds %>% html_table()


azure = html(azure_linux)
set_values(azure, `wa-dropdown-region`='us-west')
set_values(azure, `waDropdownCurrency`='USD')
tbs = azure %>% html_nodes('table') %>% .[[1]]
tds = tbs %>% html_nodes('tr') %>% html_nodes('td') %>% html_nodes('.active .price-data') %>% html_text()
