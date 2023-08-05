from stockwrapper import YahooData
import pylab

data = YahooData()

fran_hist = data.get_historical('FRAN.BA')

dates = [item['Date'] for item in fran_hist]
close = [item['AdjClose'] for item in fran_hist]

ndates = pylab.datestr2num(dates)

pylab.plot_date(ndates, close)
pylab.title("FRAN.BA" + " historical prices")
pylab.ylabel("Price")
pylab.xlabel("Date")
pylab.grid(True)
pylab.show()
