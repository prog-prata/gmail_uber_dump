from pytz import timezone
from dateutil import parser
import quopri
import re

from utils.mailler import decode_mime_words

FUSO_BRASIL = timezone('America/Sao_Paulo')

def get_date_from_message(message):
    date = message.get('Date')
    data_utc = parser.parse(date)
    data_timezone = data_utc.astimezone(FUSO_BRASIL) 
    return data_timezone.strftime('%Y-%m-%d %H:%M:%S')

def get_subject_from_message(message):
    return decode_mime_words(message.get('Subject'))

def get_body_from_message(message):
    payload = message.get_payload()
    body = quopri.decodestring(payload)
    parsed_body = body.decode('utf-8', 'replace')
    #with open("html/{}.html".format(email_id), "w") as arquivo:
    #    arquivo.write(parsed_body)
    return parsed_body

def get_total_from_body(body):                
    valores = re.findall(r'R\$\s\d+[,|.]\d{2}', body)
    total = 0
    for item in valores:
        valor = float(item.split()[1].replace(',', '.'))
        if  valor > total:
            total = valor
        #print(item)
    return total

def get_distance_from_body(body):
    return float((re.findall(r'\d+[,|.]\d{2}\sQuil', body)[0]).split()[0])

def get_addresses_from_body(body):
    ceps = re.findall(r'.[^\>]*\d{5}-\d{3}', body)
    ruas = []
    for item in ceps:
        ruas.append(item.replace('>', ''))
    addresses = {}
    for addr in enumerate(ruas):
        addresses["addr{}".format(addr[0]+1)] = addr[1]
    return addresses