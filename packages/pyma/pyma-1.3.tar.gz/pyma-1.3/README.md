#pyma

This library provide simple moving average function. Pyma is prononced /paɪ ˈɛm ˈa/ or Pie M A.

##List of Included Function
Functions are inside class to provide a simple iterative callable interface.

* SimpleMA(n) 	This function calculate the moving average over the last n day/data.
* EMA(a)		This function calculate the exponential moving average with a as the alpha parameter.
* NDayEMA		This function calculate the exponential moving average over N day/data as define in wikipedias. Equivalent to using EMA(a) with a = 2/(n+1)
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

##TODO
*Add dynamic class like EMA23, EMA234, EMA70 ...
*Add an option to have non-empty first value for SimpleEMA.
*Add simple weight moving average with user made weight function
*Add (wiki),, simple moving mean