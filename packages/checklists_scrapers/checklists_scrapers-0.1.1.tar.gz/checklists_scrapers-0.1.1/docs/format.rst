=====================
Checklist File Format
=====================

A checklist is a nested dictionary with key-value pairs for the date, location,
observers, the list of the species seen, etc. Files are saved in JSON format
to make it easy to transport and process the information.

There is no standard format, though there are fields that are common to most
(all) data sources, with date, name of the location and the list of species
seen being the most obvious examples. The scrapers that parse the different
sources attempt to extract all the information available for a given checklist
and the nested dictionary format makes it easy to accommodate this while
keeping the (formatted) files human-readable.

A typical checklist has the following structure. ::

    {
        "meta": {
            "version": 1,
            "language": "en",
        },
        "identifier": "S1234567",
        "date": "2013-07-05",
        "location": {
            "identifier": "L12345",
            "name": "Cape Clear",
            "county": "Cork",
            "region": "",
            "country": "Eire",
            "lat": 51.433333,
            "lon": -9.5
        },
        "activity": "Seawatching",
        "protocol": {
            "name": "Stationary",
            "time": "07:00",
            "duration_hours": 3,
            "duration_minutes": 25,
            "area": 0,
            "distance": 0,
        },
        "observers": {
            'count': 5,
            'names': [
                "Martin Swift",
                "Bob Roller",
                "June Finch"
            ]
        },
        "source": {
            "name": "ebird",
            "url": "http://http://ebird.org/ebird/view/checklist?subID=S12345",
            "submitted_by": "Martin Swift",
        },
        "entries": [
            {
                "identifier": "OBS12345",
                "species": {
                    "name": "Manx Shearwater",
                    "scientific_name": "Puffinus puffinus"
                },
                "count": 22,
                "comment": "Flying west"
            },
            {
                "identifier": "OBS12346",
                "species": {
                    "name": "Gannet",
                },
                "count": 45,
                "comment": "Flying east",
                "details": [
                    {
                        "age": "Adult",
                        "sex": "Sex Unknown",
                        "count": 26
                    },
                    {
                        "age": "Immature",
                        "sex": "Sex Unknown",
                        "count": 19
                    }
                ]
            },
            ...
        ]
    }

**Meta**

This contains information added by the scraper. ::

        "meta": {
            "version": 1,
            "language: "en",
        }


Currently there are two attributes: **version** is the revision number for the
format used in the checklist file. It will be incremented for each
incompatible* change to the existing format; **language** is the two-letter,
ISO 639-1 code used to identify the spoken language used in species names and
comments. Currently the scrapers only generate checklists in English, 'en'.

*Since this project is in an early stage of development, currently there are
only scrapers for eBird and WorldBirds, what exactly constitutes an
incompatible change is not clearly defined. If the latitude and longitude
of the location were moved to a dictionary that added grid references, that
is clearly incompatible with existing code that processed the files.
However, adding new categories of information such as weather conditions is
currently considered not to be incompatible.

**Identifier**

This is the identifier for the checklist given by the source. When combined
with the name of the source this should be unique. This allows a checklist
to be loaded into a database repeatedly, at first adding then updating the
existing record.

The identifier is an effective shorthand way of referencing a checklist.
The alternative is the combination of date, time, location name, the name
of the observer who submitted the checklist and the name of the source. The
date, time and location name are not sufficient to uniquely identify the
checklist since it may be submitted by the same observer to multiple
sources or by different observers to the same source. In these situations
the checklists should be considered separate even though they contain the
same set of observations. It is much easier simply to ignore the duplicates
rather than try and merge them together when adding the checklists to a
database for example.

**Date**

This is the date when the observations were made. It follows the ISO 8601
format, YYYY-MM-DD.

**Location**

Contains information about the place were the observations were made. ::

    "location": {
        "identifier": "L12345",
        "name": "Cape Clear",
        "county": "Cork",
        "region": "",
        "country": "Eire",
        "lat": 51.433333,
        "lon": -9.5
    }

Usually the **name** is sufficient to uniquely identify a given location, at
least for limited geographical areas. As the areas increase, **county**,
**region** or even **country** may be required to uniquely identify a location.
The latitude, **lat** and longitude, **lon** *should* be sufficient but often
these are given by the person who submitted the checklist and are highly
variable and prone to error such that they are not reliable, see next.

There is also an **identifier** for the location. This is less useful since
there may be several different names in use for a given location within a
given source (eBird is moderated so most locations names are standardized
with unique names, but that is not a requirement. WorldBirds, by contrast,
is not moderated so often there are several different names for the same
location or several locations in close proximity that they should be
treated as one). It is a similar story with the latitude and longitude,
more so since these are floating-point numbers.

When loading the location into a database, one technique is to used a table
of aliases which map all the different variations in name to a single
location. The same thing could be done for the identifiers, though that is
more difficult to maintain.

**Activity**

This is a simple description, usually one or two words, of what the
observers were doing when the checklist was created. It is useful to
distinguish between surveys (winter atlas counts) or specialized activities
(seawatching, viz migging, etc.) and more general birding.

