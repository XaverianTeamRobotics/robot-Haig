import sqlite3
import os
import gql
from gql.transport.requests import RequestsHTTPTransport


def entry():
    print("Welcome to the Robot-Haig scouting tool, named in honor of the person this is replacing")
    print("This tool will allow you to automatically gather data from the Orange Alliance API and the FTCScout.org API")
    print("It's goal is to analyze a team's performance and predict their performance in future matches")
    print("By adding a team to the database, you will be able to analyze their performance without constant Internet access\n")
    # Create a basic text interface for a person to input team data, event data, and scouting data
    # Store the data in a persistent database
    # Team history can then be gathered from the Orange Alliance API and the FTCScout.org API
    # The data can be combined with the scouting data to create a ranking system,
    #               ideal alliance selection, and potential match outcomes

    # The data can be exported to a SQL database for further analysis
    # With the explaining done, let's get started

    # We need to create a database to store the data in
    # We will use SQLite for this
    # If the database does not exist, we will create it
    if not os.path.exists("scouting.db"):
        createDB()

    # Now, we need to allow the user to select what they want to do
    # We will create a basic text interface

    # First, we need to create a loop that will continue until the user exits the program
    while True:
        # First, we need show the user the options
        print("Please select an option:")
        print("  1. Add a team to the database")
        print("  2. Analyze a team's matches")
        print("  3. Exit the program")

        # Now, we need to get the user's input
        user_input = input("Please enter the number of the option you would like to select: ")

        # Now, we need to check if the user entered a valid option
        if user_input == "1":
            # The user wants to add a team to the database
            # We need to get the team number
            team_number = input("Please enter the team number: ")

            # Now, we need to add the team to the database
            add_all_team_data(team_number)

        elif user_input == "2":
            # The user wants to analyze a team's matches
            # We need to get the team number
            team_number = input("Please enter the team number: ")

            # Now, we need to analyze the team's matches
            analyze_matches(team_number)

        elif user_input == "3":
            # The user wants to exit the program
            # We will break out of the loop
            break


def add_all_team_data(team_number):
    add_team(team_number)
    add_events(team_number)
    add_matches(team_number)
    eliminate_duplicate_teams_events_and_matches()


def analyze_matches(team_number):
    # A brief explanation of the algorithm:
    #   1. Get the team's matches
    #   2. Find their scores (before penalties, totalPointsNp) (the opponent's scores are not necessary)
    #   3. Find their most common strategy (circuits, autonomous, junction distribution, etc.)
    #   4. Report the results

    # First, we need to open the database
    conn = sqlite3.connect("scouting.db")
    c = conn.cursor()

    # Now, we need to get the team's matches
    # We will get this from the match table, finding all matches where the team is either red_number_1 or red_number_2,
    # then a second time where the team is either blue_number_1 or blue_number_2
    c.execute("SELECT * FROM matches WHERE red_number_1 = ? OR red_number_2 = ?", (team_number, team_number))
    red_matches = c.fetchall()
    c.execute("SELECT * FROM matches WHERE blue_number_1 = ? OR blue_number_2 = ?", (team_number, team_number))
    blue_matches = c.fetchall()

    # Now, we need to find the team's scores
    # We will do this by finding the average of the team's scores in each match

    # First, we need to find the total number of matches
    total_matches = len(red_matches) + len(blue_matches)

    # Next, we need to find the total number of points
    total_points = 0
    for match in red_matches:
        total_points += match[-5]
    for match in blue_matches:
        total_points += match[6]

    try:
        # Now, we can find the average
        average_points = total_points / total_matches

        # Now, we need to find the average autonomous score
        # We will do this by finding the average of the team's autonomous scores in each match

        total_auto_points = 0
        for match in red_matches:
            total_auto_points += match[-4]
        for match in blue_matches:
            total_auto_points += match[7]
        average_auto_points = total_auto_points / total_matches

        # Find the average teleop score
        total_teleop_points = 0
        for match in red_matches:
            total_teleop_points += match[-3]
        for match in blue_matches:
            total_teleop_points += match[8]
        average_teleop_points = total_teleop_points / total_matches

        # Find the average endgame score
        total_endgame_points = 0
        for match in red_matches:
            total_endgame_points += match[-2]
        for match in blue_matches:
            total_endgame_points += match[9]
        average_endgame_points = total_endgame_points / total_matches
    except ZeroDivisionError:
        print("The team has not played any matches")
        input("Press enter to continue...")
        return

    print("Average points: " + str(average_points))
    print("Average autonomous points: " + str(average_auto_points))
    print("Average teleop points: " + str(average_teleop_points))
    print("Average endgame points: " + str(average_endgame_points))

    input("Press enter to continue...")


def createDB():
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
    c.execute('''CREATE TABLE matches
                    (event_code text, match_number text, red_number_1 integer, red_number_2 integer, 
                    blue_number_1 integer, blue_number_2 integer,
                    totalPoints_blue integer, autoPoints_blue integer, dcPoints_blue integer, endgamePoints_blue integer,
                    totalPointsNp_blue integer, totalPoints_red integer, autoPoints_red integer,
                    dcPoints_red integer, endgamePoints_red integer, totalPointsNp_red integer)''')

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

    # End the database connection
    conn.commit()
    conn.close()

    add_team(team_number)

    add_events(team_number)

    add_matches(team_number)


