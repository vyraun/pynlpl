#---------------------------------------------------------------
# PyNLPl - Search Algorithms
#   by Maarten van Gompel, ILK, Universiteit van Tilburg
#   http://ilk.uvt.nl/~mvgompel
#   proycon AT anaproy DOT nl
#
#   Licensed under GPLv3
#
#----------------------------------------------------------------

"""This module contains various search algorithms."""

from sys import stderr
from pynlpl.datatypes import FIFOQueue, PriorityQueue
from collections import deque

class AbstractSearchState(object):
    def __init__(self,  parent = None, cost = 0):
        self.parent = parent        
        self.cost = cost

    def test(self, goalstates = None):
        """Checks whether this state is a valid goal state, returns a boolean. If no goalstate is defined, then all states will test positively, this is what you usually want for optimisation problems."""
        if goalstates:
            return (self in goalstates)
        else:
            return True
            #raise Exception("Classes derived from AbstractSearchState must define a test() method!")

    def score(self):
        """Should return a heuristic value. This needs to be set if you plan to used an informed search algorithm."""
        raise Exception("Classes derived from AbstractSearchState must define a score() method if used in informed search algorithms!")

    def expand(self):
        """Generates successor states, implement your custom operators in the derived method."""
        raise Exception("Classes derived from AbstractSearchState must define an expand() method!")

    def __eq__(self):
        """Implement an equality test in the derived method, based only on the state's content (not its path etc!)"""
        raise Exception("Classes derived from AbstractSearchState must define an __eq__() method!")

    
    def __hash__(self):
        """Return a unique hash for this state, based on its ID"""
        raise Exception("Classes derived from AbstractSearchState must define a __hash__() method if the search space is a graph and visited nodes to be are stored in memory!")        


    def depth(self):
        if not self.parent:
            return 0
        else:
            return self.parent.depth() + 1            

    #def __len__(self):
    #    return len(self.path())

    def path(self):
        if not self.parent:
            return [self]
        else: 
            return self.parent.path() + [self]

    def pathcost(self):
        if not self.parent:
            return self.cost
        else: 
            return self.parent.pathcost() + self.cost


        

    #def __cmp__(self, other):
    #    if self.score < other.score:
    #        return -1
    #    elif self.score > other.score:
    #        return 1
    #    else:
    #        return 0

