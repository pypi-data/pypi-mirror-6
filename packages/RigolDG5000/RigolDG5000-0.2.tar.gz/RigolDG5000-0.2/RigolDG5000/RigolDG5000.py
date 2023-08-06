# -*- coding: utf-8 -*-
from VISA_wrapper_metaclass import *

IndexedGroup.var = '<n>'
        
class Generic(object):
    def __init__(self, inst, verbose=False):
        self._verbose = verbose
        self._inst = inst
    def write(self, cmd):
        if self._verbose : 
            print "Write command %s"%cmd
        self._inst.write(cmd)
    def ask(self, cmd):
        if self._verbose : 
            print "Ask command %s ..."%cmd,
        out = self._inst.ask(cmd)
        if self._verbose : 
            print "recieve %s"%out
        return out

class TestValuePercent(TestValue):
    "Test if a value is a precentage"
    def __init__(self):
        self.minimum = 0
        self.maximum = 100
    def condition(self, value):
        return isinstance(value, numbers.Number) and value>=self.minimum and value<=self.maximum
    def to_string(self, value):
        return str(value)+"%"
    def from_string(self, value):
        return TestValue.from_string(self, value[:-1])
    def __repr__(self):
        return 'percentage between %s and %s'%(self.minimum, self.maximum)

name_to_type = {'brightness':TestValuePercent(), "name":str, "ohms":TestValueBoundNumber(1,10000)} 

class Argument(Argument):
    def create_list_test_value(self):
        list_test_value = []
        for elm in self.list_value:
            if isinstance(elm, str) and elm.startswith('<'):
                for name,val in name_to_type.iteritems():
                    if name in elm:
                         list_test_value.append(val)
                         break
                else:
                    list_test_value.append(numbers.Number)
            else:
                list_test_value.append(elm)  
        return list_test_value 
        

        



class CouplingPhase(Group):
    __metaclass__ = InstrumentMetaclass
    class deviation(GenericGetSetCommandClass):
        """Set the phase deviation of phase coupling and the default unit is "°".
        The query returns the phase deviation value in scientific notation."""
        cmd = ':COUPling:PHASe:DEViation'
        full_acces = 'coupling.phase.deviation'
        deviation=Argument(0,["<deviation>"])
    

class CouplingFrequency(Group):
    __metaclass__ = InstrumentMetaclass
    class deviation(GenericGetSetCommandClass):
        """Set the frequency deviation of frequency coupling and the default unit is "Hz".
        The query returns the frequency deviation value in scientific notation."""
        cmd = ':COUPling:FREQuency:DEViation'
        full_acces = 'coupling.frequency.deviation'
        deviation=Argument(0,["<deviation>"])
    

class CouplingChannel(Group):
    __metaclass__ = InstrumentMetaclass
    class base(GenericGetSetCommandClass):
        """Set the coupling base channel as CH1 or CH2.
        The query returns CH1 or CH2."""
        cmd = ':COUPling:CHannel:BASE'
        full_acces = 'coupling.channel.base'
        __value=Argument(0,["CH1","CH2"])
    

class Coupling(Group):
    __metaclass__ = InstrumentMetaclass
    phase=CouplingPhase
    frequency=CouplingFrequency
    channel=CouplingChannel
    class state(GenericGetSetCommandClass):
        """Turn the channel coupling function on or off.
        The query returns ON or OFF."""
        cmd = ':COUPling:STATe'
        full_acces = 'coupling.state'
        __value=Argument(0,["ON","OFF"])
    
    class type(GenericGetSetCommandClass):
        """Select the coupling type: Frequency Deviation or Phase Deviation.
        The query returns PHASE or FREQ."""
        cmd = ':COUPling:TYPE'
        full_acces = 'coupling.type'
        __value=Argument(0,["PHASE","FREQ"])
    

class TraceDataPoints(Group):
    __metaclass__ = InstrumentMetaclass
    class val(GenericGetSetCommandClass):
        """Set the number of the initial points.
        Query the number of the initial points of the edited waveform."""
        cmd = ':TRACe:DATA:POINts'
        full_acces = 'trace.data.points.val'
        __value=Argument(0,["VOLATILE"])
        value=Argument(1,["<value>","MINimum","MAXimum"])
    
    class interpolate(GenericGetSetCommandClass):
        """Set the interpolation mode between the defined points of the waveform.
        The query returns LINEAR, SINC or OFF.
        """
        cmd = ':TRACe:DATA:POINts:INTerpolate'
        full_acces = 'trace.data.points.interpolate'
        __value=Argument(0,["LINear","SINC","OFF"])
    

class TraceData(Group):
    __metaclass__ = InstrumentMetaclass
    points=TraceDataPoints
    class load(GenericGetCommandClass):
        """Query the number of arbitrary waveform data packets in the volatile memory.
        Read the specified data packet in the volatile memory."""
        cmd = ':TRACe:DATA:LOAD'
        full_acces = 'trace.data.load'
    
    class dac16(GenericSetCommandClass):
        """Download the waveform edited into the DDRII."""
        cmd = ':TRACe:DATA:DAC16'
        full_acces = 'trace.data.dac16'
        __value=Argument(0,["VOLATILE"])
        flag=Argument(1,["<flag>"])
        binary_block_data=Argument(2,["<binary_block_data>"])
    
    class dac(GenericSetCommandClass):
        """Send binary data block or decimal DAC value to the volatile memory."""
        cmd = ':TRACe:DATA:DAC'
        full_acces = 'trace.data.dac'
        __value=Argument(0,["VOLATILE"])
        binary_block_data=Argument(1,["<binary_block_data>","<value>"])
        value=Argument(2,["<value>"])
        value=Argument(3,["<value>"])
    
    class value(GenericGetCommandClass):
        """Query the decimal integer value of a certain point in the volatile memory.
        The query returns a decimal value and the range is from 0 to 16383."""
        cmd = ':TRACe:DATA:VALue'
        full_acces = 'trace.data.value'
    
    class data(GenericSetCommandClass):
        """Download floating point voltage value into the volatile memory. The range of the number of the floating points is from -1 to +1 and the data length can not exceed 512 kpts."""
        cmd = ':TRACe:DATA:DATA'
        full_acces = 'trace.data.data'
        __value=Argument(0,["VOLATILE"])
        value1=Argument(1,["<value1>"])
        value2=Argument(2,["<value2>"])
    

class Trace(Group):
    __metaclass__ = InstrumentMetaclass
    data=TraceData

class SystemKlock(Group):
    __metaclass__ = InstrumentMetaclass
    class state(GenericGetSetCommandClass):
        """Lock or unlock the front panel remotely.
        The query returns ON or OFF."""
        cmd = ':SYSTem:KLOCk:STATe'
        full_acces = 'system.klock.state'
        __value=Argument(0,["ON","OFF"])
    

class SystemCommunicateLanAutoip(Group):
    __metaclass__ = InstrumentMetaclass
    class state(GenericGetSetCommandClass):
        """Turn the AutoIP mode on/off.
        The query returns ON or OFF."""
        cmd = ':SYSTem:COMMunicate:LAN:AUTOip:STATe'
        full_acces = 'system.communicate.lan.autoip.state'
        __value=Argument(0,["ON","OFF"])
    

