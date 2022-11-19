import interactions    
from dataclasses import dataclass


@dataclass
class PrintableCommand:
    name: str
    description: str
    options: dict[str,tuple[str,str]]

    
def gather_all_commands(client:interactions.Client) -> dict[str, list[PrintableCommand]]:
    """Function for converting list of commands to dict {extension_name: [Command(), ...]}"""
    
    commands: dict[str, list[PrintableCommand]] = {}
    for command in client._commands:
        ext_name = str(command.extension.__class__.__name__)
        if ext_name not in commands:
            commands[ext_name] = []
        
        if command.options and command.options[0].type == interactions.OptionType.SUB_COMMAND:
            for sub_command in command.options:
                commands[ext_name].append(
                    PrintableCommand(
                        name=f'/{command.name} {sub_command.name}',
                        description=sub_command.description,
                        options={op.name: (op.description, op.type.name) for op in sub_command.options or []}
                    ))  # type: ignore
        else:
            commands[ext_name].append(
                PrintableCommand(
                    name=f'/{command.name}',
                    description=command.description or '',
                    options={op.name: (op.description, op.type.name) for op in command.options or []}
            ))
    return commands