This package provides class to control the GPIO on Cubieboard A10.
Current release does no support any peripheral functions.
This package is an apapted version of pyA20 for Olimex's OLinuXino-A20.

Example
=======

Typical usage::
    
    #!/usr/bin/env python

    import A10_GPIO as GPIO

    #init module
    GPIO.init()
    
    #configure module
    GPIO.setcfg(GPIO.PD2, GPIO.OUTPUT)
    GPIO.setcfg(GPIO.PD3, GPIO.INPUT)
        
    #read the current GPIO configuration
    config = GPIO.getcfg(GPIO.PD2)
    
    #set GPIO high
    GPIO.output(GPIO.PD2, GPIO.HIGH)
    
    #set GPIO low
    GPIO.output(GPIO.PD2, GPIO.LOW)
    
    #read input
    state = GPIO.input(GPIO.PD3)
    
    #cleanup 
    GPIO.cleanup()
    

Warning
=======

    Before using this tool it is HIGHLY RECOMENDED to check Cubieboard A10
    schematic on http://linux-sunxi.org.