class SystemCommunicateLanStatic(Group):
    __metaclass__ = InstrumentMetaclass
    class state(GenericGetSetCommandClass):
        """Turn the ManualIP mode on/off.
        The query returns ON or OFF."""
        cmd = ':SYSTem:COMMunicate:LAN:STATic:STATe'
        full_acces = 'system.communicate.lan.static.state'
        __value=Argument(0,["ON","OFF"])
    

class SystemCommunicateLanDhcp(Group):
    __metaclass__ = InstrumentMetaclass
    class state(GenericGetSetCommandClass):
        """Turn the DHCP mode on/off.
        The query returns ON or OFF."""
        cmd = ':SYSTem:COMMunicate:LAN:DHCP:STATe'
        full_acces = 'system.communicate.lan.dhcp.state'
        __value=Argument(0,["ON","OFF"])
    

class SystemCommunicateLan(Group):
    __metaclass__ = InstrumentMetaclass
    autoip=SystemCommunicateLanAutoip
    static=SystemCommunicateLanStatic
    dhcp=SystemCommunicateLanDhcp
    class smask(GenericGetSetCommandClass):
        """Set the subnet mask for the signal generator.
        The query returns the subnet mask in nnn.nnn.nnn.nnn format."""
        cmd = ':SYSTem:COMMunicate:LAN:SMASk'
        full_acces = 'system.communicate.lan.smask'
        mask=Argument(0,["<mask>"])
    
    class hostname(GenericGetSetCommandClass):
        """Set the host name for the signal generator.
        The query returns the host name."""
        cmd = ':SYSTem:COMMunicate:LAN:HOSTname'
        full_acces = 'system.communicate.lan.hostname'
        name=Argument(0,["<name>"])
    
    class domain(GenericGetSetCommandClass):
        """Set the domain name for the signal generator.
        The query returns the domain name."""
        cmd = ':SYSTem:COMMunicate:LAN:DOMain'
        full_acces = 'system.communicate.lan.domain'
        name=Argument(0,["<name>"])
    
    class mac(GenericGetCommandClass):
        """Query and return the MAC address."""
        cmd = ':SYSTem:COMMunicate:LAN:MAC'
        full_acces = 'system.communicate.lan.mac'
    
    class dns(GenericGetSetCommandClass):
        """Set the DNS server address for the signal generator.
        The query returns the DNS server address in nnn.nnn.nnn.nnn format."""
        cmd = ':SYSTem:COMMunicate:LAN:DNS'
        full_acces = 'system.communicate.lan.dns'
        address=Argument(0,["<address>"])
    
    class ipaddress(GenericGetSetCommandClass):
        """Set the IP address for the signal generator.
        The query returns the IP address in nnn.nnn.nnn.nnn format."""
        cmd = ':SYSTem:COMMunicate:LAN:IPADdress'
        full_acces = 'system.communicate.lan.ipaddress'
        ip_addr=Argument(0,["<ip_addr>"])
    
    class gateway(GenericGetSetCommandClass):
        """Set the default gateway for the signal generator.
        The query returns the default gateway in nnn.nnn.nnn.nnn format."""
        cmd = ':SYSTem:COMMunicate:LAN:GATEway'
        full_acces = 'system.communicate.lan.gateway'
        address=Argument(0,["<address>"])
    

class SystemCommunicateGpibSelf(Group):
    __metaclass__ = InstrumentMetaclass
    class address(GenericGetSetCommandClass):
        """Set the GPIB address for the signal generator.
        The query returns the value from 0 to 30."""
        cmd = ':SYSTem:COMMunicate:GPIB:SELF:ADDRess'
        full_acces = 'system.communicate.gpib.self.address'
        integer=Argument(0,["<integer>"])
    

class SystemCommunicateGpib(Group):
    __metaclass__ = InstrumentMetaclass
    self=SystemCommunicateGpibSelf

class SystemCommunicateUsbSelf(Group):
    __metaclass__ = InstrumentMetaclass
    class class_(GenericGetSetCommandClass):
        """Select the device type to be connected to the instrument via the USB Device interface of the signal generator.
        The query returns COMP or PRIN."""
        cmd = ':SYSTem:COMMunicate:USB:SELF:CLASs'
        full_acces = 'system.communicate.usb.self.class_'
        __value=Argument(0,["COMPuter","PRINter"])
    

class SystemCommunicateUsb(Group):
    __metaclass__ = InstrumentMetaclass
    self=SystemCommunicateUsbSelf
    class information(GenericGetCommandClass):
        """Query the USB information."""
        cmd = ':SYSTem:COMMunicate:USB:INFormation'
        full_acces = 'system.communicate.usb.information'
    

class SystemCommunicate(Group):
    __metaclass__ = InstrumentMetaclass
    lan=SystemCommunicateLan
    gpib=SystemCommunicateGpib
    usb=SystemCommunicateUsb

class SystemRoscillator(Group):
    __metaclass__ = InstrumentMetaclass
    class source(GenericGetSetCommandClass):
        """Set the reference clock source type: Internal or External.
        The query returns INT or EXT."""
        cmd = ':SYSTem:ROSCillator:SOURce'
        full_acces = 'system.roscillator.source'
        __value=Argument(0,["INT","EXT"])
    

class SystemBeeper(Group):
    __metaclass__ = InstrumentMetaclass
    class state(GenericGetSetCommandClass):
        """Turn the beeper on or off.
        The query returns ON or OFF."""
        cmd = ':SYSTem:BEEPer:STATe'
        full_acces = 'system.beeper.state'
        __value=Argument(0,["ON","OFF"])
    
    class immediate(GenericCommandClass):
        """The beeper immediately generate a beep."""
        cmd = ':SYSTem:BEEPer:IMMediate'
        full_acces = 'system.beeper.immediate'
    

class System(Group):
    __metaclass__ = InstrumentMetaclass
    klock=SystemKlock
    communicate=SystemCommunicate
    roscillator=SystemRoscillator
    beeper=SystemBeeper
    class language(GenericGetSetCommandClass):
        """Set the system language type: English or Simplified Chinese.
        The query returns ENGL or SCH."""
        cmd = ':SYSTem:LANGuage'
        full_acces = 'system.language'
        __value=Argument(0,["ENGLish","SCHinese"])
    
    class cscopy(GenericSetCommandClass):
        """Copy the parameter configuration of CH1 (CH2) to CH2 (CH1)."""
        cmd = ':SYSTem:CSCopy'
        full_acces = 'system.cscopy'
        __value=Argument(0,["CH1,CH2","CH2,CH1"])
    
    class error(GenericGetCommandClass):
        """Query the error event queue."""
        cmd = ':SYSTem:ERRor'
        full_acces = 'system.error'
    
    class switch(GenericSetCommandClass):
        """Disable or enable the power key at the front panel."""
        cmd = ':SYSTem:SWItch'
        full_acces = 'system.switch'
        __value=Argument(0,["ON","OFF"])
    
    class version(GenericGetCommandClass):
        """Query and return SCPI version information."""
        cmd = ':SYSTem:VERSion'
        full_acces = 'system.version'
    
    class shutdown(GenericCommandClass):
        """Power-off"""
        cmd = ':SYSTem:SHUTDOWN'
        full_acces = 'system.shutdown'
    
    class poweron(GenericGetSetCommandClass):
        """Set the configuration to be used at power-on.
        The query returns DEFAULT or LAST."""
        cmd = ':SYSTem:POWeron'
        full_acces = 'system.poweron'
        __value=Argument(0,["DEFault","LASt"])
    
    class restart(GenericCommandClass):
        """Restart the instrument."""
        cmd = ':SYSTem:RESTART'
        full_acces = 'system.restart'
    

