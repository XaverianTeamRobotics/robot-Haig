# Create and train a neural network to go along with the strategy_creator.py script
# The neural network will take in the play styles of the four teams and the position of the user
# The neural network will output the best strategy for the user to use
# The neural network will be trained by a human, who will determine if the algorithm's strategy is good or not
#
# Path: train_strategy_ai.py
# Compare this snippet from strategy_creator.py:
# # - The team is good at circuits
# # - The team plays on their side of the field
# # - The team plays on the other side of the field
# # - The robot is a turret-style bot
# # - The robot is fast
# # - The robot has a fast lift
# # - etc.

# We will then use the checkboxes to determine the best pre-programmed strategy for the team
# The best strategy will be determined by a neural network algorithm
# The algorithm will be trained by a human, who will determine if the algorithm's strategy is good or not

# We will import the numpy library to help us with the math
import numpy as np

# We will also import some functions from the strategy_creator.py script
from strategy_creator import getPlayStyle, getYesNo, getStrategy, getPlayStyleQuestions, getStrategyList, loadNeuralNetwork


def train():
    # Get the four teams play styles
    styleR1 = getPlayStyle("Red 1")
    styleR2 = getPlayStyle("Red 2")
    styleB1 = getPlayStyle("Blue 1")
    styleB2 = getPlayStyle("Blue 2")

    # Get which position the user is in
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
    strategy = getStrategy(styleR1, styleR2, styleB1, styleB2, position)

    print(f"The best strategy is {strategy}.")

    # Ask the user if the strategy is good or not
    good = getYesNo("Is this strategy good?")

    # Adjust the weights accordingly
    adjustWeights(styleR1, styleR2, styleB1, styleB2, position, strategy, good)


def adjustWeights(styleR1: dict, styleR2: dict, styleB1: dict, styleB2: dict, position: int, strategy: str, good: bool):
    # Get the neural network
    neuralNet = loadNeuralNetwork()

    # Get the list of play style questions
    playStyleQuestions = getPlayStyleQuestions()

    # Get the list of strategies
    strategies = getStrategyList()

    # Get the index of the strategy
    strategyIndex = strategies.index(strategy)

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

    # Do the adjustments
    # We work backwards from the last hidden layer to the input layer
    # The output layer is always set to 0 before execution, so we don't need to worry about it
    # We will keep doing this until we get our desired result
    # We will then save the neural network

    while True:
        # Adjust the weights for the input layer
        for i in range(4):
            # Adjust the weights for each team
            for question in playStyleQuestions:
                # Adjust the weight for each play style question
                if good:
                    # If the strategy is good, then we want to increase the weight
                    neuralNet["weights"]["input"][i][question] += neuralNet["input"][i][question] * 0.1
                else:
                    # If the strategy is bad, then we want to decrease the weight
                    neuralNet["weights"]["input"][i][question] -= neuralNet["input"][i][question] * 0.1

        # Adjust the weights for the hidden layers
        for i in range(5):
            # Adjust the weights for each hidden layer
            for j in range(len(neuralNet["input"])):
                # Adjust the weights for each neuron
                for question in playStyleQuestions:
                    # Adjust the weight for each play style question
                    if good:
                        # If the strategy is good, then we want to increase the weight
                        neuralNet["weights"]["hidden"][i][j][question] += neuralNet["input"][j][question] * 0.1
                    else:
                        # If the strategy is bad, then we want to decrease the weight
                        neuralNet["weights"]["hidden"][i][j][question] -= neuralNet["input"][j][question] * 0.1

        # Check if the new neural network is good
        newStrategy = getStrategy(styleR1, styleR2, styleB1, styleB2, position)
        if newStrategy == strategy and good:
            # If the new strategy is the same as the old strategy and the old strategy was good, then we are done
            break
        elif newStrategy == strategy and not good:
            # If the new strategy is the same as the old strategy and the old strategy was bad, then we need to try again
            continue

    # Save the neural network
    saveNeuralNetwork(neuralNet)


def createUntrainedNeuralNetwork():
    # Create a neural network with random weights
    # The neural network will have 1 input per play style question per team
    # The neural network will have 1 output per strategy
    # The neural network will have as 5 hidden layers
    # The neural network will have as many neurons per hidden layer as needed

    # Get the list of play style questions
    playStyleQuestions = getPlayStyleQuestions()

    # Get the list of strategies
    strategies = getStrategyList()

    # Create a dictionary of the neural network
    neuralNet = {"input": [{}, {}, {}, {}], "output": {}, "weights": {"input": [{}, {}, {}, {}], "hidden": [[{}, {}, {}, {}], [{}, {}, {}, {}], [{}, {}, {}, {}], [{}, {}, {}, {}], [{}, {}, {}, {}]]}}

    # Create the input layer
    for i in range(4):
        # Create the input layer for each team
        for question in playStyleQuestions:
            # Create a neuron for each play style question
            neuralNet["input"][i][question] = 0

    # Create the weights for the hidden layers
    for i in range(5):
        # Create the weights for each hidden layer
        for j in range(len(neuralNet["input"])):
            # Create the weights for each input neuron
            for question in playStyleQuestions:
                # Create a weight for each play style question
                neuralNet["weights"]["hidden"][i][j][question] = np.random.rand()

    # Create the output layer
    strategy: str
    for strategy in strategies:
        # Create a neuron for each strategy
        neuralNet["output"][strategy] = 0

    # Create the weights for the input layer
    for i in range(4):
        # Create the weights for each team
        for question in playStyleQuestions:
            # Create a weight for each play style question
            neuralNet["weights"]["input"][i][question] = np.random.rand()

    # Return the neural network
    return neuralNet


def saveNeuralNetwork(neuralNet):
    # Save the neural network to a file
    # A pandas dataframe cannot be used because of the nested dictionary
    # We will use JSON instead

    # Import the json library
    import json

    # Save the neural network to a file
    with open("neural_network.json", "w") as file:
        json.dump(neuralNet, file)

    # Print a message to the user
    print("The neural network has been saved to the neural_network.json file.")


if __name__ == "__main__":
    # Ask the user if they want to train the neural network or create a new one
    trainOrNew = getYesNo("Do you want to train the neural network or create a new one?")

    # If the user wants to train the neural network
    if trainOrNew:
        # Train the neural network
        train()

    # If the user wants to create a new neural network
    else:
        # Create a new neural network
        neuralNetwork = createUntrainedNeuralNetwork()

        # Save the neural network
        saveNeuralNetwork(neuralNetwork)
