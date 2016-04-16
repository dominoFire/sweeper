#!/usr/bin/python3

from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
from functools import reduce


def append_df(a, b):
    return a.append(b)


def save_df_list(p_df_list, filename):
    big_df = reduce(append_df, p_df_list, pd.DataFrame())
    big_df.to_csv(filename, index=None, encoding='utf-8')


if __name__ == '__main__':
    driver = Firefox()
    azure_linux = 'http://azure.microsoft.com/en-us/pricing/details/virtual-machines/#Linux'
    driver.get(azure_linux)

    ddlCurrency = Select(driver.find_element_by_id('wa-dropdown-currency'))
    ddlCurrency.select_by_value('USD')
    ddlRegion = Select(driver.find_element_by_id('wa-dropdown-region'))

    pricing_list = []
    suse_list = []

    # Iterate over all Azure compute regions
    for opt in ddlRegion.options:
        current_region = opt.get_attribute('value')
        ddlRegion.select_by_value(current_region)
        html_doc = driver.page_source
        soup = BeautifulSoup(html_doc, 'html.parser')
        # All info is in the same page, we can exract it in a single pass
        div = soup.find('div', attrs={'class': 'wa-tabs-container'})
        div_active = div.find('div', attrs={'class': 'active'}, recursive=False)
        tables = div_active.find_all('table')
        print('{0} tables: {1}, divs: {2}'.format(current_region, len(tables), len(div_active)))

        # Iterate over all tables found in the pricing page
        for i, table in enumerate(tables):
            df_list = pd.io.html.read_html(str(table), parse_dates=False, flavor='html5lib')
            df = pd.DataFrame(df_list[0])

            # Which table we  are processing
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

            # Decide in which list to put the extracted table
            if 'SLES Premium' in df.columns:
                suse_list.append(df)
            else:
                pricing_list.append(df)

            print('{0}: {1}'.format(title, df.shape))

    save_df_list(suse_list, 'azure_pricing_vm_suse.csv')
    save_df_list(pricing_list, 'azure_pricing_vm_common.csv')

    driver.close()
