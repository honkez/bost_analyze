from cgitb import html
import requests as req
from bs4 import BeautifulSoup as bs
import lxml
import re
import pandas as pd
from datetime import datetime

def update_sido_url(url,sida):
   # updaterar url med sidnummer
    if sida == 1:
        return url
    else:
        return url+'&page='+str(sida)


#salda_hus=req.get('https://www.booli.se/slutpriser/skovde/401?objectType=Villa&minSoldDate=2017-01-09&maxSoldDate=2022-06-09&sort=soldDate') #Page1

# function to call site with dynamic url
def req_site_soup(ur_l):
    return req.get(ur_l)

#Change sign on the +/- , + ,- result value 
def change_sign(list):
    try:
        if list[0][0] == '+':
            return list [0][1]
        elif list[0][0] == '-':
            strn=str(list[0][0])+str(list[0][1])
            return strn
        else:
            return -1 
    except:    
        pass
    return -1

# find the result
def re_search(str_to_search,expr):
    t=[]
    split=re.split('%',str_to_search)
    t=re.findall(r'([+-])[\/]*[-]*[\d]*?([\d]*[\.]*[\d]*)[\s]*',split[0])
    #print("Test")
    #print(t[0][0],t[0][1])
    return change_sign(t)
# make the soup

## TODO
## Det som saknas är diffen som är uträknad
# ligger i div class_  
def make_del_soup(salda_hus,list_ite):
    list_items=[]
    soppa=bs(salda_hus.content,'lxml')

    #class="_2m6km uC2y2 _3oDFL"
    bostader=soppa.find('div',class_='_2m6km uC2y2 _3oDFL')
    bostad_lst=bostader.findAll('div')
    # Len = 38
    for bst_div in bostad_lst:
        ress=bst_div.text       
        try:          
            diva=bst_div.a.contents
            b_loc=diva[1].h4.text
            b_size=diva[1].p.text
            b_price=diva[2].h4.text
            b_pr_m2=diva[2].p.text
            b_sale_date='-'
            b_split_rslt=bst_div.text # use reqx to pars out the conents until % sign
            res_bost_deal=re_search(b_split_rslt,'smutt')
            try:
                b_sale_date=diva[2].find_all('p')[1].text
            except:
                continue

            if 'rum' not in b_size:
                b_size="None, "+b_size

            list_items.append({'b_loc':b_loc,
                            'b_size':b_size,
                            'b_price':b_price,
                            'b_pr_m2':b_pr_m2,
                            'b_sale_rslt':res_bost_deal, # TODO Denna är inte testad , kommer inte att funka ännu, fel här!!!
                            'b_sale_date':b_sale_date           
            })

        except:
            continue
    return list_items
   
if __name__ == '__main__':
    #Define Url
    urlen='https://www.booli.se/slutpriser/skovde/401?objectType=Villa&minSoldDate=2017-01-09&maxSoldDate=2022-07-20&sort=soldDate'
    sida_nr=1
    ant_sidor=5

    l_items=[]
    lig=[]
    item_list=[10]
    while sida_nr<=ant_sidor:
        #update page_nr
        side_url=update_sido_url(urlen,sida_nr)
        print(side_url)
        # call requester
        dt=datetime.now().date()
        nu_tid=dt
        r_page=req_site_soup(side_url)
        #populate lista med bostäder
        item_list=make_del_soup(r_page,l_items)#.extend
        # lägg till i listan
        lig.extend(item_list)
        sida_nr+=1
    #make dataframe with:
df_df = pd.DataFrame(lig)
print(df_df.head(8))
filnamn="scrape_booli_" + str(nu_tid) +".csv"
df_df.to_csv(filnamn)

input('Finished running scrape program')

