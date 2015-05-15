"""
Initial notes:


After 3 times, a veset is established
    Even once it is established, if it diverges once, you need to be concerned about the others
    can only be replaced with another veset kevua.



Veset Haflaga - time difference between them.
    Always need to be concerned for this.
    Only applicable for someone with a history of two sightings

Details - Must be at same day/night.

Ona benenis
    30th day
    only if no kevua

veset hashvua:
    Same day of week, with at least a 4-week gap

Veset hadilug:
    either ascending or descending at the same rate (11,12,13 or 11,13,15 of month) or gap of (28,29,30 or 28,30,32). Or backwards (13,12,11 or 15,13,11) or backwards gaps (30,29,28 or 30, 28, 26)
    Not choshesh unless 3x

veset haseirug:
    2 month gaps, same day of month.
"""

import logging

from calendrical_calculations import GregorianDate, HebrewDate, LastDayOfHebrewMonth


"""
Programming methodology as follows:
For each Veset,
Input: The list of sightings. Each sighting is the date and whether it was at day or night.
Output: (date, time_period) it became kavua (if it did), kavua value(day of month, difference between), kavua status, next kavua date/time (for separation), next non-kavua date (for separation)
"""

class Sighting:
    def __init__(self, date, time_period):
        """
        date is a calendrical_calculations.GregorianDate
        time_period is either "day" or "night"
        """
        # Validate first
        if time_period not in ["day", "night"]:
            raise Exception("Invalid value for time_period: %s" % time_period)
        
        self.date = date
        self.time_period = time_period
    
    @property
    def hebrew_day_of_month(self):
        """Calculates the day of the month in the Hebrew calendar"""
        # If the period began at night, it's one day later on the Hebrew calendar
        if self.time_period == 'day':
            hebrew_day = HebrewDate.from_absolute(self.date.to_absolute()).day
        else:
            hebrew_day = HebrewDate.from_absolute(self.date.to_absolute() + 1).day
        return hebrew_day
    
    def __eq__(self, other):
        return self.date == other.date and self.time_period == other.time_period
    
    def __ne__(self, other):
        return not(self == other)
        
    def __str__(self):
        return "%s/%s" % (self.date, self.time_period)
        

def next_occurence_of_day(hebrewdate):
    pass

