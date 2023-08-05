#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Octopasty is an Asterisk AMI proxy

# Copyright © 2011, 2012  Jean Schurger <jean@schurger.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""\
Asterisk specific AMI actions.
"""

__metaclass__ = type

### AMI Message Keys.

# From Manager_Key name to Manager_Key subclass.
manager_keys = {}


class Manager_Key:

    # Key text.
    name = None

    # Sequence of fixed replies.
    fixed = None

    # Set of previous replies (if not fixed).
    previous = None

    @classmethod
    def each_name(this):
        text = this.name
        if text.endswith('_'):
            text = text[:-1]
        yield text

    @classmethod
    def validate(this, ami_message, value):
        if not (this.fixed is None or value in this.fixed):
            return "Invalid value.  (Hint: TAB shows choices)"


class Manager_Key1(Manager_Key):

    @classmethod
    def each_name(this):
        suffix = 1
        while True:
            yield '%s%d' % (this.name, suffix)
            suffix += 1


class Manager_Key6(Manager_Key):

    @classmethod
    def each_name(this):
        suffix = 0
        while True:
            yield '%s-%.6d' % (this.name, suffix)
            suffix += 1


class Manager_KeyPar(Manager_Key):

    @classmethod
    def each_name(this):
        suffix = 0
        while True:
            yield '%s(%d)' % (this.name, suffix)
            suffix += 1


class AOCBillingId(Manager_Key):
    fixed = ('Normal', 'ReverseCharge', 'CreditCard', 'CallFwdUnconditional',
             'CallFwdBusy', 'CallFwdNoReply', 'CallDeflection', 'CallTransfer')
    name = 'AOCBillingId'


class Account(Manager_Key):
    name = 'Account'


class Action(Manager_Key):
    "Requested manager action or command."
    name = 'Action'


class Action_(Manager_Key6):
    fixed = ('NewCat', 'RenameCat', 'DelCat', 'EmptyCat', 'Update', 'Delete',
             'Append', 'Insert')
    name = 'Action'


class ActionID(Manager_Key):
    "ActionID for this transaction. Will be returned."
    name = 'ActionID'


class Agent(Manager_Key):
    name = 'Agent'


class Application(Manager_Key):
    name = 'Application'


class Async(Manager_Key):
    name = 'Async'


class AuthType(Manager_Key):
    fixed = 'MD5',


class CallerID(Manager_Key):
    name = 'CallerID'


class Cat(Manager_Key6):
    fixed = ('NewCat', 'RenameCat', 'DelCat', 'Update', 'Delete',
             'Append', 'Insert')
    name = 'Cat'


class Category(Manager_Key):
    name = 'Category'


class Cause(Manager_Key):
    name = 'Cause'


class Channel1(Manager_Key):
    name = 'Channel1'


class Channel2(Manager_Key):
    name = 'Channel2'


class Channel(Manager_Key):
    name = 'Channel'


class ChannelPrefix(Manager_Key):
    name = 'ChannelPrefix'


class ChargeType(Manager_Key):
    name = 'ChargeType'
    fixed = 'NA', 'FREE', 'Currency', 'Unit'


class ChargingAssociationId(Manager_Key):
    name = 'ChargingAssociationId'

    @classmethod
    def validate(this, ami_message, value):
        try:
            value = int(value)
        except ValueError:
            pass
        else:
            if -32768 <= value <= 32767:
                return None
        return "Value should be an integer between -32768 and 32767."


class ChargingAssociationNumber(Manager_Key):
    name = 'ChargingAssociationNumber'


class ChargingAssociationPlan(Manager_Key):
    name = 'ChargingAssociationPlan'

    @classmethod
    def validate(this, ami_message, value):
        if not (value.isdigit() and 0 <= int(value) <= 127):
            return "Value should be between 0 and 127."


class Codecs(Manager_Key):
    name = 'Codecs'


class Command_(Manager_Key):
    name = 'Command'


class CommandID(Manager_Key):
    name = 'CommandID'


class Conference(Manager_Key):
    name = 'Conference'


class Context(Manager_Key):
    name = 'Context'


class CurrencyAmount(Manager_Key):
    name = 'CurrencyAmount'

    @classmethod
    def validate(this, ami_message, value):
        if not value.isdigit() or int(value) <= 0:
            return "Value should be a positive integer."


class CurrencyMultiplier(Manager_Key):
    fixed = ('OneThousandth', 'OneHundredth', 'OneTenth',
             'One', 'Ten', 'Hundred', 'Thousand')
    name = 'CurrencyMultiplier'


class CurrencyName(Manager_Key):
    name = 'CurrencyName'


class DAHDIChannel(Manager_Key):
    name = 'DAHDIChannel'


class Data(Manager_Key):
    name = 'Data'


class Device(Manager_Key):
    name = 'Device'


class Digit(Manager_Key):
    name = 'Digit'


class Direction(Manager_Key):
    name = 'Direction'


class DstFilename(Manager_Key):
    name = 'DstFilename'


class Event(Manager_Key):
    name = 'Event'


class EventMask(Manager_Key):
    name = 'EventMask'
    previous = set(['on', 'off', 'system', 'call', 'log'])


class Exten(Manager_Key):
    name = 'Exten'


class Extension(Manager_Key):
    name = 'Extension'


class ExtraChannel(Manager_Key):
    name = 'ExtraChannel'


class ExtraContext(Manager_Key):
    name = 'ExtraContext'


class ExtraExten(Manager_Key):
    name = 'ExtraExten'


class ExtraPriority(Manager_Key):
    name = 'ExtraPriority'


class Family(Manager_Key):
    name = 'Family'


class File(Manager_Key):
    name = 'File'


class Filename(Manager_Key):
    name = 'Filename'


class Filter(Manager_Key):
    name = 'Filter'


class Format(Manager_Key):
    name = 'Format'


class Header(Manager_Key1):
    name = 'Header'


class Interface(Manager_Key):
    name = 'Interface'


class JID(Manager_Key):
    name = 'JID'


class Jabber(Manager_Key):
    name = 'Jabber'


class Key(Manager_Key):
    name = 'Key'


class Line(Manager_Key):
    name = 'Line'


class Line_(Manager_Key6):
    name = 'Line'


class LoadType(Manager_Key):
    name = 'LoadType'
    fixed = 'load', 'unload', 'reload'


class Mailbox(Manager_Key):
    name = 'Mailbox'


class Match(Manager_Key6):
    name = 'Match'


class Meetme(Manager_Key):
    name = 'Meetme'


class Member(Manager_Key):
    name = 'Member'


class MemberName(Manager_Key):
    name = 'MemberName'


class Members(Manager_Key):
    name = 'Members'
    fixed = 'yes', 'no'


class Message(Manager_Key):
    name = 'Message'


class Mix(Manager_Key):
    name = 'Mix'


class Module(Manager_Key):
    fixed = 'cdr', 'enum', 'dnsmgr', 'extconfig', 'manager', 'rtp', 'http'
    name = 'Module'


class MsgType(Manager_Key):
    fixed = 'D', 'E'
    name = 'MsgType'


class Number(Manager_Key):
    name = 'Number'


class Parameters(Manager_Key):
    name = 'Parameters'
    fixed = 'yes', 'no'


class Parkinglot(Manager_Key):
    name = 'Parkinglot'


class Path(Manager_Key):
    name = 'Path'


class Paused(Manager_Key):
    name = 'Paused'


class Peer(Manager_Key):
    name = 'Peer'


class Penalty(Manager_Key):
    name = 'Penalty'


class Priority(Manager_Key):
    name = 'Priority'


class Queue(Manager_Key):
    name = 'Queue'


class Reason(Manager_Key):
    name = 'Reason'


class Reload_(Manager_Key):
    name = 'Reload'


class Rule(Manager_Key):
    name = 'Rule'


class Rules(Manager_Key):
    fixed = 'yes', 'no'
    name = 'Rules'


class Search(Manager_Key):
    name = 'Search'


class Secret(Manager_Key):
    name = 'Secret'


class Soft(Manager_Key):
    name = 'Soft'


class SrcFilename(Manager_Key):
    fixed = 'false', 'true'
    name = 'SrcFilename'


class State(Manager_Key):
    name = 'State'


class StateInterface(Manager_Key):
    name = 'StateInterface'


class Timeout(Manager_Key):
    name = 'Timeout'

    @classmethod
    def validate(this, ami_message, value):
        if not value.isdigit():
            # FIXME: floating values are acceptable?
            return "Value should be an integer."


class Tone(Manager_Key):
    fixed = 'yes', 'no'
    name = 'Tone'


class TotalType(Manager_Key):
    fixed = 'Total', 'SubTotal'
    name = 'TotalType'


class Uniqueid(Manager_Key):
    name = 'Uniqueid'


class UnitAmount(Manager_KeyPar):
    name = 'UnitAmount'

    @classmethod
    def validate(this, ami_message, value):
        if not value.isdigit():
            return "Value should be an integer."


class UnitType(Manager_Key):
    name = 'UnitType_'
    previous = set(map(str, range(1, 17)))

    @classmethod
    def validate(this, ami_message, value):
        if not value.isdigit():
            return "Value should be an integer."


class UserEvent_(Manager_Key):
    name = 'UserEvent_'


class Username(Manager_Key):
    name = 'Username'


class Usernum(Manager_Key):
    name = 'Usernum'


class Val(Manager_Key):
    name = 'Val'


class Value(Manager_Key):
    name = 'Value'


class Value_(Manager_Key6):
    name = 'Value'


class Var(Manager_Key6):
    name = 'Var'


class Variable(Manager_Key):
    name = 'Variable'


class Variables(Manager_Key):
    name = 'Variables'


### Asterisk Manager Actions.

# From Manager_Action name to Manager_Action subclass.
manager_actions = {}


class Manager_Action:
    "Base for all manager actions bubbles."
    # This base class is merely used for finding derived classes in
    # this module.  The real Manager_Action base sits in the ami.py
    # module and gets mixed in, see it for default fields and methods.
    description = None


class AbsoluteTimeout(Manager_Action):
    description = (
        "Hangup a channel after a certain time."
        " Acknowledges set time with Timeout Set message.")
    keys = [
        ActionID,
        (Channel, "Channel name to hangup."),
        (Timeout, "Maximum duration of the call (sec).")]
    name = 'AbsoluteTimeout'
    summary = "Set absolute timeout."


class AgentLogoff(Manager_Action):
    keys = [
        ActionID,
        (Agent, "Agent ID of the agent to log off."),
        (Soft, "Set to true to not hangup existing calls.")]
    name = 'AgentLogoff'
    summary = "Sets an agent as no longer logged in."


class Agents(Manager_Action):
    description = "Will list info about all possible agents."
    keys = [ActionID]
    name = 'Agents'
    summary = "Lists agents and their status."


class AGI(Manager_Action):
    description = (
        "Add an AGI command to the execute queue of the channel in Async AGI.")
    keys = [
        ActionID,
        (Channel, "Channel that is currently in Async AGI."),
        (Command_, "Application to execute."),
        (CommandID, (
            "This will be sent back in CommandID header of AsyncAGI exec event"
            " notification."))]
    name = 'AGI'
    summary = "Add an AGI command to execute by Async AGI."


class AOCMessage(Manager_Action):
    description = "Generates an AOC-D or AOC-E message on a channel."
    keys = [
        ActionID,
        (Channel, "Channel name to generate the AOC message on."),
        (ChannelPrefix, (
            "Partial channel prefix."
            " By using this option one can match the beginning part of a"
            " channel name without having to put the entire name in."
            " For example if a channel name is SIP/snom-00000001 and this"
            " value is set to SIP/snom, then that channel matches and the"
            " message will be sent."
            " Note however that only the first matched channel has the"
            " message sent on it.")),
        (MsgType, (
            "Defines what type of AOC message to create, AOC-D or AOC-E")),
        (ChargeType, "Defines what kind of charge this message represents."),
        (UnitAmount, (
            "This represents the amount of units charged."
            " The ETSI AOC standard specifies that this value along with the"
            " optional UnitType value are entries in a list."
            " To accommodate this these values take an index value starting"
            " at 0 which can be used to generate this list of unit entries."
            " For Example, If two unit entires were required this could be"
            " achieved by setting the paramter UnitAmount(0)=1234 and"
            " UnitAmount(1)=5678."
            " Note that UnitAmount at index 0 is required when"
            " ChargeType=Unit, all other entries in the list are optional.")),
        (UnitType, (
            "Defines the type of unit."
            " ETSI AOC standard specifies this as an integer value between 1"
            " and 16, but this value is left open to accept any positive"
            " integer."
            " Like the UnitAmount parameter, this value represents a"
            " list entry and has an index parameter that starts at 0.")),
        (CurrencyName, (
            "Specifies the currency's name."
            " Note that this value is truncated after 10 characters.")),
        (CurrencyAmount, (
            "Specifies the charge unit amount as a positive integer."
            " This value is required when ChargeType==Currency.")),
        (CurrencyMultiplier, (
            "Specifies the currency multiplier."
            " This value is required when ChargeType==Currency.")),
        (TotalType, "Defines what kind of AOC-D total is represented."),
        (AOCBillingId, (
            "Represents a billing ID associated with an AOC-D or AOC-E"
            " message."
            " Note that only the first 3 items of the enum are valid AOC-D"
            " billing IDs")),
        (ChargingAssociationId, (
            "Charging association identifier."
            " This is optional for AOC-E and can be set to any value between"
            " -32768 and 32767")),
        (ChargingAssociationNumber, (
            "Represents the charging association party number."
            " This value is optional for AOC-E.")),
        (ChargingAssociationPlan, (
            "Integer representing the charging plan associated with the"
            " ChargingAssociationNumber."
            " The value is bits 7 through 1 of the Q.931 octet containing the"
            " type-of-number and numbering-plan-identification fields."))]
    name = 'AOCMessage'
    summary = "Generate an Advice of Charge message on a channel."


class Atxfer(Manager_Action):
    keys = [
        ActionID,
        (Channel, "Transferer's channel."),
        (Exten, "Extension to transfer to."),
        (Context, "Context to transfer to."),
        (Priority, "Priority to transfer to.")]
    name = 'Atxfer'
    summary = "Attended transfer."


class Bridge(Manager_Action):
    description = "Bridge together two channels already in the PBX."
    keys = [
        ActionID,
        (Channel1, "Channel to Bridge to Channel2."),
        (Channel2, "Channel to Bridge to Channel1."),
        (Tone, "Play courtesy tone to Channel 2.")]
    name = 'Bridge'
    summary = "Bridge two channels already in the PBX."


class Challenge(Manager_Action):
    description = "Generate a challenge for MD5 authentication."
    keys = [
        ActionID,
        (AuthType, (
            "Digest algorithm to use in the challenge. Valid values are:"))]
    name = 'Challenge'
    summary = "Generate Challenge for MD5 Auth."


class ChangeMonitor(Manager_Action):
    description = (
        "This action may be used to change the file started by a previous"
        " 'Monitor' action.")
    keys = [
        ActionID,
        (Channel, "Used to specify the channel to record."),
        (File, (
            "Is the new name of the file created in the monitor"
            " spool directory."))]
    name = 'ChangeMonitor'
    summary = "Change monitoring filename of a channel."


class Command(Manager_Action):
    description = "Run a CLI command."
    keys = [
        ActionID,
        (Command_, "Asterisk CLI command to run.")]
    name = 'Command'
    summary = "Execute Asterisk CLI Command."


class CoreSettings(Manager_Action):
    description = "Query for Core PBX settings."
    keys = [ActionID]
    name = 'CoreSettings'
    summary = "Show PBX core settings (version etc)."


class CoreShowChannels(Manager_Action):
    description = ("List currently defined channels and some information"
                   " about them.")
    keys = [ActionID]
    name = 'CoreShowChannels'
    summary = "List currently active channels."


class CoreStatus(Manager_Action):
    description = "Query for Core PBX status."
    keys = [ActionID]
    name = 'CoreStatus'
    summary = "Show PBX core status variables."


class CreateConfig(Manager_Action):
    description = ("This action will create an empty file in the"
                   " configuration directory."
                   " This action is intended to be used before an"
                   " UpdateConfig action.")
    keys = [
        ActionID,
        (Filename, "The configuration filename to create (e.g. foo.conf).")]
    name = 'CreateConfig'
    summary = "Creates an empty file in the configuration directory."


class DAHDIDialOffhook(Manager_Action):
    description = "Generate DTMF control frames to the bridged peer."
    keys = [
        ActionID,
        (DAHDIChannel, "DAHDI channel number to dial digits."),
        (Number, "Digits to dial.")]
    name = 'DAHDIDialOffhook'
    summary = "Dial over DAHDI channel while offhook."


class DAHDIDNDoff(Manager_Action):
    description = (
        "Equivalent to the CLI command \"dahdi set dnd channel off\".\n"
        "\n"
        "Note: Feature only supported by analog channels.")
    keys = [
        ActionID,
        (DAHDIChannel, "DAHDI channel number to set DND off.")]
    name = 'DAHDIDNDoff'
    summary = "Toggle DAHDI channel Do Not Disturb status OFF."


class DAHDIDNDon(Manager_Action):
    description = (
        "Equivalent to the CLI command \"dahdi set dnd channel on\".\n"
        "\n"
        "Note: Feature only supported by analog channels.")
    keys = [
        ActionID,
        (DAHDIChannel, "DAHDI channel number to set DND on.")]
    name = 'DAHDIDNDon'
    summary = "Toggle DAHDI channel Do Not Disturb status ON."


class DAHDIHangup(Manager_Action):
    description = (
        "Simulate an on-hook event by the user connected to the channel.\n"
        "\n"
        "Note: Valid only for analog channels.")
    keys = [
        ActionID,
        (DAHDIChannel, "DAHDI channel number to hangup.")]
    name = 'DAHDIHangup'
    summary = "Hangup DAHDI Channel."


class DAHDIRestart(Manager_Action):
    description = "Equivalent to the CLI command \"dahdi restart\"."
    keys = [ActionID]
    name = 'DAHDIRestart'
    summary = "Fully Restart DAHDI channels (terminates calls)."


class DAHDIShowChannels(Manager_Action):
    description = "Similar to the CLI command \"dahdi show channels\"."
    keys = [
        ActionID,
        (DAHDIChannel, (
            "Specify the specific channel number to show."
            " Show all channels if zero or not present."))]
    name = 'DAHDIShowChannels'
    summary = "Show status of DAHDI channels."


class DAHDITransfer(Manager_Action):
    description = (
        "Simulate a flash hook event by the user connected to the channel.\n"
        "\n"
        "Note: Valid only for analog channels.")
    keys = [
        ActionID,
        (DAHDIChannel, "DAHDI channel number to transfer.")]
    name = 'DAHDITransfer'
    summary = "Transfer DAHDI Channel."


class DataGet(Manager_Action):
    keys = [ActionID, Path, Search, Filter]
    name = 'DataGet'
    summary = "Retrieve the data api tree."


class DBDel(Manager_Action):
    keys = [ActionID, Family, Key]
    name = 'DBDel'
    summary = "Delete DB entry."


class DBDelTree(Manager_Action):
    keys = [ActionID, Family, Key]
    name = 'DBDelTree'
    summary = "Delete DB Tree."


class DBGet(Manager_Action):
    keys = [ActionID, Family, Key]
    name = 'DBGet'
    summary = "Get DB Entry."


class DBPut(Manager_Action):
    keys = [ActionID, Family, Key, Val]
    name = 'DBPut'
    summary = "Put DB entry."


class Events(Manager_Action):
    description = "Enable/Disable sending of events to this manager client."
    keys = [
        ActionID,
        (EventMask, (
            "on - If all events should be sent.\n"
            "off - If no events should be sent.\n"
            "system,call,log,... - To select which flags events should have"
            " to be sent."))]
    name = 'Events'
    summary = "Control Event Flow."


class ExtensionState(Manager_Action):
    description = (
        "Report the extension state for given extension."
        " If the extension has a hint, will use devicestate to check the"
        " status of the device connected to the extension.\n"
        "\n"
        "Will return an Extension Status message."
        " The response will include the hint for the extension and"
        " the status.")
    keys = [
        ActionID,
        (Exten, "Extension to check state on."),
        (Context, "Context for extension.")]
    name = 'ExtensionState'
    summary = "Check Extension Status."


class GetConfig(Manager_Action):
    description = (
        "This action will dump the contents of a configuration file by"
        " category and contents or optionally by specified category only.")
    keys = [
        ActionID,
        (Filename, "Configuration filename (e.g. foo.conf)."),
        (Category, "Category in configuration file.")]
    name = 'GetConfig'
    summary = "Retrieve configuration."


class GetConfigJSON(Manager_Action):
    description = (
        "This action will dump the contents of a configuration file by"
        " category and contents in JSON format."
        " This only makes sense to be used using rawman over"
        " the HTTP interface.")
    keys = [
        ActionID,
        (Filename, "Configuration filename (e.g. foo.conf).")]
    name = 'GetConfigJSON'
    summary = "Retrieve configuration (JSON format)."


class Getvar(Manager_Action):
    description = (
        "Get the value of a global or local channel variable.\n"
        "\n"
        "Note: If a channel name is not provided then the variable is global.")
    keys = [
        ActionID,
        (Channel, "Channel to read variable from."),
        (Variable, "Variable name.")]
    name = 'Getvar'
    summary = "Gets a channel variable."


class Hangup(Manager_Action):
    description = "Hangup a channel."
    keys = [
        ActionID,
        (Channel, "The channel name to be hangup."),
        (Cause, "Numeric hangup cause.")]
    name = 'Hangup'
    summary = "Hangup channel."


class IAXnetstats(Manager_Action):
    description = "Show IAX channels network statistics."
    keys = ()
    name = 'IAXnetstats'
    summary = "Show IAX Netstats."


class IAXpeerlist(Manager_Action):
    description = "List all the IAX peers."
    keys = [ActionID]
    name = 'IAXpeerlist'
    summary = "List IAX Peers."


class IAXpeers(Manager_Action):
    keys = [ActionID]
    name = 'IAXpeers'
    summary = "List IAX peers."


class IAXregistry(Manager_Action):
    keys = [ActionID]
    name = 'IAXregistry'
    summary = "Show IAX registrations."


class JabberSend(Manager_Action):
    keys = [
        ActionID,
        (Jabber, "Client or transport Asterisk uses to connect to JABBER."),
        (JID, "XMPP/Jabber JID (Name) of recipient."),
        (Message, "Message to be sent to the buddy.")]
    name = 'JabberSend'
    summary = "Sends a message to a Jabber Client."


class ListCategories(Manager_Action):
    description = "This action will dump the categories in a given file."
    keys = [
        ActionID,
        (Filename, "Configuration filename (e.g. foo.conf).")]
    name = 'ListCategories'
    summary = "List categories in configuration file."


class ListCommands(Manager_Action):
    description = (
        "Returns the action name and synopsis for every action that is"
        " available to the user.")
    keys = [ActionID]
    name = 'ListCommands'
    summary = "List available manager commands."


class LocalOptimizeAway(Manager_Action):
    description = ("A local channel created with \"/n\" will not"
                   " automatically optimize away."
                   " Calling this command on the local channel will clear"
                   " that flag and allow it to optimize away if it's bridged"
                   " or when it becomes bridged.")
    keys = [
        ActionID,
        (Channel, "The channel name to optimize away.")]
    name = 'LocalOptimizeAway'
    summary = "Optimize away a local channel when possible."


class Login(Manager_Action):
    keys = [
        ActionID,
        (Username, "Username to login with as specified in manager.conf."),
        (Secret, "Secret to login with as specified in manager.conf.")]
    name = 'Login'
    summary = "Login Manager."


class Logoff(Manager_Action):
    description = "Logoff the current manager session."
    keys = [ActionID]
    name = 'Logoff'
    summary = "Logoff Manager."


class MailboxCount(Manager_Action):
    description = (
        "Checks a voicemail account for new messages.\n"
        "\n"
        "Returns number of urgent, new and old messages.\n"
        "\n"
        "Message: Mailbox Message Count\n"
        "Mailbox: mailboxid\n"
        "UrgentMessages: count\n"
        "NewMessages: count\n"
        "OldMessages: count\n")
    keys = [
        ActionID,
        (Mailbox, "Full mailbox ID mailbox@vm-context.")]
    name = 'MailboxCount'
    summary = "Check Mailbox Message Count."


class MailboxStatus(Manager_Action):
    description = (
        "Checks a voicemail account for status.\n"
        "\n"
        "Returns number of messages."
        "\n"
        "Message: Mailbox Status.\n"
        "Mailbox: mailboxid.\n"
        "Waiting: count.\n")
    keys = [
        ActionID,
        (Mailbox, "Full mailbox ID mailbox@vm-context.")]
    name = 'MailboxStatus'
    summary = "Check mailbox."


class MeetmeList(Manager_Action):
    description = (
        "Lists all users in a particular MeetMe conference."
        " MeetmeList will follow as separate events, followed by a final"
        " event called MeetmeListComplete.")
    keys = [
        ActionID,
        (Conference, "Conference number.")]
    name = 'MeetmeList'
    summary = "List participants in a conference."


class MeetmeMute(Manager_Action):
    keys = [ActionID, Meetme, Usernum]
    name = 'MeetmeMute'
    summary = "Mute a Meetme user."


class MeetmeUnmute(Manager_Action):
    keys = [ActionID, Meetme, Usernum]
    name = 'MeetmeUnmute'
    summary = "Unmute a Meetme user."


class MixMonitorMute(Manager_Action):
    description = "This action may be used to mute a MixMonitor recording."
    keys = [
        ActionID,
        (Channel, "Used to specify the channel to mute."),
        (Direction, (
            "Which part of the recording to mute: read, write or both"
            " (from channel, to channel or both channels).")),
        (State, "Turn mute on or off : 1 to turn on, 0 to turn off.")]
    name = 'MixMonitorMute'
    summary = "Mute / unMute a Mixmonitor recording."


class ModuleCheck(Manager_Action):
    description = (
        "Checks if Asterisk module is loaded."
        " Will return Success/Failure. For success returns,"
        " the module revision number is included.")
    keys = [
        (Module, "Asterisk module name (not including extension).")]
    name = 'ModuleCheck'
    summary = "Check if module is loaded."


class ModuleLoad(Manager_Action):
    description = (
        "Loads, unloads or reloads an Asterisk module in a running system.")
    keys = [
        ActionID,
        (Module, (
            "Asterisk module name (including .so extension) or subsystem"
            " identifier.")),
        (LoadType, (
            "The operation to be done on module."
            " If no module is specified for a reload loadtype,"
            " all modules are reloaded."))]
    name = 'ModuleLoad'
    summary = "Module management."


class Monitor(Manager_Action):
    description = (
        "This action may be used to record the audio on a specified channel.")
    keys = [
        ActionID,
        (Channel, "Used to specify the channel to record."),
        (File, (
            "Is the name of the file created in the monitor spool directory."
            " Defaults to the same name as the channel"
            " (with slashes replaced with dashes).")),
        (Format, "Is the audio recording format. Defaults to wav."),
        (Mix, (
            "Boolean parameter as to whether to mix the input and output"
            " channels together after the recording is finished."))]
    name = 'Monitor'
    summary = "Monitor a channel."


class Originate(Manager_Action):
    description = (
        "Generates an outgoing call to a Extension/Context/Priority"
        " or Application/Data")
    keys = [
        ActionID,
        (Channel, "Channel name to call."),
        (Exten, "Extension to use (requires Context and Priority)"),
        (Context, "Context to use (requires Exten and Priority)"),
        (Priority, "Priority to use (requires Exten and Context)"),
        (Application, "Application to execute."),
        (Data, "Data to use (requires Application)."),
        (Timeout, "How long to wait for call to be answered (in ms.)."),
        (CallerID, "Caller ID to be set on the outgoing channel."),
        (Variable, (
            "Channel variable to set, multiple Variable:"
            " headers are allowed.")),
        (Account, "Account code."),
        (Async, "Set to true for fast origination."),
        (Codecs, "Comma-separated list of codecs to use for this call.")]
    name = 'Originate'
    summary = "Originate a call."


class Park(Manager_Action):
    keys = [
        ActionID,
        (Channel, "Channel name to park."),
        (Channel2, "Channel to return to if timeout."),
        (Timeout, "Number of milliseconds to wait before callback."),
        (Parkinglot, "Specify in which parking lot to park the channel.")]
    name = 'Park'
    summary = "Park a channel."


class ParkedCalls(Manager_Action):
    keys = [ActionID]
    name = 'ParkedCalls'
    summary = "List parked calls."


class PauseMonitor(Manager_Action):
    description = (
        "This action may be used to temporarily stop the recording"
        " of a channel.")
    keys = [
        ActionID,
        (Channel, "Used to specify the channel to record.")]
    name = 'PauseMonitor'
    summary = "Pause monitoring of a channel."


class Ping(Manager_Action):
    description = ("A 'Ping' action will ellicit a 'Pong' response."
                   " Used to keep the manager connection open.")
    keys = [ActionID]
    name = 'Ping'
    summary = "Keepalive command."


class PlayDTMF(Manager_Action):
    description = "Plays a dtmf digit on the specified channel."
    keys = [
        ActionID,
        (Channel, "Channel name to send digit to."),
        (Digit, "The DTMF digit to play.")]
    name = 'PlayDTMF'
    summary = "Play DTMF signal on a specific channel."


class QueueAdd(Manager_Action):
    keys = [ActionID, Queue, Interface, Penalty, Paused, MemberName,
            StateInterface]
    name = 'QueueAdd'
    summary = "Add interface to queue."


class QueueLog(Manager_Action):
    keys = [ActionID, Queue, Event, Uniqueid, Interface, Message]
    name = 'QueueLog'
    summary = "Adds custom entry in queue_log."


class QueuePause(Manager_Action):
    keys = [ActionID, Interface, Paused, Queue, Reason]
    name = 'QueuePause'
    summary = "Makes a queue member temporarily unavailable."


class QueuePenalty(Manager_Action):
    keys = [ActionID, Interface, Penalty, Queue]
    name = 'QueuePenalty'
    summary = "Set the penalty for a queue member."


class QueueReload(Manager_Action):
    keys = [ActionID, Queue, Members, Rules, Parameters]
    name = 'QueueReload'
    summary = (
        "Reload a queue, queues, or any sub-section of a queue or queues.")


class QueueRemove(Manager_Action):
    keys = [ActionID, Queue, Interface]
    name = 'QueueRemove'
    summary = "Remove interface from queue."


class QueueReset(Manager_Action):
    keys = [ActionID, Queue]
    name = 'QueueReset'
    summary = "Reset queue statistics."


class QueueRule(Manager_Action):
    keys = [ActionID, Rule]
    name = 'QueueRule'
    summary = "Queue Rules."


class Queues(Manager_Action):
    keys = ()
    name = 'Queues'
    summary = "Queues."
    # FIXME: May reply "No queues.", which is not an AMI message!


class QueueStatus(Manager_Action):
    keys = [ActionID, Queue, Member]
    name = 'QueueStatus'
    summary = "Show queue status."


class QueueSummary(Manager_Action):
    keys = [ActionID, Queue]
    name = 'QueueSummary'
    summary = "Show queue summary."


class Redirect(Manager_Action):
    keys = [
        ActionID,
        (Channel, "Channel to redirect."),
        (ExtraChannel, "Second call leg to transfer (optional)."),
        (Exten, "Extension to transfer to."),
        (ExtraExten, "Extension to transfer extrachannel to (optional)."),
        (Context, "Context to transfer to."),
        (ExtraContext, "Context to transfer extrachannel to (optional)."),
        (Priority, "Priority to transfer to."),
        (ExtraPriority, "Priority to transfer extrachannel to (optional).")]
    name = 'Redirect'
    summary = "Redirect (transfer) a call."


class Reload(Manager_Action):
    keys = [
        ActionID,
        (Module, "Name of the module to reload.")]
    name = 'Reload'
    summary = "Send a reload event."


class SendText(Manager_Action):
    description = "Sends A Text Message to a channel while in a call."
    keys = [
        ActionID,
        (Channel, "Channel to send message to."),
        (Message, "Message to send.")]
    name = 'SendText'
    summary = "Send text message to channel."


class Setvar(Manager_Action):
    description = (
        "Set a global or local channel variable.\n"
        "\n"
        "Note: If a channel name is not provided then the variable is global.")
    keys = [
        ActionID,
        (Channel, "Channel to set variable for."),
        (Variable, "Variable name."),
        (Value, "Variable value.")]
    name = 'Setvar'
    summary = "Set a channel variable."


class ShowDialPlan(Manager_Action):
    description = (
        "Show dialplan contexts and extensions."
        " Be aware that showing the full dialplan may take a lot of capacity.")
    keys = [
        ActionID,
        (Extension, "Show a specific extension."),
        (Context, "Show a specific context.")]
    name = 'ShowDialPlan'
    summary = "Show dialplan contexts and extensions"


class SIPnotify(Manager_Action):
    description = (
        "Sends a SIP Notify event.\n"
        "\n"
        "All parameters for this event must be specified in the body of this"
        " request via multiple Variable: name=value sequences.")
    keys = [
        ActionID,
        (Channel, "Peer to receive the notify."),
        (Variable, "At least one variable pair must be specified. name=value")]
    name = 'SIPnotify'
    summary = "Send a SIP notify."


class SIPpeers(Manager_Action):
    description = (
        "Lists SIP peers in text format with details on current status."
        " Peerlist will follow as separate events, followed by a final event"
        " called PeerlistComplete.")
    keys = [ActionID]
    name = 'SIPpeers'
    summary = "List SIP peers (text format)."


class SIPqualifypeer(Manager_Action):
    description = "Qualify a SIP peer."
    keys = [
        ActionID,
        (Peer, "The peer name you want to qualify.")]
    name = 'SIPqualifypeer'
    summary = "Qualify SIP peers."


class SIPshowpeer(Manager_Action):
    description = "Show one SIP peer with details on current status."
    keys = [
        ActionID,
        (Peer, "The peer name you want to check.")]
    name = 'SIPshowpeer'
    summary = "show SIP peer (text format)."


class SIPshowregistry(Manager_Action):
    description = (
        "Lists all registration requests and status."
        " Registrations will follow as separate events. followed by a final"
        " event called RegistrationsComplete.")
    keys = [ActionID]
    name = 'SIPshowregistry'
    summary = "Show SIP registrations (text format)."


class SKINNYdevices(Manager_Action):
    description = (
        "Lists Skinny devices in text format with details on current status."
        " Devicelist will follow as separate events, followed by a final event"
        " called DevicelistComplete.")
    keys = [ActionID]
    name = 'SKINNYdevices'
    summary = "List SKINNY devices (text format)."


class SKINNYlines(Manager_Action):
    description = ("Lists Skinny lines in text format with details on"
                   " current status."
                   " Linelist will follow as separate events, followed by a"
                   " final event called LinelistComplete.")
    keys = [ActionID]
    name = 'SKINNYlines'
    summary = "List SKINNY lines (text format)."


class SKINNYshowdevice(Manager_Action):
    description = "Show one SKINNY device with details on current status."
    keys = [
        ActionID,
        (Device, "The device name you want to check.")]
    name = 'SKINNYshowdevice'
    summary = "Show SKINNY device (text format)."


class SKINNYshowline(Manager_Action):
    description = "Show one SKINNY line with details on current status."
    keys = [
        ActionID,
        (Line, "The line name you want to check.")]
    name = 'SKINNYshowline'
    summary = "Show SKINNY line (text format)."


class Status(Manager_Action):
    description = ("Will return the status information of each channel along"
                   " with the value for the specified channel variables.")
    keys = [
        ActionID,
        (Channel, "The name of the channel to query for status."),
        (Variables, "Comma , separated list of variable to include.")]
    name = 'Status'
    summary = "List channel status."


class StopMonitor(Manager_Action):
    description = (
        "This action may be used to end a previously started"
        " 'Monitor' action.")
    keys = [
        ActionID,
        (Channel, "The name of the channel monitored.")]
    name = 'StopMonitor'
    summary = "Stop monitoring a channel."


class UnpauseMonitor(Manager_Action):
    description = (
        "This action may be used to re-enable recording of a channel after"
        " calling PauseMonitor.")
    keys = [
        ActionID,
        (Channel, "Used to specify the channel to record.")]
    name = 'UnpauseMonitor'
    summary = "Unpause monitoring of a channel."


class UpdateConfig(Manager_Action):
    description = (
        "This action will modify, create, or delete configuration elements"
        " in Asterisk configuration files.")
    keys = [
        ActionID,
        (SrcFilename, "Configuration filename to read (e.g. foo.conf)."),
        (DstFilename, "Configuration filename to write (e.g. foo.conf)"),
        (Reload_, (
            "Whether or not a reload should take place"
            " (or name of specific module).")),
        (Action_, (
            "Action to take."
            " X's represent 6 digit number beginning with 000000.")),
        (Cat, (
            "Category to operate on."
            " X's represent 6 digit number beginning with 000000.")),
        (Var, (
            "Variable to work on."
            " X's represent 6 digit number beginning with 000000.")),
        (Value_, (
            "Value to work on."
            " X's represent 6 digit number beginning with 000000.")),
        (Match, (
            "Extra match required to match line."
            " X's represent 6 digit number beginning with 000000.")),
        (Line_, (
            "Line in category to operate on"
            " (used with delete and insert actions).",
            " X's represent 6 digit number beginning with 000000."))]
    name = 'UpdateConfig'
    summary = "Update basic configuration."


class UserEvent(Manager_Action):
    description = "Send an event to manager sessions."
    keys = [
        ActionID,
        (UserEvent_, "Event string to send."),
        (Header, "Content1.")]
    name = 'UserEvent'
    summary = "Send an arbitrary event."


class VoicemailUsersList(Manager_Action):
    keys = [ActionID]
    name = 'VoicemailUsersList'
    summary = "List All Voicemail User Information."


class WaitEvent(Manager_Action):
    description = (
        "This action will ellicit a Success response."
        " Whenever a manager event is queued."
        " Once WaitEvent has been called on an HTTP manager session,"
        " events will be generated and queued.")
    keys = [
        ActionID,
        (Timeout, (
            "Maximum time (in seconds) to wait for events,"
            " -1 means forever."))]
    name = 'WaitEvent'
    summary = "Wait for an event to occur."


def introspect():
    for value in Manager_Action.__subclasses__():
        manager_actions[value.__name__] = value
    abstracts = Manager_Key, Manager_Key1, Manager_Key6, Manager_KeyPar
    for abstract in abstracts:
        for value in abstract.__subclasses__():
            if value not in abstracts:
                manager_keys[value.__name__] = value

introspect()
