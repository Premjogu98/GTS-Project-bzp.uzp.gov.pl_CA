from datetime import datetime
import global_var
import time
import mysql.connector
import sys, os
import pymysql.cursors
import wx
app = wx.App()



def DB_connection():
    mydb_Local = ''
    a = 0
    while a == 0:
        try:
            mydb_Local = pymysql.connect(host='185.142.34.92',user='ams',password='TgdRKAGedt%h',db='contractawards_db',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
            a = 1
            return mydb_Local
        except Exception as e:
            exc_type , exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : " , sys._getframe().f_code.co_name + "--> " + str(e) , "\n" , exc_type , "\n" , fname ,"\n" , exc_tb.tb_lineno)
            global_var.On_Error += 1
            a = 0
            time.sleep(10)

def Error_fun(Error,Function_name,Source_name):
    mydb = DB_connection()
    mycursor = mydb.cursor()
    sql1 = "INSERT INTO ErrorLog(Error_Message,Function_Name,Exe_Name) VALUES('" + str(Error).replace("'","''") + "','" + str(Function_name).replace("'","''")+ "','"+str(Source_name)+"')"
    mycursor.execute(sql1)
    mydb.commit()
    mycursor.close()
    mydb.close()
    global_var.On_Error += 1
    return sql1

def check_Duplication(get_htmlSource,SegFields):
    global a1
    a1 = 0
    while a1 == 0:
        try:
            mydb = DB_connection()
            mycursor = mydb.cursor()
            if SegFields[13] != '' and SegFields[24] != '' and SegFields[7] != '':
                commandText = f"SELECT id from {global_var.local_table_name} where ref_number = '{str(SegFields[13])}' and purch_country = '{str(SegFields[7])}' and cont_date = '{str(SegFields[24])}'"
            
            elif SegFields[13] != "" and SegFields[7] != "":
                commandText = f"SELECT id from {global_var.local_table_name} where ref_number = '{str(SegFields[13])}' and purch_country = '{str(SegFields[7])}'"
            
            elif SegFields[19] != "" and SegFields[24] != "" and SegFields[7] != "":
                commandText = f"SELECT id from {global_var.local_table_name} where short_descp = '{str(SegFields[19])}' and cont_date = '{SegFields[24]}' and purch_country = '{SegFields[7]}'"
            
            else:
                commandText = f"SELECT id from {global_var.local_table_name} where short_descp = '{str(SegFields[19])}' and purch_country = '{str(SegFields[7])}'"
            mycursor.execute(commandText)
            results = mycursor.fetchall()
            mydb.close()
            mycursor.close()
            a1 = 1
            print("Code Reached On check_Duplication")
            return results
        except Exception as e:
            Function_name: str = sys._getframe().f_code.co_name
            Error: str = str(e)
            Source_name = str(SegFields[31])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
            Error_fun(Error,Function_name,Source_name)
            time.sleep(10)
            a1 = 0


def insert_in_Local(get_htmlSource , SegFields):

    results = check_Duplication(get_htmlSource , SegFields)
    HtmlDaoc_file_name = ''
    if len(results) > 0:
        print('Duplicate Tender')
        global_var.duplicate += 1
        return 1
    else:
        Fileid = create_filename(get_htmlSource , SegFields)
        HtmlDaoc_file_name = f'{str(Fileid)}.html'
    MyLoop = 0
    while MyLoop == 0:
        curdatetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mydb = DB_connection()
        mycursor = mydb.cursor()
        sql = f"INSERT INTO {global_var.local_table_name} (short_descp,ref_number,purchasername,purch_country,purchaseradd,purch_email,purch_url,contractorname,cont_add,cont_country,cont_email,cont_url,project_location,award_detail,contract_val,contract_currency,sector,userid,cont_date,col1,col2,col3,col4,news_check,qc,ca_number,cpv,file_name,date_c,cont_completion_date)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val= (SegFields[19],SegFields[13],SegFields[12],SegFields[7],SegFields[2],SegFields[1],SegFields[8],SegFields[3],SegFields[4],SegFields[5],SegFields[6],SegFields[9],SegFields[15],SegFields[18],SegFields[21],SegFields[22],SegFields[23],SegFields[20],SegFields[24],SegFields[31],SegFields[28],SegFields[10],SegFields[11],SegFields[14],SegFields[16],SegFields[17],SegFields[36],HtmlDaoc_file_name,curdatetime,SegFields[37])
        try:
            mycursor.execute(sql , val)
            mydb.commit()
            mydb.close()
            mycursor.close()
            print("Code Reached On insert_in_Local")
            MyLoop = 1
        except Exception as e:
            Function_name: str = sys._getframe().f_code.co_name
            Error: str = str(e)
            Source_name = str(SegFields[31])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
            Error_fun(Error,Function_name,Source_name)
            MyLoop = 0
            time.sleep(10)

    insert_L2L(SegFields, HtmlDaoc_file_name)


def create_filename(get_htmlSource , SegFields):

    Current_dateTime = datetime.now().strftime("%Y%m%d%H%M%S%f")
    Fileid = f"".join([str(global_var.exe_no) ,Current_dateTime])
    a = 0
    while a == 0:
        try:
            File_path = "Z:\\" + Fileid + ".html"
            file1 = open(File_path , "w", encoding='utf-8')
            Final_Doc = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\"><html xmlns=\"http://www.w3.org/1999/xhtml\"><head><meta content=\"text/html; charset=utf-8\" http-equiv=\"Content-Type\" /><title>Award Document</title></head><style style=\"text/css\"> td{ padding:5px;}</style><BODY><Blockquote style='border:1px solid; padding:10px;'>" + get_htmlSource + "</Blockquote></BODY></html>"
            # Final_Doc_list = []
            # Final_HTML_Document1 = [Final_Doc[idx:idx + 1000] for idx , val in enumerate(Final_Doc)if idx % 1000 == 0]
            # for Final_HTML_Document2 in Final_HTML_Document1:
            #     Final_Doc_list.append(Final_HTML_Document2)
            # for Final_Doc_list1 in Final_Doc_list:
            file1.write(str(Final_Doc))
            file1.close()
            print("Code Reached On create_filename")
            return Fileid
        except Exception as e:
            Function_name: str = sys._getframe().f_code.co_name
            Error: str = str(e)
            Source_name = str(SegFields[31])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
            Error_fun(Error,Function_name,Source_name)
            a = 0
            time.sleep(10)


def insert_L2L(SegFields , HtmlDaoc_file_name):
    MyLoop = 0
    while MyLoop == 0:
        curdatetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mydb = DB_connection()
        mycursor = mydb.cursor()
        sql = "INSERT INTO ContractAwardFinal (short_descp,ref_number,purchasername,purch_country,purchaseradd,purch_email,purch_url,contractorname,cont_add,cont_country,cont_email,cont_url,project_location,award_detail,contract_val,contract_currency,sector,userid,cont_date,col1,col2,col3,col4,news_check,qc,cpv,file_name,date_c,is_english,cont_completion_date)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val= (SegFields[19],SegFields[13],SegFields[12],SegFields[7],SegFields[2],SegFields[1],SegFields[8],SegFields[3],SegFields[4],SegFields[5],SegFields[6],SegFields[9],SegFields[15],SegFields[18],SegFields[21],SegFields[22],SegFields[23],SegFields[20],SegFields[24],SegFields[31],SegFields[28],SegFields[10],SegFields[11],SegFields[14],SegFields[16],SegFields[36],HtmlDaoc_file_name,curdatetime,str(global_var.is_english),SegFields[37])
        try:
            mycursor.execute(sql , val)
            mydb.commit()
            mydb.close()
            mycursor.close()
            print("Code Reached On insert_in_L2L")
            global_var.inserted += 1
            MyLoop = 1
        except Exception as e:
            Function_name: str = sys._getframe().f_code.co_name
            Error: str = str(e)
            Source_name = str(SegFields[31])
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error ON : ", sys._getframe().f_code.co_name + "--> " + str(e), "\n", exc_type, "\n", fname, "\n",exc_tb.tb_lineno)
            Error_fun(Error,Function_name,Source_name)
            MyLoop = 0
            time.sleep(10)