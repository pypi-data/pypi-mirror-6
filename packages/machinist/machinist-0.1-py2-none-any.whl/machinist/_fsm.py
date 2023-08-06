# Copyright Hybrid Logic Ltd.  See LICENSE file for details.
# -*- test-case-name: machinist.test.test_fsm -*-

"""
Implementation details for machinist's public interface.
"""

from zope.interface import Attribute, Interface, implementer, provider
from zope.interface.exceptions import DoesNotImplement

from eliot import Field, ActionType, Logger

from twisted.python.util import FancyStrMixin, FancyEqMixin
from twisted.python.components import proxyForInterface
from twisted.internet.defer import succeed

def _system(suffix):
    return u":".join((u"fsm", suffix))


FSM_IDENTIFIER = Field.forTypes(
    u"fsm_identifier", [unicode],
    u"An unique identifier for the FSM to which the event pertains.")
FSM_STATE = Field.forTypes(
    u"fsm_state", [unicode], u"The state of the FSM prior to the transition.")
FSM_RICH_INPUT = Field.forTypes(
    u"fsm_rich_input", [unicode],
    u"The string representation of the rich input delivered to the FSM.")
FSM_INPUT = Field.forTypes(
    u"fsm_input", [unicode],
    u"The string representation of the input symbol delivered to the FSM.")
FSM_NEXT_STATE = Field.forTypes(
    u"fsm_next_state", [unicode],
    u"The string representation of the state of the FSM after the transition.")
FSM_OUTPUT = Field.forTypes(
    u"fsm_output", [list], # of unicode
    u"A list of the string representations of the outputs produced by the "
    u"transition.")
FSM_TERMINAL_STATE = Field.forTypes(
    u"fsm_terminal_state", [unicode],
    u"The string representation of the terminal state entered by the the FSM.")

LOG_FSM_INITIALIZE = ActionType(
    _system(u"initialize"),
    [FSM_IDENTIFIER, FSM_STATE],
    [FSM_TERMINAL_STATE],
    [],
    u"A finite state machine was initialized.")

LOG_FSM_TRANSITION = ActionType(
    _system(u"transition"),
    [FSM_IDENTIFIER, FSM_STATE, FSM_RICH_INPUT, FSM_INPUT],
    [FSM_NEXT_STATE, FSM_OUTPUT],
    [],
    u"A finite state machine received an input made a transition.")

class IFiniteStateMachine(Interface):
    """
    A finite state machine.
    """
    state = Attribute("The current state of the machine.")

    # We could probably make the state, input, and output types part of this
    # interface as well.  This could facilitate more advanced tools for
    # operating on state machines (eg, tools for chaining several together).

    def receive(input):
        """
        Accept an input, transition to the next state, and return the generated
        output.

        @raise UnhandledInput: If the received input is not acceptable in the
            current state.

        @raise IllegalInput: If the received input is not acceptable in any
            state by this state machine.
        """



class IOutputExecutor(Interface):
    """
    Perform tasks and cause side-effects associated with outputs from a
    L{IFiniteStateMachine}.
    """
    def identifier():
        """
        Return a constant L{unicode} string that should uniquely identify this
        executor.  This will be used to uniquely identify log events associated
        with it.

        @rtype: L{unicode}
        """


    def output(output, context):
        """
        Perform the operations associated with a particular output.
        """



class IRichInput(Interface):
    """
    A L{IRichInput} implementation corresponds to a particular symbol in the
    input alphabet of a state machine but may also carry additional
    information.
    """
    def symbol():
        """
        Return the symbol from the input alphabet to which this input
        corresponds.
        """



class StateMachineDefinitionError(Exception):
    """
    This is the base class for exceptions relating to problems in the
    definition of a state machine (problems that will lead to the construction
    of a state machine from said definition to fail).
    """



class ExtraTransitionState(StateMachineDefinitionError):
    """
    There are extra states in the transition table which are not explicitly
    defined by the state L{Names} subclass.
    """



class MissingTransitionState(StateMachineDefinitionError):
    """
    There are states explicitly defined by the state L{Names} subclass which
    are not defined in the transition table.
    """



class ExtraTransitionInput(StateMachineDefinitionError):
    """
    There are extra inputs handled by the transition table which are not explicitly
    defined by the input L{Names} subclass.
    """



