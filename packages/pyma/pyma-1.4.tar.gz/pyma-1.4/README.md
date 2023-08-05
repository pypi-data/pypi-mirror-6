#pyma

This library provide simple moving average function. Pyma is prononced /paɪ ˈɛm ˈa/ or Pie M A.

##List of Included Function
Functions are inside class to provide a simple iterative callable interface and ensure persistent config through every calculation.


* SimpleMA(n) - Moving Average over the last n day/data.
* EMA(a) - Exponential Moving Average with a as the alpha parameter.
* NDayEMA -	Exponential Moving Average over n day/data as defined in wikipedia. Equivalent to using EMA(a) with a = 2/(n+1).
* CMA - Cumulative Moving Average.
* WMA - Weighted Moving Average, the weight function decrease in arithmetical progression with a difference equal to 

* Some common NDayEMA 
    *EMA20
    *EMA7
    *EMAW (for week, identical to EMA7)
    *EMA5

##usage exemple
###SimpleEMA

	import pyma
	# Instantiate a SimpleMA tool class and compute a SimpleMA over some data/day.
	SimpleMA = pyma.SimpleMA(5, "0") 
	#You can specify a placeholder string like "-" or "0" as a second argument. 
	#It will be use instead of returning a incomplete MA

	SimpleMA.compute(2) 		#return "0", #the placeholder provided
	SimpleMA.compute(3) 		#return "0".
	SimpleMA.compute(5) 		#return "0"
	SimpleMA.compute(3) 		#return "0".
	SimpleMA.compute(3) 		#return 3.2, finally we have 5 days/data.
	SimpleMA.compute(3, 7) 		#return 4.2.
	SimpleMA.compute(3, 2.5464) #return 4.10928.
	SimpleMA.compute(3, 9) 		#return 4.90928.

###SimpleEMA, with no placeholder
	
	import pyma
	# Instantiate a SimpleMA tool class and compute a SimpleMA over some data/day.
	SimpleMA = pyma.SimpleMA(5) 

	SimpleMA.compute(2) 		#return 2.0,
	SimpleMA.compute(3) 		#return 2.5.
	SimpleMA.compute(5) 		#return 3.3333...
	SimpleMA.compute(3) 		#return 3.25.
	SimpleMA.compute(3) 		#return 3.2, finally we have 5 days/data.
	SimpleMA.compute(3, 7) 		#return 4.2.
	SimpleMA.compute(3, 2.5464) #return 4.10928.
	SimpleMA.compute(3, 9) 		#return 4.90928.

###EMA

	import pyma
	# Instantiate a EMA tool class and compute a EMA over some data,
	#set alpha to 0.2.
	# See wikipedia for information about Exponential moving average
	# and the alpha parameter.
	EMA = pyma.EMA(0.2)

	round(EMA.compute(29.341320155),5) 		#return 29.34132
	round(EMA.compute(44.779564776),5)		#return 32.42897
	round(EMA.compute(51.659712089),5)		#return 36.27512
	round(EMA.compute(50.7477490173),5)		#return 39.16964

###NDayEMA

	import pyma
	NDayEMA = pyma.NDayEMA(n)
	NDayEMA.compute(3)
	...

###WMA
	import pyma
	WMA = pyma.WMA(5)
	print WMA.compute(1)
	...

###WMA, with empty placeholder
	import pyma
	WMA = pyma.WMA(5, "-")
	print WMA.compute(1)
	...

###CMA
	import pyma
	CMA = pyma.CMA()
	print CMA.compute(1)
	print CMA.compute(10)
	print CMA.compute(4)
	print CMA.compute(10)
	...
	
### Notes
Dynamic function won't be implemented. It look like it may be a bad idea. http://stackoverflow.com/questions/20938986/creating-a-dynamically-named-function-at-runtime

##TODO
* Add simple weight moving average with user made weight function
* Add (wiki),, simple moving mean
* Add custom difference value to WMA arithmetical weight function
