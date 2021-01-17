[![Ansible Galaxy](https://img.shields.io/badge/galaxy-tobias__richter.tasmota-45712.svg)](https://galaxy.ansible.com/tobias_richter/tasmota)
[![Build Status](https://github.com/tobias-richter/ansible-tasmota/workflows/CI/badge.svg)](https://github.com/tobias-richter/ansible-tasmota/actions)

# tobias_richter.tasmota

This role allows you to configure tasmota devices by executing commands.

:bulb: See https://tasmota.github.io/docs/#/Commands for a command list.

This role/action_plugin will send commands to a tasmota device using web requests.
It will perform the following steps for each provided `command`,`value` pair in the `tasmota_commands`:
* It will retrieve the current setting of the provided `command`
* It will compare the result of this with the incoming `value`
  * when the new value differs from the existing value the command is executed with the new value and the task will report with `changed`
  * when there is no change detected the command will not execute the command (this will avoid restarts on several commands) 

## Requirements

This role requires some python requirements to be installed.

    pip install -r requirements.txt

## Limitations

### fact gathering

You have to disable fact gathering using `gather_facts: no` because tasmota devices are currently not supported by the facts module.

### `changed` reporting

Some commands like `SetOption` are accepting `int` values, like `0` or `1` but are returning `on` or `off` when queried for the current status.
This may cause wrong reported "changed" states. You are welcome to create a PR for adding support for uncovered commands.

## Role Variables

Available variables are listed below, along with their default values:

        tasmota_user: '' 
        tasmota_password: ''
        tasmota_commands: []
   
If tasmota_user and tasmota password are both non empty, they will be included in the commands to authenticate access.

Tasmota commands contains list of tasmota commands to be executed.
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

        # set and enable template (not that template is not a string)
      - command: Template
        value: {NAME: FooModule, GPIO: [1,2272,1,2304,1,1,0,0,1,1,1,1,1,0], FLAG: 0, BASE: 54}
      - command: Module
        value: 0 # Template


        # configure multiple TuyaMCU Functions (repeat for each fnId,dpId pair)
      - command: TuyaMCU
        value: 11,10
      - command: TuyaMCU
        value: 12,13

        # make sure that TuyaMCU fnId is disabled or missing
      - command: TuyaMCU
        value: 11,0
    
        # Example for no_log
      - command: MqttPassword
        value: MySafePassword
        no_log: True

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