class MissingTransitionInput(StateMachineDefinitionError):
    """
    There are inputs explicitly defined by the input L{Names} subclass which
    are not handled by any state in the transition table.
    """



class ExtraTransitionOutput(StateMachineDefinitionError):
    """
    There are extra outputs defined by the transition table which are not explicitly
    defined by the output L{Names} subclass.
    """



class MissingTransitionOutput(StateMachineDefinitionError):
    """
    There are outputs explicitly defined by the output L{Names} subclass which
    are not generated by any state transition in the transition table.
    """



class ExtraTransitionNextState(StateMachineDefinitionError):
    """
    There are extra states as next state values in the transition table which
    are not explicitly defined by the state L{Names} subclass.
    """



class MissingTransitionNextState(StateMachineDefinitionError):
    """
    There are states explicitly defined by the state L{Names} subclass which
    cannot be reached by any input in any state defined by the transition table
    and are also not the initial state.
    """



class InvalidInitialState(StateMachineDefinitionError):
    """
    The initial state of the state machine is given as a value which is not
    explicitly defined by the state L{Names} subclass.
    """



class ExtraInputContext(StateMachineDefinitionError):
    """
    An input context is defined for a value which is not explicitly defined by
    the output L{Names} subclass.
    """



class UnhandledInput(Exception):
    """
    The state machine received an input for which no transition was defined in
    the machine's current state.
    """



class IllegalInput(Exception):
    """
    The state machine received an input which is not part of the machine's
    input alphabet.
    """



class Transition(FancyStrMixin, FancyEqMixin, object):
    """
    A L{Transition} represents an output produced and the next state to assume
    by a L{IFiniteStateMachine} on receipt of a particular input in a
    particular state.
    """
    compareAttributes = showAttributes = ["output", "nextState"]

    def __init__(self, output, nextState):
        self.output = output
        self.nextState = nextState



class TransitionTable(object):
    """
    A L{TransitionTable} contains the definitions of all state transitions for
    a L{IFiniteStateMachine}.

    @ivar table: L{dict} mapping symbols from C{states} to L{dict} mapping
        symbols from C{inputs} to L{Transition} instances giving the output and
        next state when the corresponding input is received.

    @note: L{TransitionTable} has no methods which mutate instances of it.
        Instances are meant to be immutable to simplify reasoning about state
        machines and to facilitate sharing of transition definitions.
    """
    def __init__(self, table=None):
        if table is None:
            table = {}
        self.table = table


    def _copy(self):
        """
        Create a new L{TransitionTable} just like this one using a copy of the
        underlying transition table.

        @rtype: L{TransitionTable}
        """
        table = {}
        for existingState, existingOutputs in self.table.items():
            table[existingState] = {}
            for (existingInput, existingTransition) in existingOutputs.items():
                table[existingState][existingInput] = existingTransition
        return TransitionTable(table)


    def addTransition(self, state, input, output, nextState):
        """
        Create a new L{TransitionTable} with all the same transitions as this
        L{TransitionTable} plus a new transition.

        @param state: The state for which the new transition is defined.
        @param input: The input that triggers the new transition.
        @param output: The output produced by the new transition.
        @param nextState: The state that will follow the new transition.

        @return: The newly created L{TransitionTable}.
        """
        return self.addTransitions(state, {input: (output, nextState)})


    def addTransitions(self, state, transitions):
        """
        Create a new L{TransitionTable} with all the same transitions as this
        L{TransitionTable} plus a number of new transitions.

        @param state: The state for which the new transitions are defined.
        @param transitions: A L{dict} mapping inputs to output, nextState
            pairs.  Each item from this L{dict} will define a new transition in
            C{state}.

        @return: The newly created L{TransitionTable}.
        """
        table = self._copy()
        state = table.table.setdefault(state, {})
        for (input, (output, nextState)) in transitions.items():
            state[input] = Transition(output, nextState)
        return table


    def addTerminalState(self, state):
        """
        Create a new L{TransitionTable} with all of the same transitions as
        this L{TransitionTable} plus a new state with no transitions.

        @param state: The new state to include in the new table.

        @return: The newly created L{TransitionTable}.
        """
        table = self._copy()
        table.table[state] = {}
        return table



