import random
import copy
import math

"""
Unlayered Spiking Neural Network as class in python module
Project: Proposing an 'unlayered' neural network model for machine learning
By: Joseph Parayil, 10th grade, Crooms AOIT
"""

class nn:
    """ INSTANCE MEMBERS """
    """
        cells       -list of values representing cell voltages
        synapses    -list of synapse configurations
        inputCount  -number of input neurons
        hiddenCount -number of interneurons
        outputCount -number of output neurons
  
    """

    """ STATIC MEMBERS """
    WEIGHT_LIMIT = 2
    WEIGHT_MUTATE_FACTOR = 0.4
    DEFAULT_SYNAPSES_PER_CELL = 2

    """ INSTANCE METHODS """

    # To randomly initialize network based on initial number of each type of neuron
    def __init__(self, inputCount, hiddenCount, outputCount, synapseCount=-1):
        totalCount = inputCount + hiddenCount + outputCount

        self.cells = [0] * totalCount
        self.synapses = []
        self.inputCount = inputCount
        self.hiddenCount = hiddenCount
        self.outputCount = outputCount

        if synapseCount == -1:
            synapseCount = totalCount * nn.DEFAULT_SYNAPSES_PER_CELL

        for i in range(synapseCount):
            self.synapses.append(self.getRandomSynapse())

    # Applies network propagation functionality using a list of inputs
    # Will return list of boolean values representing output cell firing states
    def run(self, input):
        #Applying input values to input neuron voltages
        for id in range(len(input)):
            self.cells[id] += input[id]

        valueUpdates = [0] * len(self.cells)

        #Applying functionality for spikes traveling along synapses
        for synapse in self.synapses:
            if self.cells[synapse['presynapticID']] >= 1:
                valueUpdates[synapse['postsynapticID']] += synapse['weight']
        #Restricting input value from value 0-1
        for id in range(self.inputCount):
            if self.cells[id] >= 1 or self.cells[id] < 0:
                self.cells[id] = 0

        #Applying updates to rest of neurons (hidden and output)
        for id in range(self.inputCount, len(self.cells)):
            if self.cells[id] >= 1 or self.cells[id] < 0:
                self.cells[id] = 0
            self.cells[id] += valueUpdates[id]

        #Getting outputs
        outputs = [False] * self.outputCount

        for id in range(self.inputCount + self.hiddenCount, len(self.cells)):
            if self.cells[id] >= 1:
                outputs[id - (self.inputCount + self.hiddenCount)] = True

        #outputs - list of the firing states of output cells
        return outputs

    # Returns a new network object with the same member configurations
    def copy(self):
        return copy.deepcopy(self)

    # Returns a synapse with random synaptic configurations
    def getRandomSynapse(self):
        mySynapse =  {
            'presynapticID': random.randint(0, len(self.cells) - 1),
            'postsynapticID': random.randint(self.inputCount, len(self.cells) - 1),
            'weight': nn.randWeight()
        }
        return mySynapse


    # Adds a new hidden cell to the network
    # Adds synapses connected to the cell
    def insertCell(self, synapsesPerCell= -1):
        if synapsesPerCell == -1:
            synapsesPerCell = nn.DEFAULT_SYNAPSES_PER_CELL

        self.cells.append(0)

        for i in range(synapsesPerCell):
            newSynapse = self.getRandomSynapse()

            if random.randint(1, 2) == 1:
                #Presynaptic cell is the added cell
                newSynapse['presynapticID'] = self.inputCount + self.hiddenCount
            else:
                #Postsynaptic cell is the added cell
                newSynapse['postsynapticID'] = self.inputCount + self.hiddenCount

            self.synapses.append(newSynapse)

        self.hiddenCount += 1


    # Removes cell at cellID from the network
    # Removes all synapses connected to this cell
    # Adjust synaptic IDs for the deleted cell
    def removeCell(self, cellID):
        self.cells.pop()

        #Decrementing corresponding cell group
        if cellID < self.inputCount:
            self.inputCount -= 1
        elif cellID < self.inputCount + self.hiddenCount:
            self.hiddenCount -= 1
        else:
            self.outputCount -= 1

        #Adjusting IDs for deleted cels
        #Delete synapses connected to deleted cell
        i = 0
        while i < len(self.synapses):
            synapse = self.synapses[i]
            if synapse['presynapticID'] == cellID:
                del self.synapses[i]
                continue
            elif synapse['presynapticID'] > cellID:
                synapse['presynapticID'] -= 1

            if synapse['postsynapticID'] == cellID:
                del self.synapses[i]
                continue
            elif synapse['postsynapticID'] > cellID:
                synapse['postsynapticID'] -= 1

            i += 1

    # Mutates synaptic configurations and number of interneurons
    def mutate(self, mutateRate, synapsesPerCell=-1):
        if synapsesPerCell == -1:
            synapsesPerCell = nn.DEFAULT_SYNAPSES_PER_CELL
        copyNetwork = self.copy()

        #Adding/removing hidden cells
        for i in range(math.floor(len(copyNetwork.cells) * mutateRate)):
            if random.randint(1, 2) == 1:
                #Add hidden cell
                copyNetwork.insertCell(synapsesPerCell)
            else:
                #Remove hidden cell
                if copyNetwork.hiddenCount > 0:
                    copyNetwork.removeCell(
                        random.randint(copyNetwork.inputCount, copyNetwork.inputCount + copyNetwork.hiddenCount - 1))

        #Adding, removing, and altering synapses
        for i in range(math.floor(len(copyNetwork.synapses) * mutateRate)):
            if random.randint(1, 3) == 1:
                #Add/remove synapse
                if random.randint(1, 2) == 1:
                    #Add synapse
                    copyNetwork.synapses.append(copyNetwork.getRandomSynapse())
                else:
                    #Remove synape
                    if len(copyNetwork.synapses) > 0:
                        del copyNetwork.synapses[random.randint(0, len(copyNetwork.synapses) - 1)]
            else:
                #Adjust synaptic weight
                copyNetwork.synapses[random.randint(0, len(copyNetwork.synapses) - 1)][
                    'weight'] += nn.adjustWeight()

        return copyNetwork




    # Returns a dictionary representing the json format of the network for exporting.
    def toJSON(self):
        jsonNetwork = {}

        jsonNetwork['Synapses'] = copy.deepcopy(self.synapses)
        jsonNetwork['InputCount'] = self.inputCount
        jsonNetwork['HiddenCount'] = self.hiddenCount
        jsonNetwork['OutputCount'] = self.outputCount

        return jsonNetwork

    """ STATIC METHODS """

    # Returns network object based on the dictionary in Json format
    @staticmethod
    def fromJSON(jsonNetwork):
        newNetwork = nn(jsonNetwork['InputCount'], jsonNetwork['HiddenCount'], jsonNetwork['OutputCount'], 0)
        newNetwork.synapses = copy.deepcopy(jsonNetwork['Synapses'])

        return newNetwork

    # Returns a random floating point number to initialize weight
    @staticmethod
    def randWeight():
        return random.uniform(-nn.WEIGHT_LIMIT, nn.WEIGHT_LIMIT)

    # Returns randomly floating point number to represent change to weight
    @staticmethod
    def adjustWeight():
        return random.uniform(-nn.WEIGHT_MUTATE_FACTOR, nn.WEIGHT_MUTATE_FACTOR)


