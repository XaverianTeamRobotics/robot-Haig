def entry():
    print("Welcome to the Robot-Haig scouting tool, named in honor of the person this is replacing")
    # Create a basic text interface for a person to input team data, event data, and scouting data
    # Store the data in a persistent database
    # Team history can then be gathered from the Orange Alliance API and the FTCScout.org API
    # The data can be combined with the scouting data to create a ranking system,
    #               ideal alliance selection, and potential match outcomes

    # The data can be exported to a SQL database for further analysis
    # With the explaining done, let's get started

    # We need to create a database to store the data in
    # We will use SQLite for this
    # TODO: Later, we will allow the user to import an existing database, but for now, we will always create a new one
    # This will allow us to freely change the database structure without worrying about breaking the user's database
    # For now, we will always create/overwrite the database
    createDB()


def createDB():
    import sqlite3
    import os
    # First, we need to check if the database already exists
    # If it does, we will delete it
    if os.path.exists("scouting.db"):
        os.remove("scouting.db")

    # Now, we can create the database
    conn = sqlite3.connect("scouting.db")
    c = conn.cursor()

    # Now, we need to create the tables
    # We will create a table for teams, events, the user's home team, and matches

    # First, we will create the team table
    # This will store the team number, name, and location
    c.execute('''CREATE TABLE teams
                    (team_number integer, team_name text, team_location text)''')

    # Next, we will create the event table
    # This will store the event name, location, and date
    c.execute('''CREATE TABLE events
                    (event_name text, event_location text, event_date text, event_code text)''')

    # Next, we will create the home team table
    # This will store the team number, name, and location
    c.execute('''CREATE TABLE home_team
                    (team_number integer, team_name text, team_location text)''')

    # Finally, we will create the match table
    # This will store the match number, the teams in the match, and the scores, as well as the following data for
    # each team:
    #    totalPoints
    #    autoTerminalCones
    #    autoGroundCones
    #    autoLowCones
    #    autoMediumCones
    #    autoHighCones
    #    autoNavigationPoints
    #    autoPoints
    #    dcTerminalCones
    #    dcGroundCones
    #    dcLowCones
    #    dcMediumCones
    #    dcHighCones
    #    dcPoints
    #    coneOwnedJunctions
    #    beaconOwnedJunctions
    #    endgameNavigationPoints
    #    endgamePoints
    #    totalPointsNp
    c.execute('''CREATE TABLE matches
                    (event_code text, match_number text, red_number_1 integer, red_number_2 integer, 
                    blue_number_1 integer, blue_number_2 integer,
                    totalPoints_blue integer, autoTerminalCones_blue integer, autoGroundCones_blue integer,
                    autoLowCones_blue integer, autoMediumCones_blue integer, autoHighCones_blue integer,
                    autoNavigationPoints_blue integer, autoPoints_blue integer, dcTerminalCones_blue integer,
                    dcGroundCones_blue integer, dcLowCones_blue integer, dcMediumCones_blue integer,
                    dcHighCones_blue integer, dcPoints_blue integer, coneOwnedJunctions_blue integer,
                    beaconOwnedJunctions_blue integer, endgameNavigationPoints_blue integer, endgamePoints_blue integer,
                    totalPointsNp_blue integer, totalPoints_red integer, autoTerminalCones_red integer,
                    autoGroundCones_red integer, autoLowCones_red integer, autoMediumCones_red integer,
                    autoHighCones_red integer, autoNavigationPoints_red integer, autoPoints_red integer,
                    dcTerminalCones_red integer, dcGroundCones_red integer, dcLowCones_red integer,
                    dcMediumCones_red integer, dcHighCones_red integer, dcPoints_red integer,
                    coneOwnedJunctions_red integer, beaconOwnedJunctions_red integer,
                    endgameNavigationPoints_red integer, endgamePoints_red integer, totalPointsNp_red integer)''')

    # Now, we need to get the data from the user and establish a database that will continue to grow
    # We will start with the team data
    # We will ask the user for their team number, then we can get the rest of the data from the Orange Alliance API

    # First, we need to get the team number
    team_number = input("Please enter your team number: ")

    # Now, we need to get the team name and location from the FTCScout.org API
    # The API uses GraphQL queried at https://api.ftcscout.org/graphql
    # We will use the gql library to query the API
    import gql
    from gql.transport.requests import RequestsHTTPTransport

    # First, we need to create the transport
    transport = RequestsHTTPTransport(
        url='https://api.ftcscout.org/graphql',
        use_json=True,
        headers={
            "Content-type": "application/json"
        },
        verify=True,
        retries=3,
    )

    # Next, we need to create the client
    client = gql.Client(
        transport=transport,
        fetch_schema_from_transport=True,
    )

    # Now, we can query the API
    # We will query the API for the team name and location
    query = gql.gql('''
        query {
            teamByNumber(number: ''' + team_number + ''') {
                name
                schoolName
            }
        }
    ''')

    # Now, we can get the data from the API
    result = client.execute(query)

    # Now, we can get the team name and location from the result
    team_name = result['teamByNumber']['name']
    team_location = result['teamByNumber']['schoolName']

    # Now, we can insert the data into the database
    c.execute("INSERT INTO home_team VALUES (?, ?, ?)", (team_number, team_name, team_location))

    print("Your team is " + team_name + " from " + team_location)

    # Now, list all events that the team has attended
    # We will get the data from the same API as before
    # We will query the API for the team's events
    query = gql.gql('''
        query {
            teamByNumber(number: ''' + team_number + ''') {
                events(season: 2022) {
                    event{
                        name
                        venue
                        start
                        code
                    }
                }
            }
        }
    ''')

    # Now, we can get the data from the API
    result = client.execute(query)

    # Now, we can get the events from the result
    events = result['teamByNumber']['events']

    # Now we can add them to the database
    for event in events:
        c.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (event['event']['name'], event['event']['venue'],
                                                             event['event']['start'], event['event']['code']))

    # Now, the long part
    # Get team numbers for all teams that have attended the same events as the user's team
    # We will get the data from the same API as before

    # First, we need to get the events that the user's team has attended
    # This we can do by querying the database
    c.execute("SELECT event_code FROM events")
    event_codes = c.fetchall()

    # Now, we need to get the team numbers for all teams that have attended the same events
    # We will query the API for the team numbers
    query = gql.gql('''
        query {
            eventByCode(code: "''' + event_codes[0][0] + '''", season: 2022) {
                teams {
                    team {
                        number
                        name
                        schoolName
                    }
                }
            }
        }
    ''')

    # Now, we can get the data from the API
    result = client.execute(query)

    # Now, we can get the teams from the result
    teams = result['eventByCode']['teams']

    # Now we can add them to the database
    for team in teams:
        c.execute("INSERT INTO teams VALUES (?, ?, ?)", (team['team']['number'], team['team']['name'],
                                                         team['team']['schoolName']))

    # Now, we need to get all of the matches for the user's team
    # This includes the match number, event code, the 4 team numbers, the score, and the cone layout
    #                                                                     (which will be in JSON format)
    # We will get the data from the same API as before
    # We will query the API for the matches
    query = gql.gql('''
        query {
            teamByNumber(number: 19460) {
                matches(season: 2022) {
                    match {
                        matchNum
                            event {
                            code
                        }
                        teams {
                            teamNumber
                            station
                        }
                        scores{
                            ... on MatchScores2022 {
                              red {
                                totalPoints
                                autoTerminalCones
                                autoGroundCones
                                autoLowCones
                                autoMediumCones
                                autoHighCones
                                autoNavigationPoints
                                autoPoints
                                dcTerminalCones
                                dcGroundCones
                                dcLowCones
                                dcMediumCones
                                dcHighCones
                                dcPoints
                                coneOwnedJunctions
                                beaconOwnedJunctions
                                endgameNavigationPoints
                                endgamePoints
                                totalPointsNp
                              }
                              blue {
                                totalPoints
                                autoTerminalCones
                                autoGroundCones
                                autoLowCones
                                autoMediumCones
                                autoHighCones
                                autoNavigationPoints
                                autoPoints
                                dcTerminalCones
                                dcGroundCones
                                dcLowCones
                                dcMediumCones
                                dcHighCones
                                dcPoints
                                coneOwnedJunctions
                                beaconOwnedJunctions
                                endgameNavigationPoints
                                endgamePoints
                                totalPointsNp
                              }
                            }
                        }
                    }
                }
            }
        }
    ''')

    # Now, we can get the data from the API
    result = client.execute(query)

    # Now, we can get the matches from the result
    matches = result['teamByNumber']['matches']

    # Now we can add them to the database
    # This query will be very long, because the table has 46 columns
    for match in matches:
        c.execute('''INSERT INTO matches VALUES (
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
        )''',
                  (match['match']['event']['code'], match['match']['matchNum'], match['match']['teams'][0]['teamNumber'],
                   match['match']['teams'][1]['teamNumber'], match['match']['teams'][2]['teamNumber'],
                   match['match']['teams'][3]['teamNumber'], match['match']['scores']['red']['totalPoints'],
                   match['match']['scores']['red']['autoTerminalCones'], match['match']['scores']['red']['autoGroundCones'],
                   match['match']['scores']['red']['autoLowCones'], match['match']['scores']['red']['autoMediumCones'],
                   match['match']['scores']['red']['autoHighCones'], match['match']['scores']['red']['autoNavigationPoints'],
                   match['match']['scores']['red']['autoPoints'], match['match']['scores']['red']['dcTerminalCones'],
                   match['match']['scores']['red']['dcGroundCones'], match['match']['scores']['red']['dcLowCones'],
                   match['match']['scores']['red']['dcMediumCones'], match['match']['scores']['red']['dcHighCones'],
                   match['match']['scores']['red']['dcPoints'], match['match']['scores']['red']['coneOwnedJunctions'],
                   match['match']['scores']['red']['beaconOwnedJunctions'],
                   match['match']['scores']['red']['endgameNavigationPoints'],
                   match['match']['scores']['red']['endgamePoints'], match['match']['scores']['red']['totalPointsNp'],
                   match['match']['scores']['blue']['totalPoints'],
                   match['match']['scores']['blue']['autoTerminalCones'], match['match']['scores']['blue']['autoGroundCones'],
                   match['match']['scores']['blue']['autoLowCones'], match['match']['scores']['blue']['autoMediumCones'],
                   match['match']['scores']['blue']['autoHighCones'], match['match']['scores']['blue']['autoNavigationPoints'],
                   match['match']['scores']['blue']['autoPoints'], match['match']['scores']['blue']['dcTerminalCones'],
                   match['match']['scores']['blue']['dcGroundCones'], match['match']['scores']['blue']['dcLowCones'],
                   match['match']['scores']['blue']['dcMediumCones'], match['match']['scores']['blue']['dcHighCones'],
                   match['match']['scores']['blue']['dcPoints'], match['match']['scores']['blue']['coneOwnedJunctions'],
                   match['match']['scores']['blue']['beaconOwnedJunctions'],
                   match['match']['scores']['blue']['endgameNavigationPoints'],
                   match['match']['scores']['blue']['endgamePoints'], match['match']['scores']['blue']['totalPointsNp'],
                   ))

    # End the database connection
    conn.commit()
    conn.close()
    print("Done!")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    entry()