def _missingExtraCheck(given, required, extraException, missingException):
    """
    If the L{sets<set>} C{required} and C{given} do not contain the same
    elements raise an exception describing how they are different.

    @param given: The L{set} of elements that was actually given.
    @param required: The L{set} of elements that must be given.

    @param extraException: An exception to raise if there are elements in
        C{given} that are not in C{required}.
    @param missingException: An exception to raise if there are elements in
        C{required} that are not in C{given}.

    @return: C{None}
    """
    extra = given - required
    if extra:
        raise extraException(extra)

    missing = required - given
    if missing:
        raise missingException(missing)



def constructFiniteStateMachine(inputs, outputs, states, table, initial,
                                richInputs, inputContext, world,
                                logger=Logger()):
    """
    Construct a new finite state machine from a definition of its states.

    @param inputs: Definitions of all input symbols the resulting machine will
        need to handle, as a L{twisted.python.constants.Names} subclass.

    @param outputs: Definitions of all output symbols the resulting machine is
        allowed to emit, as a L{twisted.python.constants.Names} subclass.

    @param states: Definitions of all possible states the resulting machine
        will be capable of inhabiting, as a L{twisted.python.constants.Names}
        subclass.

    @param table: The state transition table, defining which output and next
        state results from the receipt of any and all inputs in any and all
        states.
    @type table: L{TransitionTable}

    @param initial: The state the machine will start in (one of the symbols
        from C{states}).

    @param richInputs: A L{list} of types which correspond to each of the input
        symbols from C{inputs}.
    @type richInputs: L{list} of L{IRichInput} I{providers}

    @param inputContext: A L{dict} mapping output symbols to L{Interface}
        subclasses describing the requirements of the inputs which lead to
        them.

    @param world: An object responsible for turning FSM outputs into observable
        side-effects.
    @type world: L{IOutputExecutor} provider

    @return: An L{IFiniteStateMachine} provider
    """
    table = table.table

    _missingExtraCheck(
        set(table.keys()), set(states.iterconstants()),
        ExtraTransitionState, MissingTransitionState)

    _missingExtraCheck(
        set(i for s in table.values() for i in s), set(inputs.iterconstants()),
        ExtraTransitionInput, MissingTransitionInput)

    _missingExtraCheck(
        set(output for s in table.values() for transition in s.values() for output in transition.output),
        set(outputs.iterconstants()),
        ExtraTransitionOutput, MissingTransitionOutput)

    try:
        _missingExtraCheck(
            set(transition.nextState for s in table.values() for transition in s.values()),
            set(states.iterconstants()),
            ExtraTransitionNextState, MissingTransitionNextState)
    except MissingTransitionNextState as e:
        if e.args != ({initial},):
            raise

    if initial not in states.iterconstants():
        raise InvalidInitialState(initial)

    extraInputContext = set(inputContext) - set(outputs.iterconstants())
    if extraInputContext:
        raise ExtraInputContext(extraInputContext)

    _checkConsistency(richInputs, table, inputContext)

    fsm = _FiniteStateMachine(inputs, outputs, states, table, initial)
    executor = IOutputExecutor(world)
    return _FiniteStateLogger(
        _FiniteStateInterpreter(
            tuple(richInputs), inputContext, fsm, executor),
        logger, executor.identifier())



def _checkConsistency(richInputs, fsm, inputContext):
    """
    Verify that the outputs that can be generated by fsm have their
    requirements satisfied by the given rich inputs.

    @param richInputs: A L{list} of all of the types which will serve as rich
        inputs to an L{IFiniteStateMachine}.
    @type richInputs: L{list} of L{IRichInput} providers

    @param fsm: The L{IFiniteStateMachine} to which these rich inputs are to be
        delivered.

    @param inputContext: A L{dict} mapping output symbols to L{Interface}
        subclasses.  Rich inputs which result in these outputs being produced
        by C{fsm} must provide the corresponding interface.

    @raise DoesNotImplement: If any of the rich input types fails to implement
        the interfaces required by the outputs C{fsm} can produce when they are
        received.
    """
    for richInput in richInputs:
        for state in fsm:
            for input in fsm[state]:
                if richInput.symbol() == input:
                    # This rich input will be supplied to represent this input
                    # symbol in this state.  Check to see if it satisfies the
                    # output requirements.
                    outputs = fsm[state][input].output
                    for output in outputs:
                        try:
                            required = inputContext[output]
                        except KeyError:
                            continue
                        # Consider supporting non-interface based checking in
                        # the future: extend this to also allow
                        # issubclass(richInput, required)
                        if required.implementedBy(richInput):
                            continue
                        raise DoesNotImplement(
                            "%r not implemented by %r, "
                            "required by %r in state %r" % (
                                required, richInput,
                                input, state))



