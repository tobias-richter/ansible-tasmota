# tobias_richter.tasmota

This role allows you to configure tasmota devices by executing commands.
See https://tasmota.github.io/docs/#/Commands for a command list.

## Requirements

This role requires `requests` to be installed.

    pip install requests

## Limitations

### fact gathering

You have to disable fact gathering using `gather_facts: no` because tasmota devices are currently not supported by the facts module.

### `changed` reporting

Some commands like `SetOption` are accepting `int` values, like `0` or `1` but are returning `on` or `off` when queried for the current status.
This may cause wrong reported "changed" states. You are welcome to create a PR for adding support for uncovered commands.

## Role Variables

Available variables are listed below, along with their default values:

    tasmota_commands: []
    
A list of tasmota commands to execute.

Each tasmota_command is defined as:

    - command: <COMMAND>
      value: <VALUE>
      
e.g.

    tasmota_commands:
        
        # set TelePeriod to 10 seconds
      - command: TelePeriod
        value: 10
        
        # extend TelePeriod to 3600 seconds when switch is turned off, set do default when switch is turned on
      - command: Rule1
        value: "on Power1#state=0 do TelePeriod 3600 endon on Power1#state=1 do TelePeriod 1 endon"
        
        # enable Rule1
      - command: Rule1
        value: 1
        
        # enable one shot for Rule1
      - command: Rule1
        value: 5

## Tipps

To avoid specifying `tasmota_commands` for each host using host_vars you can use a construct similar to this:

    # commands for all instances
    default_tasmota_commands:
      # set custom NtpServer
      - command: NtpServer1
        value: 192.168.0.1
      - command: LedState
        value: 0      
    
    # specific commands 
    specific_tasmota_commands:
      tasmota001:
        - command: FriendlyName1
          value: TV
    
      tasmota002:
        - command: FriendlyName1
          value: HiFi
    
    tasmota_commands: "{{ default_tasmota_commands | union(specific_tasmota_commands[inventory_hostname] | default([])) }}"

## Example

Sets the `TelePeriod` to 10 seconds to all devices specified in the `tasmota` host group.

	- hosts: tasmota_devices  
	  # disable fact gathering since this is currently not possible on tasmota devices  
      gather_facts: no
      vars:
        tasmota_commands:
            - command: TelePeriod
              value: 10
	  roles:
	    - tobias_richter.tasmota


## License

Apache 2.0
