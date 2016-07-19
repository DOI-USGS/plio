import krc.config as config

def j2season(_date):
    """
    Ls date to a KRC season.

    Parameters
    -----------
    _date : float
   	    The input date to be converted

    Returns
    -------
    startseason : int
		  The integer index to the start season
    stopseasons : int
		  The integer index to the stop season
    """
    date = _date
    if date < config.RECORD_START_DATE:
        remainder = (config.RECORD_START_DATE - date) / config.YEAR
        date = date + int(remainder + 1.0) * config.YEAR
    dateoffset = (date - config.RECORD_START_DATE) % config.YEAR
    recordoffset = dateoffset / config.MARTIAN_DAY
    startseason = int(recordoffset)
    stopseason = startseason + 1
    return recordoffset, startseason, stopseason

