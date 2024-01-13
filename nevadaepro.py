import requests
from bs4 import BeautifulSoup
from lxml import etree
import json
import os


def main():
    dataframe = first_page()
    print(dataframe)
    with open('data.json', 'w') as f:
        json.dump(dataframe, f)

def first_page():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    start_url = "https://nevadaepro.com/bso/view/search/external/advancedSearchBid.xhtml?openBids=true"
    r = requests.get(start_url)

    soup = BeautifulSoup(r.content, 'html5lib')
    dom = etree.HTML(str(soup))
    csrf = dom.xpath("(//input[@name='_csrf'])[1]")[0]
    csrf_token = etree.tostring(csrf).decode('utf-8').split(' ')[3].split('"')[1]
    first_id = 25
    total_in_page = 25
    data = []
    common = dom.xpath("//div[@class='ui-datatable-tablewrapper']//tbody//tr[@role='row']")
    for i in common:
        Bid_Solitication_number = i.xpath(".//td[1]/a/text()")[0].strip()
        Bid_Solitication_url = "https://nevadaepro.com" + i.xpath(".//td[1]/a/@href")[0].strip()
        data2 = inside(csrf_token, Bid_Solitication_url)
        data.append({
            "Bid Solicitation #": Bid_Solitication_number,
            "Bid Solicitation url": Bid_Solitication_url,
            "header_information" : data2['header_information'],
        })

    while True:
        headers['cookie'] = '; '.join([x.name + '=' + x.value for x in r.cookies])
        headers['content-type'] = 'application/x-www-form-urlencoded'
        payload = f'bidSearchResultsForm%3AbidResultId_first={first_id}&bidSearchResultsForm%3AbidResultId_rows=25&bidSearchResultsForm%3AbidResultId_pagination=true&_csrf={csrf_token}&bidSearchResultsForm%3AbidResultId_encodeFeature=true'
        r = requests.request(
            "POST",
            'https://nevadaepro.com/bso/view/search/external/advancedSearchBid.xhtml?openBids=true',
            headers=headers,
            data=payload,
        )
        soup = BeautifulSoup(r.content, 'html5lib')
        dom = etree.HTML(str(soup))
        common = dom.xpath("//span[@id='bidSearchResultsForm:results']/a[contains(@href, 'bidDetail.sdo')]")
        if common:
            for i in common:
                Bid_Solitication_number = i.xpath(".//text()")[0].strip()
                Bid_Solitication_url = "https://nevadaepro.com" + i.xpath(".//@href")[0].strip()
                data2 = inside(csrf_token, Bid_Solitication_url)
                data.append({
                    "Bid Solicitation #": Bid_Solitication_number,
                    "Bid Solicitation url": Bid_Solitication_url,
                    "header_information" : data2['header_information'],
                })
            first_id = first_id + total_in_page
        else:
            break

    return data

