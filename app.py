# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
from datetime import datetime
from time import strptime
import settings
import sys, os

sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db


def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host,
        settings.mysql_user,
        settings.mysql_passwd,
        settings.mysql_schema)

    return con

# Used for testing: X=50, Y=20
def findAirlinebyAge(x, y):
    # Validations
    try:
        minAgeLimit = int(y)
    except:
        return [("Invalid Parameters. Please Enter an Integer on Y",)]
    try:
        maxAgeLimit = int(x)
    except:
        return [("Invalid Parameters. Please Enter an Integer on X",)]

    if (maxAgeLimit < 0 or minAgeLimit < 0):
        return [("Age restrictors Can't be less than zero. Please try again",)]

    if (maxAgeLimit < minAgeLimit):
        return [("Max Age can't be less than minimum age. Please try again",)]

    # Create a new connection
    con = connection()
    listOfResultTuples = [("airline_name", "num_of_passengers", "num_of_aircrafts")]
    # Create a cursor on the connection
    sqlQuery = f""" SELECT airlines.name airlines_name,
                        COUNT(DISTINCT flights_has_passengers.passengers_id) num_of_passengers,
                        COUNT(DISTINCT airlines_has_airplanes.airplanes_id)	num_of_aircrafts
                    FROM flights, 
                        flights_has_passengers, 
                        passengers, 
                        routes, 
                        airlines,
                        airlines_has_airplanes
                    WHERE 1=1 
                        AND flights.id = flights_has_passengers.flights_id
                        AND passengers.id = flights_has_passengers.passengers_id
                        AND flights.routes_id = routes.id
                        AND routes.airlines_id = airlines.id
                        AND airlines.id = airlines_has_airplanes.airlines_id
                        AND 2022 - passengers.year_of_birth > {minAgeLimit}
                        AND 2022 - passengers.year_of_birth < {maxAgeLimit}
                    GROUP BY airlines.name """
    cur = con.cursor()
    cur.execute(sqlQuery)
    queryResults = cur.fetchall()
    for result in queryResults:
        listOfResultTuples.append(result)

    cur.close()
    con.close()
    return listOfResultTuples

# Used for testing: X=Aegean Airlines, A=2010-03-01, B=2022-07-17
def findAirportVisitors(x, a, b):
    # Validations
    try:
        dateFrom = datetime.strptime(a, '%Y-%m-%d').date()
    except:
        return [("Invalid Parameters. Please Enter a Date on a",)]
    try:
        dateTo = datetime.strptime(b, '%Y-%m-%d').date()
    except:
        return [("Invalid Parameters. Please Enter a Date on b",)]

    if (dateFrom > dateTo):
        return [("Invalid Parameters. Date A must be prior to B",)]

    # Create a new connection
    con = connection()
    listOfResultTuples = [("aiport_name", "number_of_visitors")]


    # Get all airlines
    getAllAirlines = f"""   SELECT airlines.name
                            FROM airlines
                            """
    cur = con.cursor()
    cur.execute(getAllAirlines)
    queryResults = cur.fetchall()
    listOfAirlines = []
    for result in queryResults:
        listOfAirlines.append(result)
    out = [item for t in listOfAirlines for item in t]
    # Check if given airline alias exists
    if (x not in out):
        return [("Airline Not Found",)]

    
    # Create a cursor on the connection

    sqlQuery = f""" SELECT airports.name, 
                        COUNT(flights_has_passengers.passengers_id) AS 'number_of_visitors'
                    FROM airports,
                        flights,
                        flights_has_passengers,
                        airlines,
                        routes
                    WHERE 1=1
                        AND flights.id = flights_has_passengers.flights_id
                        AND flights.routes_id = routes.id
                        AND routes.airlines_id = airlines.id
                        AND (airports.id = routes.destination_id)
                        AND flights.date > '{dateFrom}'
                        AND flights.date < '{dateTo}'
                        AND airlines.name = '{x}'
                    GROUP BY airports.name
                    ORDER BY number_of_visitors DESC"""
    var = cur.execute(sqlQuery)
    queryResults = cur.fetchall()
    for result in queryResults:
        listOfResultTuples.append(result)

    cur.close()
    con.close()
    return listOfResultTuples