class OutputSync(Group):
    __metaclass__ = InstrumentMetaclass
    class polarity(GenericGetSetCommandClass):
        """Set the sync signal on the [Sync] connector to normal or invert.
        The query returns POS or NEG."""
        cmd = ':OUTPut<n>:SYNC:POLarity'
        full_acces = 'output.sync.polarity'
        __value=Argument(0,["POSitive","NEGative"])
    
    class state(GenericGetSetCommandClass):
        """Enable or disable the sync signal on the [Sync] connector.
        The query returns ON or OFF."""
        cmd = ':OUTPut<n>:SYNC:STATe'
        full_acces = 'output.sync.state'
        __value=Argument(0,["ON","OFF"])
    

class Output(IndexedGroup):
    __metaclass__ = InstrumentMetaclass
    sync=OutputSync
    class load(GenericGetSetCommandClass):
        """Set the output impedance of the [Output] connector at the front panel and the default unit is "Ω".
        The query returns the specific impedance value or INFINITY (High Z)."""
        cmd = ':OUTPut<n>:LOAD'
        full_acces = 'output.load'
        ohms=Argument(0,["<ohms>","INFinity","MINimum","MAXimum"])
    
    class polarity(GenericGetSetCommandClass):
        """Set the output polarity of the signal at the [Output] connector to normal or invert.
        The query returns NORMAL or INVERTED."""
        cmd = ':OUTPut<n>:POLarity'
        full_acces = 'output.polarity'
        __value=Argument(0,["NORMal","INVerted"])
    
    class attenuation(GenericGetSetCommandClass):
        """Set the attenuation (amplication) coefficient of the signal on the [Output] connector.
        The query returns 1X, 2X, 5X or 10X."""
        cmd = ':OUTPut<n>:ATTenuation'
        full_acces = 'output.attenuation'
        __value=Argument(0,["1X","2X","5X","10X"])
    
    class state(GenericGetSetCommandClass):
        """Enable or disable the output of the [Output] connector at the front panel corresponding to the channel.
        The query returns ON or OFF."""
        cmd = ':OUTPut<n>:STATe'
        full_acces = 'output.state'
        __value=Argument(0,["ON","OFF"])
    
    class impedance(GenericGetSetCommandClass):
        """Set the output impedance of the [Output] connector at the front panel and the default unit is "Ω".
        The query returns the specific impedance value or INFINITY (High Z)."""
        cmd = ':OUTPut<n>:IMPedance'
        full_acces = 'output.impedance'
        ohms=Argument(0,["<ohms>","INFinity","MINimum","MAXimum"])
    

class Mmemory(Group):
    __metaclass__ = InstrumentMetaclass
    class mdirectory(GenericSetCommandClass):
        """Create a folder under the current directory using the filename specified by<dir_name>."""
        cmd = ':MMEMory:MDIRectory'
        full_acces = 'mmemory.mdirectory'
        dir_name=Argument(0,["<dir_name>"])
    
    class load(GenericSetCommandClass):
        """Load the file specified by <file_name> under the current directory."""
        cmd = ':MMEMory:LOAD'
        full_acces = 'mmemory.load'
        file_name=Argument(0,["<file_name>"])
    
    class rdirectory(GenericGetCommandClass):
        """Query the disks currently available."""
        cmd = ':MMEMory:RDIRectory'
        full_acces = 'mmemory.rdirectory'
    
    class cdirectory(GenericGetSetCommandClass):
        """Change the current directory to the directory specified by <directory_name>.
        The query returns the current directory in character string."""
        cmd = ':MMEMory:CDIRectory'
        full_acces = 'mmemory.cdirectory'
        directory_name=Argument(0,["<directory_name>"])
    
    class catalog(GenericGetCommandClass):
        """Query all the files and folders under the current catalog."""
        cmd = ':MMEMory:CATalog'
        full_acces = 'mmemory.catalog'
    
    class copy(GenericSetCommandClass):
        """Copy the file specified by <file_name> under the current directory to the directory (not the current directory) specified by <directory_name>."""
        cmd = ':MMEMory:COPY'
        full_acces = 'mmemory.copy'
        directory_name=Argument(0,["<directory_name>"])
        file_name=Argument(1,["<file_name>"])
    
    class store(GenericSetCommandClass):
        """Store the file under the current directory with the filename specified by <file_name>."""
        cmd = ':MMEMory:STORe'
        full_acces = 'mmemory.store'
        file_name=Argument(0,["<file_name>"])
    
    class delete(GenericSetCommandClass):
        """Delete the file or folder specified by <file_name> under the current directory."""
        cmd = ':MMEMory:DELete'
        full_acces = 'mmemory.delete'
        file_name=Argument(0,["<file_name>"])
    

class SourceFunctionSquare(Group):
    __metaclass__ = InstrumentMetaclass
    class dcycle(GenericGetSetCommandClass):
        """Set the duty cycle of the square waveform, expressed in % and support settings without %.
        The query returns the duty cycle in scientific notation."""
        cmd = ':SOURce<n>:FUNCtion:SQUare:DCYCle'
        full_acces = 'source.function.square.dcycle'
        percent=Argument(0,["<percent>","MINimum","MAXimum"])
    

class SourceFunctionRamp(Group):
    __metaclass__ = InstrumentMetaclass
    class symmetry(GenericGetSetCommandClass):
        """Set the symmetry of the ramp waveform, expressed in % and support settings without %.
        The query returns the symmetry in scientific notation."""
        cmd = ':SOURce<n>:FUNCtion:RAMP:SYMMetry'
        full_acces = 'source.function.ramp.symmetry'
        symmetry=Argument(0,["<symmetry>","MINimum","MAXimum"])
    

class SourceFunctionArb(Group):
    __metaclass__ = InstrumentMetaclass
    class sample(GenericGetSetCommandClass):
        """Set the frequency division coefficient of the sample rate of the arbitrary waveform.
        The query returns integer coefficient value."""
        cmd = ':SOURce<n>:FUNCtion:ARB:SAMPLE'
        full_acces = 'source.function.arb.sample'
        samplediv=Argument(0,["<samplediv>","MINimum","MAXimum"])
    
    class mode(GenericGetSetCommandClass):
        """Select the output mode of the arbitrary waveform: "INTernal" (also called Normal) or "PLAY".
        The query returns INT or PLAY."""
        cmd = ':SOURce<n>:FUNCtion:ARB:MODE'
        full_acces = 'source.function.arb.mode'
        __value=Argument(0,["INTernal","PLAY"])
    

class SourceFunction(Group):
    __metaclass__ = InstrumentMetaclass
    square=SourceFunctionSquare
    ramp=SourceFunctionRamp
    arb=SourceFunctionArb
    class shape(GenericGetSetCommandClass):
        """Select waveform.
        The query returns SIN, SQU, RAMP, PULSE, NOISE, USER, DC, SINC, EXPR, EXPF, CARD, GAUS, HAV, LOR, ARBPULSE or DUA."""
        cmd = ':SOURce<n>:FUNCtion:SHAPe'
        full_acces = 'source.function.shape'
        __value=Argument(0,["SINusoid","SQUare","RAMP","PULSe","NOISe","USER","DC","SINC","EXPRise","EXPFall","CARDiac","GAUSsian"])
    