def add_team(team_number):
    conn = sqlite3.connect("scouting.db")
    c = conn.cursor()

    client = gql.Client(
        transport=RequestsHTTPTransport(
            url='https://api.ftcscout.org/graphql',
            use_json=True,
            headers={
                "Content-type": "application/json"
            },
            verify=True,
            retries=3,
        ),
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
    c.execute("INSERT INTO teams VALUES (?, ?, ?)", (team_number, team_name, team_location))

    # End the database connection
    conn.commit()
    conn.close()


def add_events(team_number):
    conn = sqlite3.connect("scouting.db")
    c = conn.cursor()

    client = gql.Client(
        transport=RequestsHTTPTransport(
            url='https://api.ftcscout.org/graphql',
            use_json=True,
            headers={
                "Content-type": "application/json"
            },
            verify=True,
            retries=3,
        ),
        fetch_schema_from_transport=True,
    )

    # Now, list all events that the team has attended
    # We will get the data from the same API as before
    # We will query the API for the team's events
    query = gql.gql('''
        query {
            teamByNumber(number: ''' + team_number + ''') {
                events(season: 2023) {
                    event{
                        name
                        location { venue }
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

    # If there are no events, we will return
    if len(events) == 0:
        conn.commit()
        conn.close()
        return

    # Now we can add them to the database
    for event in events:
        c.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (event['event']['name'], event['event']['venue'],
                                                             event['event']['start'], event['event']['code']))

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

    conn.commit()
    conn.close()


def add_matches(team_number):
    conn = sqlite3.connect("scouting.db")
    c = conn.cursor()

    client = gql.Client(
        transport=RequestsHTTPTransport(
            url='https://api.ftcscout.org/graphql',
            use_json=True,
            headers={
                "Content-type": "application/json"
            },
            verify=True,
            retries=3,
        ),
        fetch_schema_from_transport=True,
    )

    # Now, we need to get all of the matches for the user's team
    # This includes the match number, event code, the 4 team numbers, the score, and the cone layout
    # We will get the data from the same API as before
    # We will query the API for the matches
    query = gql.gql('''
        query {
            teamByNumber(number: ''' + team_number + ''') {
                matches(season: 2023) {
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
                            ... on MatchScores2023 {
                              red {
                                totalPoints
                                autoPoints
                                dcPoints
                                egPoints
                                totalPointsNp
                              }
                              blue {
                                totalPoints
                                autoPoints
                                dcPoints
                                egPoints
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
            (
                    match['match']['event']['code'], match['match']['matchNum'],
                    match['match']['teams'][0]['teamNumber'],
                    match['match']['teams'][1]['teamNumber'],
                    match['match']['teams'][2]['teamNumber'],
                    match['match']['teams'][3]['teamNumber'],
                    match['match']['scores']['blue']['totalPoints'],
                    match['match']['scores']['blue']['autoPoints'],
                    match['match']['scores']['blue']['dcPoints'],
                    match['match']['scores']['blue']['egPoints'],
                    match['match']['scores']['blue']['totalPointsNp'],
                    match['match']['scores']['red']['totalPoints'],
                    match['match']['scores']['red']['autoPoints'],
                    match['match']['scores']['red']['dcPoints'],
                    match['match']['scores']['red']['egPoints'],
                    match['match']['scores']['red']['totalPointsNp'],
                  ))

    # Now, we can commit the changes
    conn.commit()
    conn.close()


def eliminate_duplicate_teams_events_and_matches():
    # This function will eliminate duplicate teams, events, and matches
    # This will be done with specially crafted SQL queries
    # Teams are easy, because the team number is the primary key
    # Events are easy, because the event code is the primary key
    # Matches are a little more complicated, because the primary key is a combination of the event code, match number, and team numbers
    # This is because the same match can be played by multiple teams, and the same set of teams can play multiple matches

    # First, we will eliminate duplicate teams
    # This is easy, because the team number is the primary key
    conn = sqlite3.connect('scouting.db')
    c = conn.cursor()
    c.execute('''DELETE FROM teams WHERE rowid NOT IN (
        SELECT MIN(rowid) FROM teams GROUP BY team_number
    )''')
    conn.commit()
    conn.close()

    # Next, we will eliminate duplicate events
    # This is easy, because the event code is the primary key
    conn = sqlite3.connect('scouting.db')
    c = conn.cursor()
    c.execute('''DELETE FROM events WHERE rowid NOT IN (
        SELECT MIN(rowid) FROM events GROUP BY event_code
    )''')
    conn.commit()
    conn.close()

    # Next, we will eliminate duplicate matches
    # This is a little more complicated, because the primary key is a combination of the event code, match number, and team numbers
    # This is because the same match can be played by multiple teams, and the same set of teams can play multiple matches
    conn = sqlite3.connect('scouting.db')
    c = conn.cursor()
    c.execute('''DELETE FROM matches WHERE rowid NOT IN (
        SELECT MIN(rowid) FROM matches GROUP BY event_code, match_number, red_number_1, red_number_2, blue_number_1, blue_number_2
    )''')
    conn.commit()
    conn.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    entry()
