'''
@author: Brainerd Dharmaraj

This module has been created to provide functions that are useful in pricing and risk management of 
fixed-income securities. The goal is to break-down complex quantitative financial calculations into
easy-to-understand functions as much as possible. 

To begin with, there are two functions: 
    duration: calculates the Macaulay and Modified Durations.
    bondprice: provides an estimated price for a security for given basis point change.
    
More functions will be added periodically. 

'''
import math
import sys

def duration(coupon,maturity_amt,period,byield,no_of_coupons,price):
    '''
    Calculates Macaulay Duration and Modified Duration.
    
    Arguments: coupon: coupon payment
               maturity_amt: maturity (on par) value
               period: number of periods to maturity
               byield: percentage yield in decimal
               no_of_coupons: number of coupons in a year
               price: bond price
               
               returned_array[0] = Macaulay Duration
               returned_array[1] = Modified Duration
    '''  
    
    try:
        nparm1 = 0
        per = 1
                
        while per <= period:
            nparm1 = nparm1 + (per * coupon)/math.pow(1+byield,per)
            per += 1
            
        nparm2 = ((period * maturity_amt)/math.pow(1+byield, period))
        
        '''Macaulay Duration '''
        macdur = (nparm1 + nparm2)/price
                        
        '''Modified Duration '''
        moddur = macdur/(1 + (byield/no_of_coupons))
        
        dur = [macdur,moddur]
                                              
    except:
        e = sys.exc_info()[0]
        print(str(e))

    return dur


def bondprice(curr_price,mod_duration,convexity,basis_pt_chg):
    '''
    Returns an estimated price for a given security 
    
    Arguments: curr_price: current price of bond
               mod_duration: Modified Duration
               convexity
               basis_pt_chg: The chg in basis points for which the 
                             price needs to be estimated
    ''' 
    
    try:
        pctchg = (mod_duration * -1 * 0.01) + (convexity * math.pow(0.01,2))
        estimatedprice = curr_price * (1 + pctchg) 
    except:
        e = sys.exc_info()[0]
        print(str(e))
      
    return estimatedprice  
    
    
    
    

             
    