class SourceBurstTrigger(Group):
    __metaclass__ = InstrumentMetaclass
    class slope(GenericGetSetCommandClass):
        """Select to enable the burst output on the "Leading" or "Trailing" edge of the external trigger signal.
        The query returns POS or NEG."""
        cmd = ':SOURce<n>:BURSt:TRIGger:SLOPe'
        full_acces = 'source.burst.trigger.slope'
        __value=Argument(0,["POSitive","NEGative"])
    
    class source(GenericGetSetCommandClass):
        """Set the Burst trigger source type to Internal, External or Manual.
        The query returns INT, EXT or MAN."""
        cmd = ':SOURce<n>:BURSt:TRIGger:SOURce'
        full_acces = 'source.burst.trigger.source'
        __value=Argument(0,["INTernal","EXTernal","MANual"])
    
    class trigout(GenericGetSetCommandClass):
        """Specify the edge type of the trigger output signal.
        The query returns OFF, POS or NEG."""
        cmd = ':SOURce<n>:BURSt:TRIGger:TRIGOut'
        full_acces = 'source.burst.trigger.trigout'
        __value=Argument(0,["OFF","POSitive","NEGative"])
    
    class immediate(GenericCommandClass):
        """Trigger the instrument immediately."""
        cmd = ':SOURce<n>:BURSt:TRIGger:IMMediate'
        full_acces = 'source.burst.trigger.immediate'
    

class SourceBurstInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class period(GenericGetSetCommandClass):
        """Set the Burst period (the time from the beginning of the N Cycle burst to the beginning of the next burst) and the default unit is "s".
        The query returns the period value in scientific notation."""
        cmd = ':SOURce<n>:BURSt:INTernal:PERiod'
        full_acces = 'source.burst.internal.period'
        period=Argument(0,["<period>","MINimum","MAXimum"])
    

class SourceBurstGate(Group):
    __metaclass__ = InstrumentMetaclass
    class polarity(GenericGetSetCommandClass):
        """Output burst waveform when the gated signal on the [ExtTrig] connector at the rear panel is high level or low level.
        The query returns NORM or INV."""
        cmd = ':SOURce<n>:BURSt:GATE:POLarity'
        full_acces = 'source.burst.gate.polarity'
        __value=Argument(0,["NORMal","INVerted"])
    

class SourceBurst(Group):
    __metaclass__ = InstrumentMetaclass
    trigger=SourceBurstTrigger
    internal=SourceBurstInternal
    gate=SourceBurstGate
    class ncycles(GenericGetSetCommandClass):
        """Set the cycle number of the Burst.
        The query returns the value of the cycle number."""
        cmd = ':SOURce<n>:BURSt:NCYCles'
        full_acces = 'source.burst.ncycles'
        cycles=Argument(0,["<cycles>","MINimum","MAXimum"])
    
    class state(GenericGetSetCommandClass):
        """Enable or disable the Burst function.
        The query returns ON or OFF."""
        cmd = ':SOURce<n>:BURSt:STATe'
        full_acces = 'source.burst.state'
        __value=Argument(0,["ON","OFF"])
    
    class mode(GenericGetSetCommandClass):
        """Select the Burst type: N Cycle, Gated or Infinite.
        The query returns TRIG, GAT or INF."""
        cmd = ':SOURce<n>:BURSt:MODE'
        full_acces = 'source.burst.mode'
        __value=Argument(0,["TRIGgered","GATed","INFinity"])
    
    class phase(GenericGetSetCommandClass):
        """Set the start phase of the burst and the default unit is "°".
        The query returns the phase value in scientific notation."""
        cmd = ':SOURce<n>:BURSt:PHASe'
        full_acces = 'source.burst.phase'
        phase=Argument(0,["<phase>","MINimum","MAXimum"])
    
    class tdelay(GenericGetSetCommandClass):
        """Set the time that the signal generator holds from recieving a trigger signal to starting outputing the N Cycle (or Infinite) burst and the default unit is "s".
        The query returns the time value in scientific notation."""
        cmd = ':SOURce<n>:BURSt:TDELay'
        full_acces = 'source.burst.tdelay'
        delay=Argument(0,["<delay>","MINimum","MAXimum"])
    

class SourcePeriod(Group):
    __metaclass__ = InstrumentMetaclass
    class fixed(GenericGetSetCommandClass):
        """Set the basic waveform period and the default unit is "s".
        The query returns the period value in scientific notation."""
        cmd = ':SOURce<n>:PERiod:FIXed'
        full_acces = 'source.period.fixed'
        period=Argument(0,["<period>","MINimum","MAXimum"])
    

class SourcePulseTransition(Group):
    __metaclass__ = InstrumentMetaclass
    class leading(GenericGetSetCommandClass):
        """Set the rising edge of the pulse and the default unit is "s".
        The query returns the time value in scientific notation and the default unit is "s"."""
        cmd = ':SOURce<n>:PULSe:TRANsition:LEADing'
        full_acces = 'source.pulse.transition.leading'
        seconds=Argument(0,["<seconds>","MINimum","MAXimum"])
    
    class trailing(GenericGetSetCommandClass):
        """Set the falling edge of the pulse and the default unit is "s".
        The query returns the time value in scientific notation and the default unit is "s"."""
        cmd = ':SOURce<n>:PULSe:TRANsition:TRAiling'
        full_acces = 'source.pulse.transition.trailing'
        seconds=Argument(0,["<seconds>","MINimum","MAXimum"])
    

class SourcePulse(Group):
    __metaclass__ = InstrumentMetaclass
    transition=SourcePulseTransition
    class dcycle(GenericGetSetCommandClass):
        """Set the pulse duty cycle, expressed in %.
        The query returns the duty cycle value in scientific notation."""
        cmd = ':SOURce<n>:PULSe:DCYCle'
        full_acces = 'source.pulse.dcycle'
        percent=Argument(0,["<percent>","MINimum","MAXimum"])
    
    class delay(GenericGetSetCommandClass):
        """Set the delayed time of the pulse and the default unit is "s".
        The query returns the pulse delay in scientific notation."""
        cmd = ':SOURce<n>:PULSe:DELay'
        full_acces = 'source.pulse.delay'
        delay=Argument(0,["<delay>","MINimum","MAXimum"])
    
    class hold(GenericGetSetCommandClass):
        """Select to hold at the "Pulse Width" or "Duty Cycle" state.
        The query returns WIDT or DUTY."""
        cmd = ':SOURce<n>:PULSe:HOLD'
        full_acces = 'source.pulse.hold'
        __value=Argument(0,["WIDTh","DUTY"])
    
    class width(GenericGetSetCommandClass):
        """Set the pulse width (the time from the 50% threshold of a rising edge amplitude to the 50% threshold of the next falling edge amplitude) and the default unit is "s".
        The query returns the pulse width value in scientific notation."""
        cmd = ':SOURce<n>:PULSe:WIDTh'
        full_acces = 'source.pulse.width'
        seconds=Argument(0,["<seconds>","MINimum","MAXimum"])
    

