#coding=utf8

from uliweb.core.commands import Command, get_answer, CommandManager

class BuildCommand(CommandManager):
    name = 'build'
    args = 'build_command'
    check_apps_dirs = False
    has_options = True
    check_apps = False

    def get_commands(self, global_options):
        import subcommands
        cmds = get_commands(subcommands)
        return cmds
    