class AbstractSearch(object): #not a real search, just a base class for DFS and BFS
    def __init__(self, **kwargs):
        """For graph-searches graph=True is required (default), otherwise the search may loop forever. For tree-searches, set tree=True for better performance"""
        self.usememory = True
        self.poll = lambda x: x.pop
        self.maxdepth = False #unlimited
        self.minimize = False #minimize rather than maximize the score function? default: no
        self.keeptraversal = False
        self.goalstates = None
        self.traversed = 0 #Count of number of nodes visited
        self.solutions = 0 #Counts the number of solutions
        self.debug = 0
        for key, value in kwargs.items():
            if key == 'graph':
                self.usememory = value #search space is a graph? memory required to keep visited states
            elif key == 'tree':
                self.usememory = not value;  #search space is a tree? memory not required
            elif key == 'poll':
                self.poll = value #function
            elif key == 'maxdepth':
                self.maxdepth = value
            elif key == 'minimize':
                self.minimize = value
            elif key == 'maximize':
                self.minimize = not value
            elif key == 'keeptraversal': #remember entire traversal?
                self.keeptraversal = value
            elif key == 'goal' or key == 'goals':
                if isinstance(value, list) or isinstance(value, tuple):
                    self.goalstates = value
                else:
                    self.goalstates = [value]
            elif key == 'debug':
                self.debug = value
        self.visited = {}
        self.traversal = []
        self.incomplete = False
        self.traversed = 0

    def reset(self):
        self.visited = {}
        self.traversal = []
        self.incomplete = False
        self.traversed = 0 #Count of all visited nodes
        self.solutions = 0 #Counts the number of solutions found     

    def traversal(self):
        """Returns all visited states (only when keeptraversal=True), note that this is not equal to the path, but contains all states that were checked!"""
        if self.keeptraversal:
            return self.traversal
        else:
            raise Exception("No traversal available, algorithm not started with keeptraversal=True!")
    
    def traversalsize(self):
        """Returns the number of nodes visited  (also when keeptravel=False). Note that this is not equal to the path, but contains all states that were checked!"""
        return self.traversed
        

    def visited(self, state):
        if self.usememory:
            return (hash(state) in self.visited)
        else:
            raise Exception("No memory kept, algorithm not started with graph=True!")
        
    def __iter__(self):
        """Generator yielding *all* valid goalstates it can find,"""
        n = 0
        while len(self.fringe) > 0:
            n += 1
            if self.debug: print >>stderr,"\t[pynlpl debug] *************** ITERATION #" + str(n) + " ****************"
            if self.debug: print >>stderr,"\t[pynlpl debug] FRINGE: ", self.fringe
            state = self.poll(self.fringe)()
            if self.debug:
                try:
                    print >>stderr,"\t[pynlpl debug] CURRENT STATE (depth " + str(state.depth()) + "): " + str(state),
                except AttributeError:
                    print >>stderr,"\t[pynlpl debug] CURRENT STATE: " + str(state),
                try:
                    print >>stderr,state.score()
                except:
                    pass
 

            #If node not visited before (or no memory kept):
            if not self.usememory or (self.usememory and not hash(state) in self.visited):
                
                #Evaluate the current state
                self.traversed += 1
                if state.test(self.goalstates):
                    if self.debug: print >>stderr,"\t[pynlpl debug] Valid goalstate, yielding"
                    yield state
                elif self.debug:
                    print >>stderr,"\t[pynlpl debug] (no goalstate, not yielding)"
                
                #Expand the specified state and add to the fringe

                
                #if self.debug: print >>stderr,"\t[pynlpl debug] EXPANDING:"
                statecount = 0
                for i, s in enumerate(state.expand()):
                    statecount += 1
                    if self.debug >= 2:
                        print >>stderr,"\t[pynlpl debug] (Iteration #" + str(n) +") Expanded state #" + str(i+1) + ", adding to fringe: " + str(s),
                        try:
                            print >>stderr,s.score()
                        except:
                            print >>stderr,"ERROR SCORING!"
                            pass
                    if not self.maxdepth or s.depth() <= self.maxdepth:
                        self.fringe.append(s)
                    else:
                        if self.debug: print >>stderr,"\t[pynlpl debug] (Iteration #" + str(n) +") Not adding to fringe, maxdepth exceeded"
                        self.incomplete = True
                if self.debug:
                    print >>stderr,"\t[pynlpl debug] Expanded " + str(statecount) + " states, offered to fringe"
                if self.keeptraversal: self.keeptraversal.append(state)
                if self.usememory: self.visited[hash(state)] = True
                self.prune(state) #calls prune method
            else:
                if self.debug:
                    print >>stderr,"\t[pynlpl debug] State already visited before, not expanding again..."
        if self.debug:
            print >>stderr,"\t[pynlpl debug] Search complete: " + str(self.solutions) + " solution(s), " + str(self.traversed) + " states traversed in " + str(n) + " rounds"
    
    def searchfirst(self):
        """Returns the very first result (regardless of it being the best or not!)"""
        for solution in self:
            return solution

    def searchall(self):
        """Returns a list of all solutions"""
        return list(iter(self))

    def searchbest(self):
        """Returns the single best result (if multiple have the same score, the first match is returned)"""
        finalsolution = None
        bestscore = None
        for solution in self:
            if bestscore == None:
                bestscore = solution.score()
                finalsolution = solution
            elif self.minimize:
                score = solution.score()
                if score < bestscore:
                    bestscore = score
                    finalsolution = solution
            elif not self.minimize:
                score = solution.score()
                if score > bestscore:
                    bestscore = score
                    finalsolution = solution                
        return finalsolution

    def searchtop(self,n=10):
        """Return the top n best resulta (or possibly less if not enough is found)"""            
        solutions = PriorityQueue([], lambda x: x.score, self.minimize, length=n, blockworse=False, blockequal=False,duplicates=False)
        for solution in self:
            solutions.append(solution)
        return solutions

    def searchlast(self,n=10):
        """Return the last n results (or possibly less if not found). Note that the last results are not necessarily the best ones! Depending on the search type."""            
        solutions = deque([], n)
        for solution in self:
            solutions.append(solution)
        return solutions

    def prune(self, state):
        """Pruning method is called AFTER expansion of each node"""
        #pruning nothing by default
        pass

class DepthFirstSearch(AbstractSearch):

    def __init__(self, state, **kwargs):
        assert isinstance(state, AbstractSearchState)
        self.fringe = [ state ]
        super(DepthFirstSearch,self).__init__(**kwargs)         