class SourceSweepTrigger(Group):
    __metaclass__ = InstrumentMetaclass
    class slope(GenericGetSetCommandClass):
        """Select to enable the frequency sweep output on the "Leading" or "Trailing" edge of the external trigger signal."""
        cmd = ':SOURce<n>:SWEep:TRIGger:SLOPe'
        full_acces = 'source.sweep.trigger.slope'
        __value=Argument(0,["POSitive","NEGative"])
    
    class source(GenericGetSetCommandClass):
        """Select the sweep trigger source type.
        The query returns INT, EXT or MAN."""
        cmd = ':SOURce<n>:SWEep:TRIGger:SOURce'
        full_acces = 'source.sweep.trigger.source'
        __value=Argument(0,["INTernal","EXTernal","MANual"])
    
    class trigout(GenericGetSetCommandClass):
        """Set the output edge of the sweep trigger.
        The query returns OFF, POS or NEG."""
        cmd = ':SOURce<n>:SWEep:TRIGger:TRIGOut'
        full_acces = 'source.sweep.trigger.trigout'
        __value=Argument(0,["OFF","POSitive","NEGative"])
    
    class immediate(GenericCommandClass):
        """Trigger the instrument immediately."""
        cmd = ':SOURce<n>:SWEep:TRIGger:IMMediate'
        full_acces = 'source.sweep.trigger.immediate'
    

class SourceSweepHtime(Group):
    __metaclass__ = InstrumentMetaclass
    class start(GenericGetSetCommandClass):
        """Set the start hold time of the sweep and the default unit is "s".
        The query returns the time value in scientific notation."""
        cmd = ':SOURce<n>:SWEep:HTIMe:STARt'
        full_acces = 'source.sweep.htime.start'
        seconds=Argument(0,["<seconds>","MINimum","MAXimum"])
    
    class stop(GenericGetSetCommandClass):
        """Set the end hold time of the Sweep and the default unit is "s".
        The query returns the time value in scientific notation."""
        cmd = ':SOURce<n>:SWEep:HTIMe:STOP'
        full_acces = 'source.sweep.htime.stop'
        seconds=Argument(0,["<seconds>","MINimum","MAXimum"])
    

class SourceSweep(Group):
    __metaclass__ = InstrumentMetaclass
    trigger=SourceSweepTrigger
    htime=SourceSweepHtime
    class rtime(GenericGetSetCommandClass):
        """Set the return time of the Sweep and the defaut unit is "s".
        The query returns the time value in scientific notation."""
        cmd = ':SOURce<n>:SWEep:RTIMe'
        full_acces = 'source.sweep.rtime'
        seconds=Argument(0,["<seconds>","MINimum","MAXimum"])
    
    class spacing(GenericGetSetCommandClass):
        """Select the sweep type: Linear, Log or step.
        The query returns LIN, LOG or STE."""
        cmd = ':SOURce<n>:SWEep:SPACing'
        full_acces = 'source.sweep.spacing'
        __value=Argument(0,["LINear","LOGarithmic","STEp"])
    
    class step(GenericGetSetCommandClass):
        """Set the step number of step sweep.
        The query returns an integer."""
        cmd = ':SOURce<n>:SWEep:STEp'
        full_acces = 'source.sweep.step'
        steps=Argument(0,["<steps>","MINimum","MAXimum"])
    
    class state(GenericGetSetCommandClass):
        """Enable or disable the frequency sweep function.
        The query returns OFF or ON."""
        cmd = ':SOURce<n>:SWEep:STATe'
        full_acces = 'source.sweep.state'
        __value=Argument(0,["OFF","ON"])
    
    class time(GenericGetSetCommandClass):
        """Set the sweep time and the default unit is "s".
        The query returns the time value in scientific notation."""
        cmd = ':SOURce<n>:SWEep:TIME'
        full_acces = 'source.sweep.time'
        seconds=Argument(0,["<seconds>","MINimum","MAXimum"])
    

class SourcePhase(Group):
    __metaclass__ = InstrumentMetaclass
    class initiate(GenericCommandClass):
        """Execute align phase operation."""
        cmd = ':SOURce<n>:PHASe:INITiate'
        full_acces = 'source.phase.initiate'
    
    class adjust(GenericGetSetCommandClass):
        """Set the start phase of the basic waveform and the default unit is "°".
        The query returns the phase value in scientific notation."""
        cmd = ':SOURce<n>:PHASe:ADJust'
        full_acces = 'source.phase.adjust'
        phase=Argument(0,["<phase>","MINimum","MAXimum"])
    

class SourceFrequency(Group):
    __metaclass__ = InstrumentMetaclass
    class stop(GenericGetSetCommandClass):
        """Set the end frequency of the Sweep and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:FREQuency:STOP'
        full_acces = 'source.frequency.stop'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    
    class start(GenericGetSetCommandClass):
        """Set the start frequency of the Sweep and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:FREQuency:STARt'
        full_acces = 'source.frequency.start'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    
    class fixed(GenericGetSetCommandClass):
        """Set the frequency of the basic waveform and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:FREQuency:FIXed'
        full_acces = 'source.frequency.fixed'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    
    class span(GenericGetSetCommandClass):
        """Set the frequency span of the Sweep and the default unit is "Hz".
        The query returns the frequency span value in scientific notation."""
        cmd = ':SOURce<n>:FREQuency:SPAN'
        full_acces = 'source.frequency.span'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    
    class center(GenericGetSetCommandClass):
        """Set the center frequency of the Sweep and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:FREQuency:CENTer'
        full_acces = 'source.frequency.center'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    

class SourceVoltageRange(Group):
    __metaclass__ = InstrumentMetaclass
    class auto(GenericGetSetCommandClass):
        """Enable or disable the range hold.
        The query returns AUTO or HOLD."""
        cmd = ':SOURce<n>:VOLTage:RANGe:AUTO'
        full_acces = 'source.voltage.range.auto'
        __value=Argument(0,["OFF","ON"])
    

class SourceVoltageLevelImmediate(Group):
    __metaclass__ = InstrumentMetaclass
    class high(GenericGetSetCommandClass):
        """Set the high level of the basic waveform and the default unit is "V".
        The query returns the high level value in scientific notation."""
        cmd = ':SOURce<n>:VOLTage:LEVel:IMMediate:HIGH'
        full_acces = 'source.voltage.level.immediate.high'
        voltage=Argument(0,["<voltage>","MINimum","MAXimum"])
    
    class low(GenericGetSetCommandClass):
        """Set the low level of the basic waveform and the default unit is "V".
        The query returns the low level value in scientific notation."""
        cmd = ':SOURce<n>:VOLTage:LEVel:IMMediate:LOW'
        full_acces = 'source.voltage.level.immediate.low'
        voltage=Argument(0,["<voltage>","MINimum","MAXimum"])
    
    class amplitude(GenericGetSetCommandClass):
        """Set the basic waveform amplitude and the default unit is "Vpp".
        The query returns the amplitude value in scientific notation."""
        cmd = ':SOURce<n>:VOLTage:LEVel:IMMediate:AMPLitude'
        full_acces = 'source.voltage.level.immediate.amplitude'
        amplitude=Argument(0,["<amplitude>","MINimum","MAXimum"])
    
    class offset(GenericGetSetCommandClass):
        """Set the DC offset voltage and the default unit is "Vdc".
        The query returns the offset voltage value in scientific notation."""
        cmd = ':SOURce<n>:VOLTage:LEVel:IMMediate:OFFSet'
        full_acces = 'source.voltage.level.immediate.offset'
        voltage=Argument(0,["<voltage>","MINimum","MAXimum"])
    

