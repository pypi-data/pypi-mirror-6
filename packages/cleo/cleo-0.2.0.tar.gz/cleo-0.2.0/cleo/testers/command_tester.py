# -*- coding: utf-8 -*-

from io import BytesIO

from ..inputs.list_input import ListInput
from ..outputs.stream_output import StreamOutput


class CommandTester(object):
    """
    Eases the testing of console commands.
    """

    def __init__(self, command):
        """
        Constructor

        @param command: A Command instance to test
        @type command: Command
        """
        self.__command = command
        self.__input = None
        self.__output = None

    def execute(self, input_, options=None):
        """
        Executes the command

        Available options:
            * interactive: Sets the input interactive flag
            * decorated: Sets the output decorated flag
            * verbosity: Sets the output verbosity flag

        @param input_: A dict of argument and options
        @type input_: list
        @param options: A dict of options
        @type options: dict

        @return: The command exit code
        @rtype: integer
        """
        options = options or {}

        self.__input = ListInput(input_)
        if 'interactive' in options:
            self.__input.set_interactive(options['interactive'])

        self.__output = StreamOutput(BytesIO())
        if 'decorated' in options:
            self.__output.set_decorated(options['decorated'])
        if 'verbosity' in options:
            self.__output.set_verbosity(options['verbosity'])

        return self.__command.run(self.__input, self.__output)

    def get_display(self):
        """
        Gets the display returned by the last execution command

        @return: The display
        @rtype: str
        """
        self.__output.get_stream().seek(0)

        return self.__output.get_stream().read().decode('utf-8')

    def get_input(self):
        """
        Gets the input instance used by the last execution of the command.

        @return: The current input instance
        @rtype: Input
        """
        return self.__input

    def get_output(self):
        """
        Gets the output instance used by the last execution of the command.

        @return: The current output instance
        @rtype: Output
        """
        return self.__output