def inside(csrf_token, url):
    data2 = []
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    dom = etree.HTML(str(soup))

    #address grabbing
    Bid_number = dom.xpath(
        "//td[contains(text(),'Bid Number:')]/following-sibling::td[1]/text()")[0].strip()
    Purchaser = dom.xpath("//td[contains(text(),'Purchaser:')]/following-sibling::td[1]/text()")[0].strip()
    Department = dom.xpath(
        "//td[contains(text(),'Department:')]/following-sibling::td[1]/text()")[0].strip()
    fiscal_year = dom.xpath(
        "//td[contains(text(),'Fiscal Year:')]/following-sibling::td[1]/text()")[0].strip()
    alternate_id = dom.xpath(
        "//td[contains(text(),'Alternate Id:')]/following-sibling::td[1]/text()")[0].strip()
    info_contact = dom.xpath(
        "//td[contains(text(),'Info Contact:')]/following-sibling::td[1]/text()")[0].strip()
    Purchase_Method = dom.xpath(
        "//td[contains(text(),'Purchase Method:')]/following-sibling::td[1]/text()")[0].strip()
    Description = dom.xpath(
        "//td[contains(text(),'Description:')]/following-sibling::td[1]/text()")[0].strip()
    Organization = dom.xpath(
        "//td[contains(text(),'Organization:')]/following-sibling::td[1]/text()")[0].strip()
    Location = dom.xpath(
        "//td[contains(text(),'Location:')]/following-sibling::td[1]/text()")[0].strip()
    Type_Code = dom.xpath(
        "//td[contains(text(),'Type Code:')]/following-sibling::td[1]/text()")[0].strip()
    Required_Date = dom.xpath(
        "//td[contains(text(),'Required Date:')]/following-sibling::td[1]/text()")[0].strip()
    Bid_Type = dom.xpath(
        "//td[contains(text(),'Bid Type:')]/following-sibling::td[1]/text()")[0].strip()
    opening_date = dom.xpath(
        "//td[contains(text(),'Bid Opening Date:')]/following-sibling::td[1]/text()")[0].strip()
    Allow_Electronic_Quote = dom.xpath(
        "//td[contains(text(),'Allow Electronic Quote:')]/following-sibling::td[1]/text()")[0].strip()
    Available_Date = dom.xpath(
        "//td[contains(text(),'Available Date')]/following-sibling::td[1]/text()")[0].strip()
    Informal_Bid_Flag = dom.xpath(
        "//td[contains(text(),'Informal Bid Flag:')]/following-sibling::td[1]/text()")[0].strip()
    Pre_Bid_Conference = dom.xpath(
        "//td[contains(text(),'Pre Bid Conference:')]/following-sibling::td[1]/text()")[0].strip()
    Bulletin_Desc = dom.xpath(
        "//td[contains(text(),'Bulletin Desc:')]/following-sibling::td[1]/text()")[0].strip()
    Ship_to = ''.join(map(str,dom.xpath("//td[contains(text(),'Ship-to Address:')]/following-sibling::td[1]/text()"))).strip()
    Bill_to = ''.join(map(str,dom.xpath("//td[contains(text(),'Bill-to Address:')]/following-sibling::td[1]/text()"))).strip()


    #download file logic
    download_directory = os.getcwd() + "\\downloaded_files"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    loop = len(dom.xpath("//td[contains(text(),'File Attachments')]/following-sibling::td/a"))
    for i in range(1, loop + 1):
        download_id = dom.xpath(f'//td[contains(text(),"File Attachments")]/following-sibling::td/a[{i}]/@href')[0].split("'")[1]
        filename = dom.xpath(f'//td[contains(text(),"File Attachments")]/following-sibling::td/a[{i}]/text()')[0]
        ext = filename.split(".")[len(filename.split(".")) - 1]
        download_url = f'https://nevadaepro.com/bso/external/bidDetail.sdo?_csrf={csrf_token}&mode=download&bidId={Bid_number}&docId={Bid_number}&currentPage=1&querySql=&downloadFileNbr={download_id}&itemNbr=undefined&parentUrl=close&fromQuote=&destination='
        r = requests.get(download_url)
        if ext == "pdf" or ext == "docx" or ext == "doc":
            with open(download_directory + f'\\{filename}', 'wb') as f:
                f.write(r.content)
        else:
            with open(download_directory + f'\\{filename}.pdf', 'wb') as f:
                f.write(r.content)


    #data returning
    data2.append(
        {
            "header_information": {
                "Bid Number": Bid_number,
                "Purchaser": Purchaser,
                "Department": Department,
                "fiscal_year": fiscal_year,
                "Alternate Id:": alternate_id,
                "info_conctact": info_contact,
                "Purchase Method": Purchase_Method,
                "Description:": Description,
                "Organization": Organization,
                "Location": Location,
                "Type Code": Type_Code,
                "Required Date": Required_Date,
                "Bid Type": Bid_Type,
                "Bid Opening Date": opening_date,
                "Allow Electronic Quote": Allow_Electronic_Quote,
                "Available Date": Available_Date,
                "Informal Bid Flag": Informal_Bid_Flag,
                "Pre Bid Conference": Pre_Bid_Conference,
                "Bulletin Desc": Bulletin_Desc,
                "Ship-to Address": Ship_to,
                "Bill-to Address": Bill_to,

            },
        }

    )
    return data2[0]


if __name__ == '__main__':
    main()