class SourceVoltageLevel(Group):
    __metaclass__ = InstrumentMetaclass
    immediate=SourceVoltageLevelImmediate

class SourceVoltage(Group):
    __metaclass__ = InstrumentMetaclass
    range=SourceVoltageRange
    level=SourceVoltageLevel
    class unit(GenericGetSetCommandClass):
        """Set the amplitude unit.
        The query returns VPP, VRMS or DBM."""
        cmd = ':SOURce<n>:VOLTage:UNIT'
        full_acces = 'source.voltage.unit'
        __value=Argument(0,["VPP","VRMS","DBM"])
    

class SourceMarker(Group):
    __metaclass__ = InstrumentMetaclass
    class state(GenericGetSetCommandClass):
        """Enable or disable the "Mark" frequency function.
        The query returns ON or OFF."""
        cmd = ':SOURce<n>:MARKer:STATe'
        full_acces = 'source.marker.state'
        __value=Argument(0,["ON","OFF"])
    
    class frequency(GenericGetSetCommandClass):
        """Set the mark frequency of the Sweep and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:MARKer:FREQuency'
        full_acces = 'source.marker.frequency'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    

class SourceApply(Group):
    __metaclass__ = InstrumentMetaclass
    class val(GenericGetCommandClass):
        """Query the current configuration of the function generator and returns a character string enclosed in double quotation marks."""
        cmd = ':SOURce<n>:APPLy'
        full_acces = 'source.apply.val'
    
    class noise(GenericSetCommandClass):
        """Output a noise waveform with specified amplitude and DC offset."""
        cmd = ':SOURce<n>:APPLy:NOISe'
        full_acces = 'source.apply.noise'
        amp=Argument(0,["<amp>"])
        offset=Argument(1,["<offset>"])
    
    class ramp(GenericSetCommandClass):
        """Output a ramp waveform with specified frequency, amplitude, DC offset and start phase."""
        cmd = ':SOURce<n>:APPLy:RAMP'
        full_acces = 'source.apply.ramp'
        freq=Argument(0,["<freq>"])
        amp=Argument(1,["<amp>"])
        offset=Argument(2,["<offset>"])
        phase=Argument(3,["<phase>"])
    
    class pulse(GenericSetCommandClass):
        """Output a pulse waveform with specified frequency, amplitude, DC offset and delay."""
        cmd = ':SOURce<n>:APPLy:PULSe'
        full_acces = 'source.apply.pulse'
        freq=Argument(0,["<freq>"])
        amp=Argument(1,["<amp>"])
        offset=Argument(2,["<offset>"])
        delay=Argument(3,["<delay>"])
    
    class square(GenericSetCommandClass):
        """Output a square waveform with specified frequency, amplitude, DC offset and start phase."""
        cmd = ':SOURce<n>:APPLy:SQUare'
        full_acces = 'source.apply.square'
        freq=Argument(0,["<freq>"])
        amp=Argument(1,["<amp>"])
        offset=Argument(2,["<offset>"])
        phase=Argument(3,["<phase>"])
    
    class sinusoid(GenericSetCommandClass):
        """Output a sine waveform with specified frequency, amplitude, DC offset and start phase."""
        cmd = ':SOURce<n>:APPLy:SINusoid'
        full_acces = 'source.apply.sinusoid'
        freq=Argument(0,["<freq>"])
        amp=Argument(1,["<amp>"])
        offset=Argument(2,["<offset>"])
        phase=Argument(3,["<phase>"])
    
    class user(GenericSetCommandClass):
        """Output an arbitrary waveform with specified frequency, amplitude, DC offset and start phase."""
        cmd = ':SOURce<n>:APPLy:USER'
        full_acces = 'source.apply.user'
        freq=Argument(0,["<freq>"])
        amp=Argument(1,["<amp>"])
        offset=Argument(2,["<offset>"])
        phase=Argument(3,["<phase>"])
    

class SourceModAskeyInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class amplitude(GenericGetSetCommandClass):
        """Set the ASK modulating waveform amplitude and the default unit is "Vpp".
        The query returns the amplitude value in scientific notation."""
        cmd = ':SOURce<n>:MOD:ASKey:INTernal:AMPLitude'
        full_acces = 'source.mod.askey.internal.amplitude'
        amplitude=Argument(0,["<amplitude>","MINimum","MAXimum"])
    

class SourceModAskey(Group):
    __metaclass__ = InstrumentMetaclass
    internal=SourceModAskeyInternal
    class polarity(GenericGetSetCommandClass):
        """Select the "Positive" or "Negative" polarity of the modulating waveform to control the output amplitude.
        The query returns POS or NEG."""
        cmd = ':SOURce<n>:MOD:ASKey:POLarity'
        full_acces = 'source.mod.askey.polarity'
        __value=Argument(0,["POSitive","NEGative"])
    
    class source(GenericGetSetCommandClass):
        """Set the ASK modulating source type: Internal or External.
        The query returns INT or EXT."""
        cmd = ':SOURce<n>:MOD:ASKey:SOURce'
        full_acces = 'source.mod.askey.source'
        __value=Argument(0,["INTernal","EXTernal"])
    
    class freqency(GenericGetSetCommandClass):
        """Set the frequency at which the outoput amplitude "shifts" between the "carrier waveform amplitude" and the "modulating amplitude". The default unit is  "Hz".
        The query returns the rate value in scientific notation."""
        cmd = ':SOURce<n>:MOD:ASKey:FREQency'
        full_acces = 'source.mod.askey.freqency'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    

class SourceModIqPattern(Group):
    __metaclass__ = InstrumentMetaclass
    class val(GenericGetSetCommandClass):
        """Select the pre-defined code pattern inside the instrument or the user-defined code pattern.
        The query returns PN9, PN11, PN15, PN23, FIX4 or USER."""
        cmd = ':SOURce<n>:MOD:IQ:PATTern'
        full_acces = 'source.mod.iq.pattern.val'
        __value=Argument(0,["PN9","PN11","PN15","PN23","FIX4","USER"])
    
    class fix4(GenericGetSetCommandClass):
        """Set the FIX4 repeat sequence code pattern.
        The query returns the current code pattern."""
        cmd = ':SOURce<n>:MOD:IQ:PATTern:FIX4'
        full_acces = 'source.mod.iq.pattern.fix4'
        value=Argument(0,["<value>"])
    

class SourceModIqInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class rate(GenericGetSetCommandClass):
        """Set the transmission rate of the IQ code pattern and the default unit is "bps".
        The query returns the IQ code rate in scientific notation."""
        cmd = ':SOURce<n>:MOD:IQ:INTernal:RATE'
        full_acces = 'source.mod.iq.internal.rate'
        rate=Argument(0,["<rate>","MINimum","MAXimum"])
    

class SourceModIq(Group):
    __metaclass__ = InstrumentMetaclass
    pattern=SourceModIqPattern
    internal=SourceModIqInternal
    class data(GenericSetCommandClass):
        """Send binary data block to the volatile memory."""
        cmd = ':SOURce<n>:MOD:IQ:DATA'
        full_acces = 'source.mod.iq.data'
        __value=Argument(0,["VOLATILE"])
        binary_block_data=Argument(1,["<binary_block_data>"])
    
    class source(GenericGetSetCommandClass):
        """Set the IQ signal source type: Internal or External.
        The query returns"""
        cmd = ':SOURce<n>:MOD:IQ:SOURce'
        full_acces = 'source.mod.iq.source'
        __value=Argument(0,["INTernal","EXTernal"])
    
    class format(GenericGetSetCommandClass):
        """Set the IQ mapping type.
        The query returns BPSK, QPSK, OQPSK, 8PSK, 16PSK, 4QAM, 8QAM, 16QAM, 32QAM or 64QAM."""
        cmd = ':SOURce<n>:MOD:IQ:FORMat'
        full_acces = 'source.mod.iq.format'
        __value=Argument(0,["BPSK","QPSK","OQPSK","8PSK","16PSK","4QAM","8QAM","16QAM","32QAM","64QAM"])
    

class SourceModFskeyInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class rate(GenericGetSetCommandClass):
        """Set the frequency at which the FSK output frequency "shifts" between the "carrier frequency" and the "hop Frequency". The default unit is "Hz".
        The query returns the rate value in scientific notation."""
        cmd = ':SOURce<n>:MOD:FSKey:INTernal:RATE'
        full_acces = 'source.mod.fskey.internal.rate'
        rate=Argument(0,["<rate>","MINimum","MAXimum"])
    

class SourceModFskey(Group):
    __metaclass__ = InstrumentMetaclass
    internal=SourceModFskeyInternal
    class polarity(GenericGetSetCommandClass):
        """Select the "Positive" or "Negative" polarity of the modulating waveform to control the output frequency.
        The query returns POS or NEG."""
        cmd = ':SOURce<n>:MOD:FSKey:POLarity'
        full_acces = 'source.mod.fskey.polarity'
        __value=Argument(0,["POSitive","NEGative"])
    
    class source(GenericGetSetCommandClass):
        """Set the FSK modulating source type: Internal or External.
        The query returns INT or EXT."""
        cmd = ':SOURce<n>:MOD:FSKey:SOURce'
        full_acces = 'source.mod.fskey.source'
        __value=Argument(0,["INTernal","EXTernal"])
    
    class frequency(GenericGetSetCommandClass):
        """Set the alternating frequency ("hop" frequency) of the FSK and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:MOD:FSKey:FREQuency'
        full_acces = 'source.mod.fskey.frequency'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    

class SourceModAmInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class function(GenericGetSetCommandClass):
        """Select AM modulating waveform shape.
        The query returns SIN, SQU, TRI, RAMP, NRAM, NOIS or USER."""
        cmd = ':SOURce<n>:MOD:AM:INTernal:FUNCtion'
        full_acces = 'source.mod.am.internal.function'
        __value=Argument(0,["SINusoid","SQUare","TRIangle","RAMP","NRAMp","NOISe","USER"])
    
    class frequency(GenericGetSetCommandClass):
        """Set the AM modulating waveform frequency and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:MOD:AM:INTernal:FREQuency'
        full_acces = 'source.mod.am.internal.frequency'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    

class SourceModAm(Group):
    __metaclass__ = InstrumentMetaclass
    internal=SourceModAmInternal
    class source(GenericGetSetCommandClass):
        """Select the AM modulating source type: Internal or External.
        The query returns INT or EXT."""
        cmd = ':SOURce<n>:MOD:AM:SOURce'
        full_acces = 'source.mod.am.source'
        __value=Argument(0,["INTernal","EXTernal"])
    
    class depth(GenericGetSetCommandClass):
        """Set the amplitude vibration degree of the AM (Modulation Depth), expressed in percentage.
        The query returns the modulation depth percentage in scientific notation."""
        cmd = ':SOURce<n>:MOD:AM:DEPTh'
        full_acces = 'source.mod.am.depth'
        depth=Argument(0,["<depth>","MINimum","MAXimum"])
    

class SourceModPskeyInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class rate(GenericGetSetCommandClass):
        """Set the frequency at which the PSK output phase "shifts" between the "carrier phase" and the "modulating phase". The default unit is "Hz".
        The query returns the rate value in scientific notation."""
        cmd = ':SOURce<n>:MOD:PSKey:INTernal:RATE'
        full_acces = 'source.mod.pskey.internal.rate'
        rate=Argument(0,["<rate>","MINimum","MAXimum"])
    

class SourceModPskey(Group):
    __metaclass__ = InstrumentMetaclass
    internal=SourceModPskeyInternal
    class phase(GenericGetSetCommandClass):
        """Set the PSK modulating waveform phase.
        The query returns the phase value in scientific notation."""
        cmd = ':SOURce<n>:MOD:PSKey:PHASe'
        full_acces = 'source.mod.pskey.phase'
        phase=Argument(0,["<phase>","MINimum","MAXimum"])
    
    class polarity(GenericGetSetCommandClass):
        """Select the "Positive" or "Negative" polarity of the modulating waveform to control the output phase.
        The query returns POS or NEG."""
        cmd = ':SOURce<n>:MOD:PSKey:POLarity'
        full_acces = 'source.mod.pskey.polarity'
        __value=Argument(0,["POSitive","NEGative"])
    
    class source(GenericGetSetCommandClass):
        """Set the PSK modulating source type: Internal or External.
        The query returns INT or EXT."""
        cmd = ':SOURce<n>:MOD:PSKey:SOURce'
        full_acces = 'source.mod.pskey.source'
        __value=Argument(0,["INTernal","EXTernal"])
    

class SourceModPwmDeviation(Group):
    __metaclass__ = InstrumentMetaclass
    class dcycle(GenericGetSetCommandClass):
        """Set the duty cycle deviation namely the variation in duty cycle  (expressed in %) of the modulated waveform from the duty cycle of the original pulse waveform.
        The query returns the deviation value in scientific notation."""
        cmd = ':SOURce<n>:MOD:PWM:DEViation:DCYCle'
        full_acces = 'source.mod.pwm.deviation.dcycle'
        percent=Argument(0,["<percent>","MINimum","MAXimum"])
    
    class width(GenericGetSetCommandClass):
        """Set the pulse width deviation namely the variation in width (expressed in seconds) of the modulated waveform from the width of the original pulse waveform.
        The query returns the pulse width deviation in scientific notation."""
        cmd = ':SOURce<n>:MOD:PWM:DEViation:WIDTh'
        full_acces = 'source.mod.pwm.deviation.width'
        deviation=Argument(0,["<deviation>","MINimum","MAXimum"])
    

class SourceModPwmInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class function(GenericGetSetCommandClass):
        """Select Sine, Square, Triangle, UpRamp, DnRamp, Noise or Arb as the PWM modulating source.
        The query returns SIN, SQU, TRI, RAMP, NRAMP, NOIS or USER."""
        cmd = ':SOURce<n>:MOD:PWM:INTernal:FUNCtion'
        full_acces = 'source.mod.pwm.internal.function'
        __value=Argument(0,["SINusoid","SQUare","TRIangle","RAMP","NRAMp","NOISe","USER"])
    
    class frequency(GenericGetSetCommandClass):
        """Set the PWM modulating waveform frequency and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:MOD:PWM:INTernal:FREQuency'
        full_acces = 'source.mod.pwm.internal.frequency'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    