class BreadthFirstSearch(AbstractSearch):


    def __init__(self, state, **kwargs):
        assert isinstance(state, AbstractSearchState)
        self.fringe = FIFOQueue([state])
        super(BreadthFirstSearch,self).__init__(**kwargs)         


class IterativeDeepening(AbstractSearch):

    def __init__(self, state, **kwargs):
        assert isinstance(state, AbstractSearchState)
        self.state = state
        self.kwargs = kwargs
        self.traversed = 0

    def __iter__(self):
        self.traversed = 0
        d = 0
        while not 'maxdepth' in self.kwargs or d <= self.kwargs['maxdepth']:
            dfs = DepthFirstSearch(self.state, **self.kwargs)
            self.traversed += dfs.traversalsize()
            for match in dfs:
                yield match
            if dfs.incomplete:
                d +=1 
            else:
                break

    def traversal(self):
        #TODO: add
        raise Exception("not implemented yet")

    def traversalsize(self):
        return self.traversed


class BestFirstSearch(AbstractSearch):

    def __init__(self, state, **kwargs):
        super(BestFirstSearch,self).__init__(**kwargs)
        assert isinstance(state, AbstractSearchState)
        self.fringe = PriorityQueue([state], lambda x: x.score, self.minimize, length=0, blockworse=False, blockequal=False,duplicates=False)

class BeamSearch(AbstractSearch):
    """Local beam search algorithm"""

    def __init__(self, states, beamsize, **kwargs):
        if isinstance(states, AbstractSearchState):
            states = [states]
        else:
            assert all( ( isinstance(x, AbstractSearchState) for x in states) )
        self.beamsize = beamsize      
        if 'eager' in kwargs:
            self.eager = kwargs['eager']
        else:
            self.eager = False
        super(BeamSearch,self).__init__(**kwargs)
        self.incomplete = True
        self.duplicates = kwargs['duplicates'] if 'duplicates' in kwargs else False
        self.fringe = PriorityQueue(states, lambda x: x.score, self.minimize, length=0, blockworse=False, blockequal=False,duplicates= self.duplicates)

    def __iter__(self):
        """Generator yielding *all* valid goalstates it can find"""
        i = 0
        while len(self.fringe) > 0:
            i +=1 
            if self.debug: print >>stderr,"\t[pynlpl debug] *************** STARTING ROUND #" + str(i) + " ****************"
            
            b = 0
            #Create a new empty fixed-length priority queue (this implies there will be pruning if more items are offered than it can hold!)
            successors = PriorityQueue([], lambda x: x.score, self.minimize, length=self.beamsize, blockworse=False, blockequal=False,duplicates= self.duplicates)
            
            while len(self.fringe) > 0:
                b += 1
                if self.debug: print >>stderr,"\t[pynlpl debug] *************** ROUND #" + str(i) + " BEAM# " + str(b) + " ****************"
                #if self.debug: print >>stderr,"\t[pynlpl debug] FRINGE: ", self.fringe

                state = self.poll(self.fringe)()
                if self.debug:
                    try:
                        print >>stderr,"\t[pynlpl debug] CURRENT STATE (depth " + str(state.depth()) + "): " + str(state),
                    except AttributeError:
                        print >>stderr,"\t[pynlpl debug] CURRENT STATE: " + str(state),
                    try:
                        print >>stderr,state.score()
                    except:
                        pass


                if not self.usememory or (self.usememory and not hash(state) in self.visited):
                    
                    self.traversed += 1
                    #Evaluate state
                    if state.test(self.goalstates):
                        if self.debug: print >>stderr,"\t[pynlpl debug] Valid goalstate, yielding"
                        self.solutions += 1 #counts the number of solutions
                        yield state
                    elif self.debug:
                        print >>stderr,"\t[pynlpl debug] (no goalstate, not yielding)"

                    if self.eager:
                        score = state.score()                    

                    #Expand the specified state and offer to the fringe
                    
                    statecount = offers = 0
                    for j, s in enumerate(state.expand()):
                        statecount += 1
                        if self.debug >= 2:
                            print >>stderr,"\t[pynlpl debug] (Round #" + str(i) +" Beam #" + str(b) + ") Expanded state #" + str(j+1) + ", offering to successor pool: " + str(s),
                            try:
                                print >>stderr,s.score(),
                            except:
                                print >>stderr,"ERROR SCORING!",
                                pass
                        if not self.maxdepth or s.depth() <= self.maxdepth:
                            if not self.eager:
                                #use all successors (even worse ones than the current state)
                                offers += 1
                                accepted = successors.append(s)
                            else:
                                #use only equal or better successors
                                if s.score() >= score:
                                    offers += 1
                                    accepted = successors.append(s)
                                else:
                                    accepted = False
                            if self.debug >= 2:
                                if accepted:
                                    print >>stderr," ACCEPTED"
                                else:
                                    print >>stderr," REJECTED"
                        else:                            
                            if self.debug >= 2:
                                print >>stderr," REJECTED, MAXDEPTH EXCEEDED."
                            elif self.debug:
                                print >>stderr,"\t[pynlpl debug] (Round #" + str(n) +") Not offered to successor pool, maxdepth exceeded"
                    if self.debug:
                        print >>stderr,"\t[pynlpl debug] Expanded " + str(statecount) + " states, " + str(offers) + " offered to successor pool"
                    if self.keeptraversal: self.keeptraversal.append(state)
                    if self.usememory: self.visited[hash(state)] = True
                    self.prune(state) #calls prune method (does nothing by default in this search!!!)

                else:
                    if self.debug:
                        print >>stderr,"\t[pynlpl debug] State already visited before, not expanding again..."
            #AFTER EXPANDING ALL NODES IN THE FRINGE/BEAM:
            
            #set fringe for next round
            self.fringe = successors

            #Pruning is implicit, successors was a fixed-size priority queue
            if self.debug: 
                l = len(self.fringe)
                print >>stderr,"\t[pynlpl debug] (Round #" + str(i) + ") Implicitly pruned with beamsize " + str(self.beamsize) + "...",
            #self.fringe.prune(self.beamsize)
            if self.debug: print >>stderr," (" + str(offers) + " to " + str(len(self.fringe)) + " items)"
        
        if self.debug:
            print >>stderr,"\t[pynlpl debug] Search complete: " + str(self.solutions) + " solution(s), " + str(self.traversed) + " states traversed in " + str(n) + " rounds"            
        
        
        