def _symbol(which):
    # Work-around for Twisted #5797 - fixed in 13.0.0
    return classmethod(lambda cls: which)



def trivialInput(symbol):
    """
    Create a new L{IRichInput} implementation for the given input symbol.

    This creates a new type object and is intended to be used at module scope
    to define rich input types.  Generally, only one use per symbol should be
    required.  For example::

        Apple = trivialInput(Fruit.apple)

    @param symbol: A symbol from some state machine's input alphabet.

    @return: A new type object usable as a rich input for the given symbol.
    @rtype: L{type}
    """
    return provider(IRichInput)(type(
            symbol.name.title(), (FancyStrMixin, object), {
                "symbol": _symbol(symbol),
                }))



@implementer(IFiniteStateMachine)
class _FiniteStateMachine(object):
    """
    A L{_FiniteStateMachine} tracks the core logic of a finite state machine:
    recording the current state and mapping inputs to outputs and next states.

    @ivar inputs: See L{constructFiniteStateMachine}
    @ivar outputs: See L{constructFiniteStateMachine}
    @ivar states: See L{constructFiniteStateMachine}
    @ivar table: See L{constructFiniteStateMachine}
    @ivar initial: See L{constructFiniteStateMachine}

    @ivar state: The current state of this FSM.
    @type state: L{NamedConstant} from C{states}
    """
    def __init__(self, inputs, outputs, states, table, initial):
        self.inputs = inputs
        self.outputs = outputs
        self.states = states
        self.table = table
        self.initial = initial
        self.state = initial


    def receive(self, input):
        try:
            current = self.table[self.state]
        except KeyError:
            raise ValueError(
                "FiniteStateMachine has no transition table for state %r!" % (
                    self.state,))
        try:
            transition = current[input]
        except KeyError:
            raise UnhandledInput(self.state, input)

        self.state = transition.nextState
        return transition.output



class _FiniteStateLogger(proxyForInterface(IFiniteStateMachine, "_fsm")):
    """
    L{_FiniteStateLogger} wraps another L{IFiniteStateMachine} provider and
    adds to it logging of all state transitions.
    """
    def __init__(self, fsm, logger, identifier):
        super(_FiniteStateLogger, self).__init__(fsm)
        self.logger = logger
        self.identifier = identifier
        self._action = LOG_FSM_INITIALIZE(
            logger, fsm_identifier=identifier, fsm_state=unicode(fsm.state))


    def receive(self, input):
        """
        Add logging of state transitions to the wrapped state machine.

        @see: L{IFiniteStateMachine.receive}
        """
        action = LOG_FSM_TRANSITION(
            self.logger,
            fsm_identifier=self.identifier,
            fsm_state=unicode(self.state),
            fsm_rich_input=unicode(input),
            fsm_input=unicode(input.symbol()))
        with action as theAction:
            output = super(_FiniteStateLogger, self).receive(input)
            theAction.addSuccessFields(
                fsm_next_state=unicode(self.state), fsm_output=[unicode(o) for o in output])

        if self._action is not None and self._isTerminal(self.state):
            self._action.addSuccessFields(
                fsm_terminal_state=unicode(self.state))
            # Better API will be available after
            # https://www.pivotaltracker.com/s/projects/787341/stories/59751070
            # is done.
            self._action.finishAfter(succeed(None))
            self._action = None

        return output


    def _isTerminal(self, state):
        """
        Determine if a state is terminal.

        A state is terminal if there are no outputs or state changes defined
        for any inputs in that state.

        @rtype: L{bool}
        """
        # This only works with _FiniteStateMachine not with arbitrary
        # IFiniteStateMachine since these attributes aren't part of the
        # interface.  This is private with the idea that maybe terminal should
        # be defined differently eventually - perhaps by accepting an explicit
        # set of terminal states in constructFiniteStateMachine.
        # https://www.pivotaltracker.com/story/show/59999580
        return all(
            transition.output == [] and transition.nextState == state
            for (input, transition)
            in self._fsm._fsm.table[state].iteritems())



