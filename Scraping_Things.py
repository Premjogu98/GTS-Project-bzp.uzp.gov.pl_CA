import re
import time
import sys , os
import string
from datetime import datetime,timedelta
import global_var
import html
from Insert_On_Datbase import create_filename,insert_in_Local
import wx
import html
app = wx.App()


def Scraping_data(get_htmlSource,purchaser,reference_number,Title,Tender_id,Url):

    SegFields = []
    for data in range(45):
        SegFields.append('')
    Decoded_get_htmlSource: str = html.unescape(str(get_htmlSource))
    Decoded_get_htmlSource: str = re.sub('\s+', ' ', str(Decoded_get_htmlSource)).replace("\n","")
    a = True
    a = True
    while a == True:
        try:
            # ==================================================================================================================
            # Purchaser_Email ID
            Address_html = Decoded_get_htmlSource.partition("NAZWA I ADRES:")[2].partition("</div>")[0]
            Email_ID = Address_html.partition("e-mail")[2].partition(",")[0].replace(':','')
            SegFields[1] = Email_ID.strip() # Purchaser_Email ID

            # ==================================================================================================================
            # Address

            Address = Address_html.partition("Polska,")[0]
            cleanr = re.compile('<.*?>')
            Address = re.sub(cleanr, '', Address).strip()
            Address = string.capwords(str(Address))
            Address = f'{str(Address)} Polska.'
            
            Tel = Address_html.partition("tel.")[2].partition(",")[0].strip()
            Fax = Address_html.partition("faks")[2].partition(".")[0].strip()

            Collected_Address = str(Address) + "<br>\n" + "Tel: " + str(Tel)+ "<br>\n" + "faks: " + Fax.replace('-','')
            SegFields[2] = Collected_Address  # Purchaser_Address

            # # ==================================================================================================================
            # # 
            contactor_name = Decoded_get_htmlSource.partition("Nazwa wykonawcy:")[2].partition("<br>")[0].strip()
            SegFields[3] = contactor_name  # Contractor_name

            CN_Address = Decoded_get_htmlSource.partition("Adres pocztowy:")[2].partition("<br>")[0].strip()
            if CN_Address != '':
                SegFields[4] += f'{CN_Address}, '

            CN_Postal_Address = Decoded_get_htmlSource.partition("Kod pocztowy:")[2].partition("<br>")[0].strip()
        
            CN_City = Decoded_get_htmlSource.partition("Miejscowość:")[2].partition("<br>")[0].strip()
            if CN_City != '':
                SegFields[4] += f'{CN_City}, '

            CN_Country_province =  Decoded_get_htmlSource.partition("Kraj/woj.:")[2].partition("<br>")[0].strip()
            if CN_Country_province != '':
                SegFields[4] += f'{CN_Country_province}, '

            if CN_Postal_Address != '':
                SegFields[4] += f'Kod pocztowy({CN_Postal_Address})'  # Contractor_Address
            SegFields[4] = SegFields[4].strip().rstrip(',')
            SegFields[7] = global_var.pur_country_code # Purchaser_Country

            SegFields[5] = global_var.cont_country_code  # Contractor_Country

            CN_Email_ID =  Decoded_get_htmlSource.partition("Email wykonawcy:")[2].partition("<br>")[0].strip()
            SegFields[6] = CN_Email_ID.lower().strip() # Contractor_EmailID

            # # ==================================================================================================================
            # # Purchaser_URL

            Purchaser_URL = Address_html.partition("Adres strony internetowej (url):")[2].replace('<br>','').strip()
            SegFields[8] = Purchaser_URL

            # # ==================================================================================================================
            # # Purchaser_name
            SegFields[12] = purchaser.strip()

            # # ==================================================================================================================
            # # reference_no
            SegFields[13] = Tender_id.strip()

            SegFields[14] = "0" # news_check

            SegFields[16] = "1" # qc

            SegFields[17] = global_var.exe_no  # CA_exe_number

            # # ==================================================================================================================
            # # Tender Details
    
            SegFields[19] = Title  # short_descp

            Short_disc = Decoded_get_htmlSource.partition("Krótki opis przedmiotu zamówienia")[2].partition("</div>")[0]
            Short_disc = str(Short_disc).encode('ascii', 'replace')
            cleanr = re.compile('<.*?>')
            Short_disc = re.sub(cleanr, '', str(Short_disc))
            Short_disc = string.capwords(str(Short_disc.strip().replace('?','')))
            
            Type_of_contract = Decoded_get_htmlSource.partition("Rodzaj zamówienia:</b>")[2].partition("</div>")[0]
            cleanr = re.compile('<.*?>')
            Type_of_contract = re.sub(cleanr, '', Type_of_contract)
            Type_of_contract = string.capwords(str(Type_of_contract.strip()))

            Collected_Tender_Details = f'Krótki opis przedmiotu zamówienia {str(Short_disc)}<br>\nRodzaj zamówienia: {str(Type_of_contract)}'
            SegFields[18] = Collected_Tender_Details # award_details

            # # ==================================================================================================================
            # # contract_date

            DATE_OF_CONTRACT_AWARD = Decoded_get_htmlSource.partition("DATA UDZIELENIA ZAMÓWIENIA:")[2].partition("<br>")[0].replace(' ','').strip()
            cleanr = re.compile('<.*?>')
            DATE_OF_CONTRACT_AWARD = re.sub(cleanr, '', DATE_OF_CONTRACT_AWARD)
            
            try:
                datetime_object = datetime.strptime(DATE_OF_CONTRACT_AWARD, '%d/%m/%Y')
                mydate = datetime_object.strftime("%Y-%m-%d")
                SegFields[24] = mydate
            except:
                pass

            SegFields[20] = '0'  # userid

            contract_amount = Decoded_get_htmlSource.partition("Wartość bez VAT</b>")[2].partition("<br>")[0].strip()
            if contract_amount != '':
                SegFields[21] = contract_amount.replace(',','')  # contract_value
                SegFields[22] = "PLN" # contract_currency


            SegFields[28] = Url.strip()  # tender_doc_file_col2

            # Source Name
            SegFields[31] = global_var.source  # source_col1

            ReplyStrings = Decoded_get_htmlSource.partition('Główny Kod CPV:</b>')[2].partition('</div> </div>')[0].strip()
            cleanr = re.compile('<.*?>')
            ReplyStrings = re.sub(cleanr, '', ReplyStrings)
            if ReplyStrings != "":
                copy_cpv = ""
                Cpv_status = True
                all_string = ""
                try:
                    while Cpv_status == True:
                        phoneNumRegex = re.compile(r'\d\d\d\d\d\d\d\d-')
                        CPv_main = phoneNumRegex.search(ReplyStrings)
                        mainNumber = CPv_main.groups()
                        if CPv_main:
                            copy_cpv = CPv_main.group(), ", "
                            ReplyStrings = ReplyStrings.replace(CPv_main.group(), "")
                        else:
                            Cpv_status = False
                        result = "".join(str(x) for x in copy_cpv)
                        result = result.replace("-", "").strip()
                        result2 = result.replace("\n", "")
                        # print(result2)
                        all_string += result2
                except:
                    pass
                # print(all_string.strip(","))
                all_string = all_string.strip().rstrip(',')
                SegFields[36] = all_string
            else:
                SegFields[36] = ""

            for SegIndex in range(len(SegFields)):
                print(SegIndex, end=' ')
                print(SegFields[SegIndex])
                SegFields[SegIndex] = html.unescape(str(SegFields[SegIndex]))
                SegFields[SegIndex] = str(SegFields[SegIndex]).replace("'", "''")

            if len(SegFields[19]) >= 200:
                SegFields[19] = str(SegFields[19])[:200]+'...'

            if len(SegFields[18]) >= 1500:
                SegFields[18] = str(SegFields[18])[:1500]+'...'

            insert_in_Local(get_htmlSource , SegFields)
            a = False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
            global_var.On_Error += 1
            a = True

# def check_date(get_htmlSource, SegFields):
#     deadline = str(SegFields[24])
#     curdate = datetime.now()
#     curdate_str = curdate.strftime("%Y-%m-%d")
#     try:
#         if deadline != '':
#             datetime_object_deadline = datetime.strptime(deadline, '%Y-%m-%d')
#             datetime_object_curdate = datetime.strptime(curdate_str, '%Y-%m-%d')
#             timedelta_obj = datetime_object_deadline - datetime_object_curdate
#             day = timedelta_obj.days
#             if day > 0:
#                 insert_in_Local(get_htmlSource , SegFields)
#             else:
#                 print("Expired Tender")
#                 global_var.expired += 1
#         else:
#             print("Deadline Not Given")
#             global_var.deadline_Not_given += 1
#     except Exception as e:
#         exc_type , exc_obj , exc_tb = sys.exc_info()
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname , "\n" ,exc_tb.tb_lineno)