class EarlyEagerBeamSearch(AbstractSearch):
    """A beam search that prunes early (after each state expansion) and eagerly (weeding out worse successors)"""
    
    def __init__(self, state, beamsize, **kwargs):
        assert isinstance(state, AbstractSearchState)
        self.beamsize = beamsize       
        super(EarlyEagerBeamSearch,self).__init__(**kwargs)
        self.fringe = PriorityQueue(state, lambda x: x.score, self.minimize, length=0, blockworse=False, blockequal=False,duplicates= kwargs['duplicates'] if 'duplicates' in kwargs else False)
        self.incomplete = True
    
    
    def prune(self, state):
        if self.debug: 
            l = len(self.fringe)
            print >>stderr,"\t[pynlpl debug] pruning with beamsize " + str(self.beamsize) + "...",
        self.fringe.prunebyscore(state.score(), retainequalscore=True)
        self.fringe.prune(self.beamsize)
        if self.debug: print >>stderr," (" + str(l) + " to " + str(len(self.fringe)) + " items)"


class BeamedBestFirstSearch(BeamSearch):
    """Best first search with a beamsize (non-optimal!)"""
    
    def prune(self, state):
        if self.debug: 
            l = len(self.fringe)
            print >>stderr,"\t[pynlpl debug] pruning with beamsize " + str(self.beamsize) + "...",
        self.fringe.prune(self.beamsize)
        if self.debug: print >>stderr," (" + str(l) + " to " + str(len(self.fringe)) + " items)"

class StochasticBeamSearch(BeamSearch):
    
    def prune(self, state):
        if self.debug: 
            l = len(self.fringe)
            print >>stderr,"\t[pynlpl debug] pruning with beamsize " + str(self.beamsize) + "...",
        if not self.exhaustive:
            self.fringe.prunebyscore(state.score(), retainequalscore=True)
        self.fringe.stochasticprune(self.beamsize)
        if self.debug: print >>stderr," (" + str(l) + " to " + str(len(self.fringe)) + " items)"
            

class HillClimbingSearch(AbstractSearch): #TODO: TEST
    """(identical to beamsearch with beam 1, but implemented differently)"""

    def __init__(self, state, **kwargs):
        assert isinstance(state, AbstractSearchState)
        super(HillClimbingSearch,self).__init__(**kwargs)
        self.fringe = PriorityQueue([state], lambda x: x.score, self.minimize, length=0, blockworse=True, blockequal=False,duplicates=False)