When combined with the protocol information it is a great way of
identifying which checklists were carried out as a standardized activity
with a standardized protocol, e.g. counts of migrating raptors from a fixed
vantage point. This makes it easier to identify checklists which could be
used for scientific or conservation purposes.

**Protocol**

This describes how the count was carried out. ::

    "protocol": {
        "name": "Stationary",
        "time": "07:00",
        "duration_hours": 3,
        "duration_minutes": 25,
        "area": 0,
        "distance": 0,
    }

The **name** field describes the protocol, e.g. "Traveling", "Stationary", etc.
Depending on the name then a number of other parameters are defined. **Time**
is when the count started. It uses the 24-hour clock in the format HH:MM.
**Duration_hours** and **duration_minutes** represent the time spent counting
birds and when combined with the number of observers give a measure of the
effort expended. **Area** is the area, in square meters, covered when counting.
Meters are used since this is the lowest denominator that provides any accuracy
(This this might change in future as very few checklists use this method so
there is not much real-world data to decide whether meters are a good idea or
not). **Distance** is the distance travelled, again in meters. Distances
less than 1 kilometer are common and using meters also provides sufficient
resolution for deal with source which express distances covered in miles.

The value for duration, distance and area use integers to avoid any issues
with rounding errors. All the values will be defined in every checklist.
If they are not relevant for the protocol i.e. distance for a Stationary
protocol then the value will be zero.

Protocol is optional. It will be omitted if the checklist did not follow a
standard methodology. This makes it easy to mix checklists together while
still being able to access the ones where an analysis of the observations
is possible because a standard methodology was used.

**Observers**

This is the list of people who participated in the count.
::

    "observers": {
        'count': 5,
        'names': [
            "Martin Swift",
            "Bob Roller",
            "June Finch"
        ]
    }

**Names** is simply a list of identifiers for the people involved. Usually
this is their full name but, depending on the source, this might also be a
list of usernames. **Count** is included as the names of all observers might
not be available but the number of observers is important in order to calculate
the effort expended when analyzing checklists.

**Source**

Source contains information about where the checklist came from.. ::

    "source": {
        "name": "ebird",
        "url": "http://http://ebird.org/ebird/view/checklist?subID=S12345",
        "submitted_by": "Martin Swift",
    }

**Name** is a short name for the source, e.g. "ebird"; **submitted_by** is the
name of the observer who submitted the checklist to the source - usually a real
name; **url** is the web page where the information was extracted from.
The URL may not always be publicly visible. An account is need to extract
checklists from WorldBirds and the URL uses an undocumented internal API
to fetch the data from the server - pasting it into a browser does work
however. The URL is a reference back to the original data and should be
used for verifying or correcting a checklists contents. Particularly in the
case of checklists from WorldBirds, it should not be re-published.

**Entries**

This is the list of observations.. ::

    "entries": [
        {
            "identifier": "OBS12345",
            "species": {
                "name": "Manx Shearwater",
                "scientific_name": "Puffinus puffinus"
            },
            "count": 22,
            "comment": "Flying west"
        },
        ...
    ]

Each entry contains a **species** (which is a dictionary containing at least
the common **name** (using the language from the meta dictionary) along with,
optionally, the **scientific_name**; and a **count** which is the number of
individuals seen. The **identifier** works in the same way as the checklist
identifier, uniquely identifying a given observation for a given checklist. It
is not guaranteed to be present but it makes life a lot easier when loading the
checklist into a database since it ensures that if the checklist is edited at
the source after it was first downloaded that the changes can be successfully
copied. The alternative is to use the species and count together but some
sources, e.g. WorldBirds allow checklists to contain multiple entries for the
same species so in these situations the only reliable action when re-loading
a checklist is to delete all the existing entries and re-add them, losing
any local changes such as comments in the process. A **comment** field is
also included for any additional information about the observation.

**Details**

Provides more information about a count. ::

    "entries": [
        ...
        {
            "identifier": "OBS12346",
            "species": {
                "name": "Gannet",
            },
            "count": 45,
            "comment": "Flying east"
            "details": [
                {
                    "age": "Adult",
                    "sex": "Sex Unknown",
                    "count": 26
                },
                {
                    "age": "Immature",
                    "sex": "Sex Unknown",
                    "count": 19
                }
            ]
        },
        ...
    ]

The **details**, currently only defined for checklists from eBird, provide
a breakdown of the count by age and sex. This is a list which contains
the **count** of the individuals seen for a given **age** and/or **sex**.
The length of the list can vary and there is no requirement that the total
of the counts match the count for the entry - though obviously it should
not exceed it.

Future Changes
--------------
The current format (version 1) covers the data available from the first two
sources for which scrapers are available, namely eBird and WorldBirds (the
latter has a number of different databases for different countries). As more
sources are added then the format is likely to change, though hopefully this
will be the addition of new fields rather than changes to the ones documented
above.

From the current sources, all the available information is extracted, except
the breeding status field from eBird. This was omitted because an earlier
version of checklists_scrapers used codes for fields such as the protocol names
and it was not clear how to incorporate the breeding status. With the recent
move to simply use the name given in the source, adding the breeding status is
a simple change and will likely happen sooner rather than later.
