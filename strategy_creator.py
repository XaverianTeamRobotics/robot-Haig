# Allow the user to create a strategy
# The user will create a strategy by gathering another team's play-style
# The user will then create a strategy based on the play-style and the team's strengths and weaknesses
# The strategy will be saved to a PDF with the opposing two teams' play styles and the strategy, as well as a diagram of the field
# The user will then be able to print the PDF or mark it up on the computer

# The play style will be seperated into a list of multiple "checkboxes" (yes/no questions in the terminal)
# The user will then fill out the strengths and weaknesses of the team using the checkboxes
# Examples of checkboxes:
# - The team is good at circuits
# - The team plays on their side of the field
# - The team plays on the other side of the field
# - The robot is a turret-style bot
# - The robot is fast
# - The robot has a fast lift
# - etc.

# We will then use the checkboxes to determine the best pre-programmed strategy for the team
# The best strategy will be determined by a neural network algorithm
# The algorithm will be trained by a human, who will determine if the algorithm's strategy is good or not


def main():
    # Get the four teams play styles
    styleR1 = getPlayStyle("Red 1")
    styleR2 = getPlayStyle("Red 2")
    styleB1 = getPlayStyle("Blue 1")
    styleB2 = getPlayStyle("Blue 2")

    position = 0

    # Get which position the user is in
    while True:
        position = input("What position are you in? (Red 1, Red 2, Blue 1, Blue 2) ").lower()
        if position == "red 1":
            position = 1
            break
        elif position == "red 2":
            position = 2
            break
        elif position == "blue 1":
            position = 3
            break
        elif position == "blue 2":
            position = 4
            break

    # Run the neural network to determine the best strategy
    print("The best strategy is " + getStrategy(styleR1, styleR2, styleB1, styleB2, position))


def getPlayStyle(position: str):
    # Create a dictionary of the play style, where the key is the question and the value is the answer as a boolean
    playStyle = {}

    # Ask the user for the team's play style
    print(f"\nWhat is {position}'s play style?\n")
    print("Please answer the following questions with a yes or no.")

    # Ask the user if the team is good at circuits
    playStyle["Circuits"] = getYesNo("Are they good at circuits?")

    # Ask the user if the team plays on their side of the field
    playStyle["Side"] = getYesNo("Do they play on their side of the field?")

    # Ask the user if the team plays on the other side of the field
    playStyle["Other side"] = getYesNo("Do they play on the other side of the field?")

    # Ask the user if the robot is a turret-style bot
    playStyle["Turret"] = getYesNo("Is their robot a turret-style bot?")

    # Ask the user if the robot is fast
    playStyle["Speed"] = getYesNo("Is their robot fast?")

    # Ask the user if the robot has a fast lift
    playStyle["Lift"] = getYesNo("Does their robot have a fast lift?")

    # Ask the user if the robot likes to distribute cones
    playStyle["Distribute"] = getYesNo("Does their robot like to distribute cones?")

    return playStyle


def getYesNo(prompt: str):
    # Ask the user a yes/no question
    # Return True if the user answers yes, False if the user answers no
    # Keep asking the user until they answer yes or no
    while True:
        # Ask the user the question
        answer = input(prompt + " (y/n) ").lower()

        # Check if the user answered yes
        if answer == "y" or answer == "yes":
            return True

        # Check if the user answered no
        if answer == "n" or answer == "no":
            return False


def getStrategyList():
    return [
        'The Braden Strategy: A quick circuit, but is easily defended against',
        'The Aggressive Strategy: Deny the other team a circuit by aggressively maintaining control of the center at the cost of no circuits for your team',
        'The Stealth Circuit Strategy: A stealthy circuit that avoids the center of the field and takes more time to complete',
        'The Turret Counter Strategy: Defend against a turret-style bot by avoiding the center of the field and by placing a cone to block the turret',
        'The Turret Strategy: A turret-style bot that can quickly score a cone without moving, but can only do so on one junction',
        'The Spread Strategy: Spread out your team to cover more of the field and to make it harder for the other team to defend against you, while also getting more points for owning junctions',
    ]


def getStrategy(styleR1, styleR2, styleB1, styleB2, position):
    return evaluateNeuralNetwork(styleB1, styleB2, styleR1, styleR2, position)


def getPlayStyleQuestions():
    return [
        'Circuits',
        'Side',
        'Other side',
        'Turret',
        'Speed',
        'Lift',
        'Distribute',
    ]


def loadNeuralNetwork():
    # Load the neural network from a JSON file
    import json
    with open('neural_network.json', 'r') as file:
        neuralNetwork = json.load(file)
    return neuralNetwork


def evaluateNeuralNetwork(styleB1, styleB2, styleR1, styleR2, position):
    # Evaluate the neural network
    # Get the neural network
    neuralNetwork = loadNeuralNetwork()

    # Get the list of play style questions
    playStyleQuestions = getPlayStyleQuestions()

    # The four teams' play styles is given as a parameter
    # The position is given as a parameter
    # However, we must manipulate the style's so that our team is one of the first two slots
    # This is because the neural network is trained to have the first two slots be the team's play style
    # The last two slots are the opposing team's play style

    # If the user is in the first slot, then we don't need to do anything
    if position == 1 or position == 2:
        pass

    # If the user is in the second slot, then we need to swap the first two slots
    elif position == 3 or position == 4:
        _styleB1, _styleB2 = styleB1, styleB2
        styleB1, styleB2 = styleR1, styleR2
        styleR1, styleR2 = _styleB1, _styleB2

    # We are done manipulating the play styles, now we can run the neural network
    # The neural network will return a list of numbers, where each number is the probability of that strategy being the best strategy

    # Get the list of strategies
    strategies = getStrategyList()

    # Set the input layer
    for i in range(4):
        # Set the input layer for each team
        for question in playStyleQuestions:
            # Set the input neuron for each play style question
            if i == 0:
                neuralNetwork["input"][i][question] = styleB1[question]
            elif i == 1:
                neuralNetwork["input"][i][question] = styleB2[question]
            elif i == 2:
                neuralNetwork["input"][i][question] = styleR1[question]
            elif i == 3:
                neuralNetwork["input"][i][question] = styleR2[question]

    # Set the output layer
    for strategy in strategies:
        # Set the output neuron for each strategy
        neuralNetwork["output"][strategy] = 0

    # Evaluate the hidden layers
    for i in range(5):
        # Evaluate each hidden layer
        for j in range(len(neuralNetwork["input"])):
            # Evaluate each input neuron
            for question in playStyleQuestions:
                # Evaluate each play style question
                neuralNetwork["input"][j][question] = neuralNetwork["input"][j][question] * neuralNetwork["weights"]["hidden"][i][j][question]

    # Evaluate the output layer
    for strategy in strategies:
        # Evaluate each output neuron
        for i in range(4):
            # Evaluate each input neuron
            for question in playStyleQuestions:
                # Evaluate each play style question
                neuralNetwork["output"][strategy] += neuralNetwork["input"][i][question] * neuralNetwork["weights"]["input"][i][question]

    # Get the best strategy
    bestStrategy = ""
    bestStrategyValue = 0
    for strategy in strategies:
        # Evaluate each strategy
        if neuralNetwork["output"][strategy] > bestStrategyValue:
            # If the strategy is better than the current best strategy
            bestStrategy = strategy
            bestStrategyValue = neuralNetwork["output"][strategy]

    # Return the best strategy
    return bestStrategy


if __name__ == "__main__":
    main()
