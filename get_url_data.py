'''Download the lib from github url https://github.com/loop-assembly/url-file-downloader '''
import DmAll

####################################################################################
'''Give the url and the file name, it will download the file and save it in the file name'''
####################################################################################




url='https://query1.finance.yahoo.com/v7/finance/download/TSLA?period1=1611987192&period2=1643523192&interval=1d&events=history&includeAdjustedClose=true'
DmAll.download(url)

