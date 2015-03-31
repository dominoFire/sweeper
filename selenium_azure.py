__author__ = 'fer'

from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd

driver = Firefox()
azure_linux = 'http://azure.microsoft.com/en-us/pricing/details/virtual-machines/#Linux'
driver.get(azure_linux)

ddlCurrency = Select(driver.find_element_by_id('waDropdownCurrency'))
ddlCurrency.select_by_value('USD')
ddlRegion = Select(driver.find_element_by_id('wa-dropdown-region'))

pricing_list = []
suse_list = []

for opt in ddlRegion.options:
    current_region = opt.get_attribute('value')
    ddlRegion.select_by_value(current_region)
    html_doc = driver.page_source
    soup = BeautifulSoup(html_doc)
    #All info is in the same page, we can exract it in a single pass
    div = soup.find('div', attrs={'class': 'wa-tabs-container'})
    div_active = div.find('div', attrs={'class': 'active'}, recursive=False)
    tables = div_active.find_all('table')
    print ('{0} tables: {1}, divs: {2}'.format(current_region, len(tables), len(div_active)))
    for i, table in enumerate(tables):
        active_pricetags = table.find_all('span', attrs={'class': 'wa-conditionalDisplay active'})
        prices_all = []
        for pricetag in active_pricetags:
            tag = pricetag.find('span', attrs={'class': 'price-data'})
            if tag:
                prices_all.append(tag.get('data-amount'))
        price_hour = prices_all[0::2]
        price_month = prices_all[1::2]
        df = pd.io.html.read_html(str(table), parse_dates=False, flavor='html5lib', infer_types=False)
        df = pd.DataFrame(df[0])

        title = table.find_previous_sibling('h3')
        if title:
            title = title.string
        else:
            title = table.parent.find_previous_sibling('h3')
            if title:
                title = title.string
            else:
                title = 'No inmediate name'

        df['region'] = pd.Series(data=[current_region] * len(df.index))
        df['description'] = pd.Series(data=[title] * len(df.index))

        if len(prices_all) > 1:
            df = df.drop('Price', 1)
            df['price_hour_usd'] = pd.Series(data=price_hour, index=df.index)
            df['price_month_usd'] = pd.Series(data=price_month)
            pricing_list.append(df)
        else:
            suse_list.append(df)

        print ('{0}: {1}'.format(title, df.shape))

append_df = lambda a, b: a.append(b)
df_all_pricing = reduce(append_df, pricing_list)
df_all_suse = reduce(append_df, suse_list)

df_all_pricing.to_csv('azure_pricing_vm_common.csv', index=None, encoding='utf-8')
df_all_suse.to_csv('azure_pricing_vm_suse.csv', index=None, encoding='utf-8')

driver.close()
