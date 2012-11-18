from django.template import Library
register = Library()

@register.filter 
def truncatechars(value,arg=50): 
    '''
    Takes a string and truncates it to the requested amount, by inserting an ellipses into the middle.
    ''' 
    arg = int(arg) 
    if arg < len(value): 
        half = (arg-3)/2 
        return "%s...%s" % (value[:half],value[-half:]) 
    return value 