class SourceModPwm(Group):
    __metaclass__ = InstrumentMetaclass
    deviation=SourceModPwmDeviation
    internal=SourceModPwmInternal
    class source(GenericGetSetCommandClass):
        """Set the PWM modulating source type:Internal or External.
        The query returns INT or EXT."""
        cmd = ':SOURce<n>:MOD:PWM:SOURce'
        full_acces = 'source.mod.pwm.source'
        __value=Argument(0,["INTernal","EXTernal"])
    

class SourceModFmInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class function(GenericGetSetCommandClass):
        """Select the FM modulating waveform shape.
        The query returns SIN, SQU, TRI, RAMP, NRAM, NOIS or USER."""
        cmd = ':SOURce<n>:MOD:FM:INTernal:FUNCtion'
        full_acces = 'source.mod.fm.internal.function'
        __value=Argument(0,["SINusoid","SQUare","TRIangle","RAMP","NRAMp","NOISe","USER"])
    
    class frequency(GenericGetSetCommandClass):
        """Set the FM modulating waveform frequency and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:MOD:FM:INTernal:FREQuency'
        full_acces = 'source.mod.fm.internal.frequency'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    

class SourceModFm(Group):
    __metaclass__ = InstrumentMetaclass
    internal=SourceModFmInternal
    class deviation(GenericGetSetCommandClass):
        """Set the frequency deviation of the FM modulating waveform relative to the carrier waveform frequency and the default unit is "Hz".
        The query returns the deviation value in scientific notation."""
        cmd = ':SOURce<n>:MOD:FM:DEViation'
        full_acces = 'source.mod.fm.deviation'
        deviation=Argument(0,["<deviation>","MINimum","MAXimum"])
    
    class source(GenericGetSetCommandClass):
        """Set the FM modulating source type: Internal or External.
        The query returns INT or EXT."""
        cmd = ':SOURce<n>:MOD:FM:SOURce'
        full_acces = 'source.mod.fm.source'
        __value=Argument(0,["INTernal","EXTernal"])
    

class SourceModPmInternal(Group):
    __metaclass__ = InstrumentMetaclass
    class function(GenericGetSetCommandClass):
        """Select the PM modulating waveform shape.
        The query returns SIN, SQU, TRI, RAMP, NRAM, NOIS or USER."""
        cmd = ':SOURce<n>:MOD:PM:INTernal:FUNCtion'
        full_acces = 'source.mod.pm.internal.function'
        __value=Argument(0,["SINusoid","SQUare","TRIangle","RAMP","NRAMp","NOISe","USER"])
    
    class frequency(GenericGetSetCommandClass):
        """Set the PM modulating waveform frequency and the default unit is "Hz".
        The query returns the frequency value in scientific notation."""
        cmd = ':SOURce<n>:MOD:PM:INTernal:FREQuency'
        full_acces = 'source.mod.pm.internal.frequency'
        frequency=Argument(0,["<frequency>","MINimum","MAXimum"])
    

class SourceModPm(Group):
    __metaclass__ = InstrumentMetaclass
    internal=SourceModPmInternal
    class deviation(GenericGetSetCommandClass):
        """Set the deviation of the PM modulating waveform phase relative to the carrier waveform phase and the default unit is "°".
        The query returns the phase deviation value in scientific notation."""
        cmd = ':SOURce<n>:MOD:PM:DEViation'
        full_acces = 'source.mod.pm.deviation'
        deviation=Argument(0,["<deviation>","MINimum","MAXimum"])
    
    class source(GenericGetSetCommandClass):
        """Set the PM modulating source type: Internal or External.
        The query returns INT or EXT."""
        cmd = ':SOURce<n>:MOD:PM:SOURce'
        full_acces = 'source.mod.pm.source'
        __value=Argument(0,["INTernal","EXTernal"])
    

class SourceMod(Group):
    __metaclass__ = InstrumentMetaclass
    askey=SourceModAskey
    iq=SourceModIq
    fskey=SourceModFskey
    am=SourceModAm
    pskey=SourceModPskey
    pwm=SourceModPwm
    fm=SourceModFm
    pm=SourceModPm
    class state(GenericGetSetCommandClass):
        """Enable or disable the modulating function.
        The query returns ON or OFF."""
        cmd = ':SOURce<n>:MOD:STATe'
        full_acces = 'source.mod.state'
        __value=Argument(0,["ON","OFF"])
    
    class type(GenericGetSetCommandClass):
        """Select the modulating type of the signal generator.
        The query returns AM, FM, PM, ASK, FSK, PSK, PWM or IQ."""
        cmd = ':SOURce<n>:MOD:TYPe'
        full_acces = 'source.mod.type'
        __value=Argument(0,["AM","FM","PM","ASK","FSK","PSK","PWM","IQ"])
    

class Source(IndexedGroup):
    __metaclass__ = InstrumentMetaclass
    function=SourceFunction
    burst=SourceBurst
    period=SourcePeriod
    pulse=SourcePulse
    sweep=SourceSweep
    phase=SourcePhase
    frequency=SourceFrequency
    voltage=SourceVoltage
    marker=SourceMarker
    apply=SourceApply
    mod=SourceMod

class DisplaySaver(Group):
    __metaclass__ = InstrumentMetaclass
    class state(GenericGetSetCommandClass):
        """Enable or disable the screen saver mode.
        The query returns ON or OFF."""
        cmd = ':DISPlay:SAVer:STATe'
        full_acces = 'display.saver.state'
        __value=Argument(0,["ON","OFF"])
    
    class immediate(GenericCommandClass):
        """Enter screen saver state immediately."""
        cmd = ':DISPlay:SAVer:IMMediate'
        full_acces = 'display.saver.immediate'
    

class DisplayWindowHlight(Group):
    __metaclass__ = InstrumentMetaclass
    class color(GenericGetSetCommandClass):
        """Set the backgound color of the parameter or the menu selected on the interface.
        The query returns RED, DEEPRED, YELLOW, GREEN, AZURE, NAVYBLUE, BLUE, LILAC, PURPLE or ARGENT."""
        cmd = ':DISPlay:WINDow:HLIGht:COLor'
        full_acces = 'display.window.hlight.color'
        color=Argument(0,["<color>"])
    

class DisplayWindow(Group):
    __metaclass__ = InstrumentMetaclass
    hlight=DisplayWindowHlight

class Display(Group):
    __metaclass__ = InstrumentMetaclass
    saver=DisplaySaver
    window=DisplayWindow
    class brightness(GenericGetSetCommandClass):
        """Set the display brightness of the screen.
        The query returns the brightness percentage."""
        cmd = ':DISPlay:BRIGhtness'
        full_acces = 'display.brightness'
        brightness=Argument(0,["<brightness>","MINimum","MAXimum"])
    

class RigolDG5000(Generic, InstrumentCommand):
    __metaclass__ = InstrumentMetaclass
    coupling=Coupling
    trace=Trace
    system=System
    output=Output
    mmemory=Mmemory
    source=Source
    display=Display