@implementer(IFiniteStateMachine)
class _FiniteStateInterpreter(object):
    """
    A L{_FiniteStateInterpreter} translates between the "real world" - which
    has rich inputs and non-pure outputs - and a finite state machine which
    accepts only symbolic inputs and produces only symbolic outputs.

    @ivar _richInputs: All the types of rich inputs that are allowed.
    @type _richInputs: L{tuple} of L{type}

    @ivar _inputContext: Adapters from rich input types to whatever types are
        required by the output executor.  The context passed to
        L{IOutputExecutor.output} is constructed by calling an adapter from
        this dictionary with the rich input that resulted in the output.
    @type _inputContext: L{dict} mapping L{type} to one-argument callables

    @ivar _fsm: The underlying, pure state machine.
    @type _fsm: L{IFiniteStateMachine} provider

    @ivar _world: The L{IOutputExecutor} provider this interpreter will drive
        with outputs from C{_fsm}.
    """

    def __repr__(self):
        return "<FSM / %s>" % (self._world,)

    @property
    def state(self):
        return self._fsm.state


    def __init__(self, richInputs, inputContext, fsm, world):
        self._richInputs = richInputs
        self._inputContext = inputContext
        self._fsm = fsm
        self._world = world


    def receive(self, input):
        """
        Deliver an input symbol to the wrapped L{IFiniteStateMachine} from the
        given rich input and deliver the resulting outputs to the wrapped
        L{IOutputExecutor}.

        @param input: An instance of one of the rich input types this state
            machine was initialized with.

        @return: The output from the wrapped L{IFiniteStateMachine}.
        """
        symbol = input.symbol()
        if not isinstance(input, self._richInputs):
            raise IllegalInput(symbol)
        outputs = self._fsm.receive(symbol)
        for output in outputs:
            adapter = self._inputContext.get(output, lambda o: o)
            self._world.output(output, adapter(input))
        return outputs



@implementer(IOutputExecutor)
class MethodSuffixOutputer(object):
    """
    A helper to do simple suffixed-method style output dispatching.

    @ivar original: Any old object with a bunch of C{output_}-prefixed methods.
    @ivar _identifier: The cached identifier of the wrapped object (cached to
        guarantee it never changes).
    """
    def __repr__(self):
        return "<Output / %s>" % (self.original,)


    def __init__(self, original):
        self.original = original
        try:
            identifier = self.original.identifier
        except AttributeError:
            self._identifier = repr(self.original).decode("ascii")
        else:
            self._identifier = identifier()


    def identifier(self):
        """
        Try delegating to the wrapped object.  Provide a simple default if the
        wrapped object doesn't implement this method.
        """
        return self._identifier


    def output(self, output, context):
        """
        Call the C{output_NAME} method of the wrapped object - where I{NAME} is
        the name of C{output}.

        @see: L{IOutputExecutor.output}
        """
        getattr(self.original, "output_" + output.name.upper())(context)



class WrongState(Exception):
    def __init__(self, stateful, pssr):
        Exception.__init__(
            self,
            "Attribute illegal in state %s, only allowed in states %s" % (
                stateful._getter(pssr), stateful._allowed))



class stateful(object):
    """
    A L{stateful} descriptor can only be used when an associated finite state
    machine is in a certain state (or states).

    @ivar _allowed: A L{tuple} of the states in which access to this attribute
        is allowed.

    @ivar _getter: A one-argument callable which accepts the object the
        descriptor is used on and returns the state of that object for
        comparison against C{_allowed}.

    @note: The current implementation strategy for this descriptor type is to
        store the application value in the instance C{__dict__} using the
        L{stateful} instance as the key.  This means that the instance must
        have a C{__dict__} (ie, not use C{__slots__}), that non-string keys are
        put into C{__dict__}, and that sharing a single L{stateful} instance to
        represent two different attributes will produce confusing (probably
        incorrect) results.
    """
    def __init__(self, getter, *allowed):
        self._getter = getter
        self._allowed = allowed


    def __get__(self, obj, cls):
        if obj is None:
            return self
        if self._getter(obj) in self._allowed:
            try:
                return obj.__dict__[self]
            except KeyError:
                raise AttributeError()
        raise WrongState(self, obj)


    def __set__(self, obj, value):
        if self._getter(obj) not in self._allowed:
            raise WrongState(self, obj)
        obj.__dict__[self] = value


    def __delete__(self, obj):
        if self._getter(obj) not in self._allowed:
            raise WrongState(self, obj)
        try:
            del obj.__dict__[self]
        except KeyError:
            raise AttributeError()
