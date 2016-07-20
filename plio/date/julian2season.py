def j2season(_date, year=686.9799625, marsday=8.5875, startdate=144.61074994):
    """
    Ls date to a KRC season to determine which KRC seasonal lookup tables to use

    Parameters
    -----------
    _date : float
   	        The input date to be converted

   	year : float
   	       The mars year to search within

   	marsday : float
   	          The length of a Mars day

   	startdate : float
   	            The zero, start date

    Returns
    -------
    startseason : int
		  The integer index to the start season
    stopseasons : int
		  The integer index to the stop season
    """
    date = _date
    if date < startdate:
        remainder = (startdate - date) / year
        date = date + int(remainder + 1.0) * year
    dateoffset = (date - startdate) % year
    recordoffset = dateoffset / marsday
    startseason = int(recordoffset)
    stopseason = startseason + 1
    return recordoffset, startseason, stopseason

