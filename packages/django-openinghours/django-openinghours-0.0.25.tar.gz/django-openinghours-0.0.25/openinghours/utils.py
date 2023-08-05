import datetime

from .models import *

def getClosingRuleForNow(companySlug, now=None):
    '''
    Access the all closing rules for a company
    '''
    if now is None:
        now = datetime.datetime.now()
    cr = ClosingRules.objects.filter(company__slug=companySlug, start__lte=now, end__gte=now)
    return cr
    
    
def hasClosingRuleForNow(companySlug, now=None):
    '''
    Has the company closing rules to evaluate?
    '''
    cr = getClosingRuleForNow(companySlug, now)
    return cr.count()
    
    
def isOpen(companySlug, now=None):
    '''
    Is the company currently open? Pass "now" to test with a specific timestamp.
    This method is used as stand alone and helper.
    '''
    if now is None:
        now = datetime.datetime.now()
    print "isOpen", now, now.isoweekday()
    
    if hasClosingRuleForNow(companySlug, now):
        return False
        
    nowTime = datetime.time(now.hour, now.minute, now.second)
    
    ohs = OpeningHours.objects.filter(company__slug=companySlug)
    for oh in ohs:
        is_open = False
        # start and end is on the same day
        if oh.weekday == now.isoweekday() and oh.fromHour <= nowTime and nowTime <= oh.toHour: 
           is_open = oh
        
        # start and end are not on the same day and we test on the start day
        if oh.weekday == now.isoweekday() and oh.fromHour <= nowTime and ((oh.toHour < oh.fromHour) and (nowTime < datetime.time(23, 59, 59))):
            is_open = oh
            
        # start and end are not on the same day and we test on the end day
        if (oh.weekday == (now.isoweekday()-1)%7 and oh.fromHour >= nowTime and oh.toHour >= nowTime and oh.toHour < oh.fromHour):
            is_open = oh
            #print " 'Special' case after midnight", oh
        
        if is_open is not False:
            return oh
    return False
    

def isClosed(companySlug, now=None):
    ''' Inverse function for isOpen. '''
    return not isOpen(companySlug, now)
    
    
def nextTimeOpen(companySlug):
    ''' 
    Returns the next possible opening hours object ( aka when is the company open for the next time?).
    '''
    if isClosed(companySlug):
        now = datetime.datetime.now()
        nowTime = datetime.time(now.hour, now.minute, now.second)
        foundOpeningHours = False
        for i in range(8):
            lWeekday = (now.isoweekday()+i)%7
            ohs = OpeningHours.objects.filter(company__slug=companySlug, weekday=lWeekday).order_by('weekday','fromHour')
            
            if ohs.count():
                for oh in ohs:
                    futureNow = now + datetime.timedelta(days=i)
                    # same day issue
                    tmpNow = datetime.datetime(futureNow.year, futureNow.month, futureNow.day, oh.fromHour.hour, oh.fromHour.minute, oh.fromHour.second)
                    if tmpNow < now:
                        tmpNow = now # be sure to set the bound correctly...
                    if isOpen(companySlug, now=tmpNow):
                        foundOpeningHours = oh
                        break
                if foundOpeningHours is not False:
                    return foundOpeningHours, tmpNow
    return False