def veset_hachodesh(sightings):
    """
    Veset Hachodesh - same day of month  (2nd of month), established with 3 occurrences.
    Always need to be concerned for this veset, even if it isn't established.
    (1st day is the day of. so on a 29-day month, this is 30 days later, in a 30day month, this is 31 days later)
    How are 30-day months handled? Are you careful on the following day 1, or get a freebie? We're working with freebie for now.
    """
    logging.debug("Beginning Veset Hachodesh calculations")
    
    if not sightings:
        return None, None, None, None, None

    # Was there any veset kevua, ever?
    was_established = False
    # Is there a veset kevua, right now?
    is_established = False
    # What (day of month, time_period) was the veset kevua established for?
    established_day_of_month_time_period = None
    # What sighting established it?
    established_sighting = None
    # If it's based on a re-establishment, when was that?
    #re_established_sighting = None
    
    previous_day_time_period = (None, None)
    relevant_sightings = []
    breaking_establishment = []

    for sighting in sightings:
        day_of_month_time_period = (sighting.hebrew_day_of_month, sighting.time_period)
        
        # Is this sighting relevant towards establishing a veset kavua?
        if day_of_month_time_period == previous_day_time_period or previous_day_time_period == (None, None):
            if day_of_month_time_period is None:
                logging.debug("Sighting was on %d at %s, first of establishing a new veset kavua" % day_of_month_time_period)
            else:
                logging.debug("Sighting was again on %d/%s" % day_of_month_time_period)
            relevant_sightings.append(sighting)            
        else:
            # Reset the count
            logging.debug("Today's day/time period of %d/%s has a different day from the previous: %d/%s" % 
                            (   day_of_month_time_period[0], day_of_month_time_period[1], 
                                previous_day_time_period[0], previous_day_time_period[1]))
            relevant_sightings = []
            # And this is our new first entry
            relevant_sightings.append(sighting)            
        
        #Is there a veset kevuah?
        if len(relevant_sightings) >= 3:
            was_established = True
            is_established = True
            established_day_of_month_time_period = day_of_month_time_period
            established_sighting = sighting
            #re_established_sighting = None
            logging.debug("Veset kevuah established for the veset hachodesh: %d/%s" % established_day_of_month_time_period)
        
        # Does this break a veset kevuah?
        if is_established:
            if day_of_month_time_period != established_day_of_month_time_period:
                breaking_establishment.append(sighting)
                if len(breaking_establishment) >= 3:
                    is_established = False
                    #re_established_sighting = None
            else:
                logging.debug("Veset kevuah for the veset hachodesh uprooted! %d/%s" % established_day_of_month_time_period)
                breaking_establishment = []
        
        # Will this re-establish a veset kevuah?
        if not is_established and day_of_month_time_period == established_day_of_month_time_period:
            logging.debug("Veset kevuah re-established for %d/%s!" % day_of_month_time_period)
            is_established = True
            #re_established_sighting = sighting
        
        # Prepare for the next iteration:
        previous_day_time_period = day_of_month_time_period
    
    # We've finished processing the sightings. Let's summarize our info:
    last_sighting = sightings[-1]
    logging.debug("Summary:")
    if not was_established:
        logging.debug("No veset kevuah for veset hachodesh established")
        logging.debug("The last sighting was on %d/%s" % (last_sighting.hebrew_day_of_month, last_sighting.time_period))
    else:
        logging.debug("A veset kevuah for veset hachodesh was established for %d/%s on %s" % (established_day_of_month_time_period[0], established_day_of_month_time_period[1], established_sighting.date))
        if is_established:
            logging.debug("The veset kevuah is still active")
        else:
            logging.debug("The veset kevuah was uprooted, and is no longer active. However, a single sighting on %d/%s will reinstate it" % established_day_of_month_time_period)
            logging.debug("The last sighting was on %d/%s" % (last_sighting.hebrew_day_of_month, last_sighting.time_period))
    
    
    # When are the dates of separation?
    # First for the 'estimate' date of anticipation
    # If it day 30 and next month is only 29 days, you get a freebie

    last_sighting_hebrew_date = HebrewDate.from_absolute(last_sighting.date.to_absolute())
    
    if last_sighting.hebrew_day_of_month == 30:
        # Get the number of days in the next month:
        guesstimate = last_sighting.date.to_absolute() + 27
        next_month_guesstimate = HebrewDate.from_absolute(guesstimate)
        while(next_month_guesstimate.month == last_sighting_hebrew_date.month):
            guesstimate += 1
            next_month_guesstimate = HebrewDate.from_absolute(guesstimate)
        next_month_days = LastDayOfHebrewMonth(next_month_guesstimate.month, next_month_guesstimate.year)

        logging.debug("Next month is month:%d, year:%d, with %d days" % (next_month_guesstimate.month, next_month_guesstimate.year, next_month_days))
        if next_month_days == 29:
            # Freebie!
            anticipated_for_day_of_month = None
        else:
            # Keep incrementing until we reach day 30:
            while(next_month_guesstimate.day != 30):
                guesstimate += 1
                next_month_guesstimate = HebrewDate.from_absolute(guesstimate)
            anticipated_for_day_of_month = next_month_guesstimate
    else:
        guesstimate = last_sighting.date.to_absolute() + 27
        next_month_guesstimate = HebrewDate.from_absolute(guesstimate)
        while(next_month_guesstimate.month == last_sighting_hebrew_date.month or next_month_guesstimate.day != last_sighting_hebrew_date.day):
            guesstimate += 1
            next_month_guesstimate = HebrewDate.from_absolute(guesstimate)
        anticipated_for_day_of_month = GregorianDate.from_absolute(next_month_guesstimate.to_absolute())
    
    logging.debug("Next day of anticipation (unestablished) is on: %s/%s" % (anticipated_for_day_of_month, last_sighting.time_period))
    
    # If a veset kavua was established, when does it fall out?
    # Note: It is impossible to have it established on day 30.
    if established_sighting and is_established:
        guesstimate = last_sighting.date.to_absolute() + 27
        next_month_guesstimate = HebrewDate.from_absolute(guesstimate)
        while(next_month_guesstimate.month == last_sighting_hebrew_date.month or next_month_guesstimate.day != established_sighting.hebrew_day_of_month):
            guesstimate += 1
            next_month_guesstimate = HebrewDate.from_absolute(guesstimate)
        anticipated_established_for_day_of_month = GregorianDate.from_absolute(next_month_guesstimate.to_absolute())
        logging.debug("Next day of anticipation (established) is on: %s/%s" % (anticipated_established_for_day_of_month, established_sighting.time_period))
    else:
        anticipated_established_for_day_of_month = None
        
    
    
    return established_sighting, established_day_of_month_time_period, is_established, anticipated_established_for_day_of_month, anticipated_for_day_of_month
                                        

def or_zaruah(sighting):
    pass
    """Time period before the one of the veset, no sex"""
    
        
def main():
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    
    sightings = [
                    Sighting(GregorianDate(9, 27, 1900), 'day'),    # 4th of Tishrei
                    Sighting(GregorianDate(10, 26, 1900), 'day'),   # 3rd of Cheshvan
                    Sighting(GregorianDate(11, 26, 1900), 'day'),   # 4th of Kislev
                    Sighting(GregorianDate(12, 23, 1900), 'night'), # 1st of Teves
                    Sighting(GregorianDate(1, 29, 1901), 'night'),  # 10th of Shvat
                    Sighting(GregorianDate(3, 6, 1901), 'day'), # 15th of Adar
                    Sighting(GregorianDate(4, 4, 1901), 'day'), # 15th of Nisan
                    Sighting(GregorianDate(5, 4, 1901), 'day'), # 15th of Iyyar
                    Sighting(GregorianDate(5, 28, 1901), 'day'), # 10th of Sivan
                    Sighting(GregorianDate(7, 1, 1901), 'night'), # 15th of Tamuz
                    Sighting(GregorianDate(7, 26, 1901), 'night'), # 11th of Av
                    Sighting(GregorianDate(8, 28, 1901), 'day'), # 12th of Elul
                    Sighting(GregorianDate(9, 27, 1901), 'day'), # 14th of Tishrei
    ]
    veset_hachodesh(sightings)

if __name__ == "__main__":
    main()
