"Shell command line completion support"
from begin import subcommands

completers = subcommands.Collector()

@subcommands.subcommand(collector=completers)
def _bash_completion(command, partial, previous):
    """Command line completion for bash shell

    To use, register the subcommand with bash a the command line completion
    function for this program.

        $ complete -o default -C '%(prog)s _bash_completion' %(prog)s

    Bash will now call this subcommand when attempting shell completion of
    arguments.
    """
