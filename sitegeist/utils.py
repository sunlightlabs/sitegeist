def age2ym(age):
    """ Convert a float age to a years and months tuple. For example,
        2.5 years would return (2, 6).
    """
    try:
        years = int(age)
        months = int(12 * (age - years))
    except:
        years = None
        months = None
    return (years, months)
