# -*- coding: utf-8 -*-

"""

Created on Thu Jun 25 11:07:03 2020

 

@author: jparker2

"""

 

import re

import requests

 

class genTables():

    def __init__(self):

        self.urls = []

        self.urlParams = {}

        self.goodResp = []

        self.filetext = ''

        self.file = r'C:\Users\jparker2\Documents\ApiThink.py'

        self.realBase = 'https://quant.vaneck.com:3939/quant_api/'

        self.baseUrls = ['/think/v1/']

        self.filetoWrite = 'api_think4.py'

       

        #self.getUrlData()

        self.getUrlDataFromRoute()

        self.removeHtmlSuccess()

        self.genData()

    def getUrlDataFromRoute(self):

        file = open(self.file,"r")

        self.filetext = file.read()

        self.urls = re.findall('@[A-Za-z0-9._-]+route(.+)', self.filetext)

        addbase = self.baseUrls[0][:-1]

        for x in range(len(self.urls)):

            self.urls[x] = addbase+self.urls[x].replace("('","").replace("')","")

    def getUrlParamsFromFunc(self):

        for url in self.urls:

            newurl = url.replace(self.baseUrls[0],'/')

            textnospace = self.filetext.replace('\n',' ')

            textsearch = re.findall("@api {get} "+url+".*?{get}", textnospace)[0]

            params = re.findall("request.args.get(w+)",textsearch)

            for x in range(len(params)):

                params[x] = params[x].replace('request.args.get(','').replace(')','')

            self.urlParams[url] = params

    #Gets url data based on baseUrls and ApiDoc

    def getUrlData(self):

        for baseUrl in self.baseUrls:

            file = open(self.file,"r")

            self.filetext = file.read()

            self.urls = self.urls + re.findall('@api {get} '+baseUrl+'\w+/',self.filetext)

                   

        for x in range(len(self.urls)):

            self.urls[x] = self.urls[x].replace("@api {get} ","")

            print(self.urls[x])

        #Get Parameters for URLS

        for url in self.urls:

            params = []

            fullurl = re.findall('@api {get} '+url+'.+',self.filetext)

            params = re.findall('\w+=', fullurl[0])

            for x in range(len(params)):

                params[x] = params[x].replace('=','')

            self.urlParams[url] = params

    #Remove Pre-existing Html success response

    def removeHtmlSuccess(self):

        toRemove = re.findall('@apiSuccessExample Html Success-Response:\n.+\n.+\n.+\n.+',self.filetext)

        for r in toRemove:

            self.filetext = self.filetext.replace(r+'\n','')

    #NOT USED future support for param?

    def removeAllParams(self):

        toRemove = re.findall('@apiParam .+',self.filetext)

    #API Success table remove

    def removeAllApiSuccess(self):

        toRemove = re.findall('@apiSuccess .+',self.filetext)

        for r in toRemove:

            self.filetext = self.filetext.replace(r+'\n','')

    def removeAllApiGet(self):

        toRemove = re.findall('@api {get} .+',self.filetext)

        for r in toRemove:

            self.filetext = self.filetext.replace(r+'\n','')

    #Generates Success Responses. And adds to filetowrite inserts below @api {get} url in orginal code file

    def genData(self):

        self.removeAllApiSuccess()

        self.removeHtmlSuccess()

        self.removeAllApiGet()

        #Write @api {get}

        for url in self.urls:

            newurl = url.replace(self.baseUrls[0],'/')

            toReplace = re.findall("@[A-Za-z0-9._-]+route\('"+newurl+"'\)", self.filetext)[0]

            self.filetext = self.filetext.replace(toReplace,'"""@api {get} '+url+' \n'+toReplace)

            file = open(self.filetoWrite,"w")

            file.write(self.filetext)

        self.getUrlParamsFromFunc()

        for url in self.urls:

            resp = requests.get(self.realBase+url+'/'+'?date=2020-06-24',verify=False)

            try:

                data = resp.json()

                htmlresp = resp.text

            except:

                print('Data failure.')

                continue

            htmlsuccess = "@apiSuccessExample Html Success-Response:\n      HTTP/1.1 200 OK\n     {\n"+htmlresp+"\n      }\n"

            columnData = data["col_display"]

            typeData = data["meta"]

            exampleData = data["data"]

            if(not len(exampleData)==0 and len(exampleData[0])==0):

                for i in range(len(exampleData)):

                    exampleData[i].append('')

            apidocTable = ''

            for x in range(len(columnData)):

                apidocTable += "@apiSuccess "+"{"+str(typeData[x])+"} "+str(columnData[x]).replace(" ", '-').replace('%', 'Percent').replace('(Percent)','-Percent').replace('(', '').replace(')','').replace('#','number')+" Ex. "+str(exampleData[x][0])+"\n"

            print(apidocTable)

            toReplace = re.findall('@api {get} '+url+'.+',self.filetext)

            self.filetext = self.filetext.replace(toReplace[0],toReplace[0]+'\n'+apidocTable+'\n'+htmlsuccess+'\n"""')

        file = open(self.filetoWrite,"w")

        file.write(self.filetext)

        print(self.filetext)

       

run = genTables()