# Used for testing: X=2014-11-03, A=Male, B=Dubai
def findFlights(x, a, b):
    # Validations
    try:
        date = datetime.strptime(x, '%Y-%m-%d').date()
    except:
        return [("Invalid Parameters. Please Enter a Date on a",)]

    # Create a new connection
    con = connection()

    listOfResultTuples = [("flight_id", "alt_name", "dest_name", "aircraft_model"), ]

    sqlQuery = f""" SELECT flights.id flight_id,
                            airlines.alias alt_name,
                            dst.name dest_name,
                            airplanes.model aircraft_model
                    FROM flights, 
                        airlines,
                        routes,
                        airplanes,
                        airports src,
                        airports dst
                    WHERE 1=1
                        AND flights.routes_id = routes.id
                        AND routes.airlines_id = airlines.id
                        AND flights.airplanes_id = airplanes.id
                        AND src.id = routes.source_id
                        AND dst.id = routes.destination_id
                        AND airlines.active = 'Y'
                        AND src.city = '{a}'
                        AND dst.city = '{b}'
                        AND flights.date = '{date}'"""
    # Create a cursor on the connection
    cur = con.cursor()
    var = cur.execute(sqlQuery)
    queryResults = cur.fetchall()
    for result in queryResults:
        listOfResultTuples.append(result)
    
    cur.close()
    con.close()
    return listOfResultTuples

# Used for testing: N=1,...,10
def findLargestAirlines(N):
    # Validations
    try:
        maxNumberOfResults = int(N)
    except:
        return [("Invalid Parameters. Please Enter an Integer",)]
    if (maxNumberOfResults < 0):
        return [("Number of elements can't be less than zero. Please try again",)]
    # Create a new connection
    con = connection()
    # Create a cursor on the connection
    cur = con.cursor()
    
    sqlQuery = """  SELECT airlines.name AS 'name',
                        airlines.code AS 'id',
                        COUNT(DISTINCT airplanes.id) AS 'num_of_aircrafts',
                        COUNT(DISTINCT flights.id) AS 'num_of_flights'
                    FROM flights,
                        routes,
                        airlines,
                        airlines_has_airplanes,
                        airplanes
                    WHERE 1=1
                        AND flights.routes_id = routes.id
                        AND airplanes.id = airlines_has_airplanes.airplanes_id
                        AND airlines.id = airlines_has_airplanes.airlines_id
                        AND routes.airlines_id = airlines.id
                    GROUP BY airlines.code, airlines.name
                    ORDER BY num_of_flights DESC"""
    listOfResultTuples = [("name", "id", "num_of_aircrafts", "num_of_flights")]
    count = 0

    cur.execute(sqlQuery)
    queryResults = cur.fetchall()

    for result in queryResults:
        if (count == 0):
            previousResult = result
        else:
            previousResult = listOfResultTuples[-1]
        count += 1
        if (count > maxNumberOfResults and previousResult[-1] != result[-1]):
            break
        listOfResultTuples.append(result)

    cur.close()
    con.close()
    return listOfResultTuples

# Used for testing: X=Air Asia, Y=Kalibo
def insertNewRoute(x, y):
    # Create a new connection
    con = connection()

    # Validations
    getAllAliases = f"""SELECT DISTINCT alias
                            FROM airlines
                            WHERE 1=1
                                AND airlines.alias IS NOT NULL
                                AND airlines.alias != "" """
    cur = con.cursor()
    cur.execute(getAllAliases)
    queryResults = cur.fetchall()
    listOfAliases = []
    for result in queryResults:
        listOfAliases.append(result)
    out = [item for t in listOfAliases for item in t]
    if (x not in out):
        return [("Alias Not Found",)]

    getAllAirports = f"""SELECT name
                            FROM airports"""
    cur.execute(getAllAirports)
    queryResults = cur.fetchall()
    listOfAirports = []
    for result in queryResults:
        listOfAirports.append(result)
    out = [item for t in listOfAirports for item in t]
    if (y not in out):
        return [("Airport Not Found",)]


    sqlQuery = f"""SELECT airports.id
                        FROM airports
                        WHERE airports.id  NOT IN 
                        (SELECT routes.destination_id 
                            FROM airports, routes, airlines 
                            WHERE routes.airlines_id = airlines.id AND routes.source_id = airports.id 
                            AND airlines.alias = '{x}' AND airports.name = '{y}')
                        AND airports.name != '{y}'"""

    numberOfResults = cur.execute(sqlQuery)
    destination_id = cur.fetchone()
    if (numberOfResults == 0):
        return [("Airline capacity full", )]

    # Get necesssary info to create record
    sqlQuery = f"""SELECT airlines.id
                        FROM airlines
                        WHERE airlines.alias = '{x}'"""
    cur.execute(sqlQuery)
    airline_id = cur.fetchone()

    sqlQuery = f"""SELECT airports.id
                            FROM airports
                            WHERE airports.name = '{y}'"""
    testing = cur.execute(sqlQuery)

    source_id = cur.fetchone()

    sqlQuery = f"""SELECT MAX(id) + 1
                    FROM routes"""
    cur.execute(sqlQuery)
    new_route_id = cur.fetchone()

    sqlQuery = f"""INSERT INTO routes
                    VALUES ('{new_route_id[0]}', '{airline_id[0]}', '{source_id[0]}', '{destination_id[0]}')"""
    cur.execute(sqlQuery)


    cur.close()
    con.close()
    return [("OK", ) ]