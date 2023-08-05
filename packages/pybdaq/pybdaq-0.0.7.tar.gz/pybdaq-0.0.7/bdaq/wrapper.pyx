import bdaq.wrapper_enums as enums

cimport libc.stdint
cimport libcpp
cimport bdaq.wrapper_c as _c
cimport bdaq.wrapper_enums_c as enums_c

from libc.stddef cimport wchar_t
from libc.stdint cimport (
    uint8_t,
    int32_t)
from cython.view cimport array as cvarray
from cython.operator cimport dereference as deref


class BdaqError(Exception):
    def __init__(self, error_code):
        assert isinstance(error_code, enums.ErrorCode)

        super(BdaqError, self).__init__("bdaq error: {}".format(error_code))

        self.error_code = error_code


def encode_wchar(string):
    # TODO make this less obviously incorrect

    if sizeof(wchar_t) == 2:
        return string.encode("UTF-16")
    elif sizeof(wchar_t) == 4:
        return string.encode("UTF-32")
    else:
        assert False


def pack_bits(bools):
    """Pack array of bools into bits."""

    if len(bools) % 8 != 0:
        raise ValueError("list length must be multiple of 8")

    cdef int i

    bytes_ = []

    for i in xrange(len(bools) / 8):
        b = 0

        for v in reversed(bools[i * 8:(i + 1) * 8]):
            b <<= 1

            b |= int(bool(v))

        bytes_.append(b)

    return bytes_


cdef libcpp.bool raise_on_null(void* pointer) except False:
    if pointer == NULL:
        raise Exception("object does not exist")
    else:
        return True


cdef libcpp.bool raise_on_failure(enums_c.ErrorCode error) except False:
    if error == enums_c.Success:
        return True
    else:
        raise BdaqError(enums.ErrorCode(error))


cdef class MathInterval:
    cdef object _type
    cdef double _min
    cdef double _max

    def __cinit__(self, type_, min_, max_):
        if not isinstance(type_, enums.MathIntervalType):
            raise ValueError("type_ must be MathIntervalType")

        self._type = type_
        self._min = min_
        self._max = max_

    property type:
        def __get__(self):
            return self._type

    property min:
        def __get__(self):
            return self._min

    property max:
        def __get__(self):
            return self._max

cdef MathInterval math_interval_from_c(_c.MathInterval interval):
    return MathInterval(
        enums.MathIntervalType(interval.Type),
        interval.Min,
        interval.Max)


cdef class CjcSetting:
    cdef InstantAiCtrl _instant_ai

    def __cinit__(self, InstantAiCtrl instant_ai):
        self._instant_ai = instant_ai

    cdef _c.CjcSetting* c0(self):
        return self._instant_ai.c2().getCjc()

    property channel:
        def __get__(self):
            return self.c0().getChannel()

        def __set__(self, int32_t channel):
            cdef enums_c.ErrorCode error = self.c0().setChannel(channel)

            raise_on_failure(error)

    property value:
        def __get__(self):
            return self.c0().getValue()

        def __set__(self, double value):
            cdef enums_c.ErrorCode error = self.c0().setValue(value)

            raise_on_failure(error)


cdef class DeviceInformation:
    cdef _c.DeviceInformation* _this

    def __cinit__(self, number=None, description=None, mode=None, index=None):
        self._this = new _c.DeviceInformation()

        cdef wchar_t* description_wchar = NULL

        if description is not None:
            description_wchar_py = encode_wchar(description)
            description_wchar = <libc.stddef.wchar_t*><char*>description_wchar_py

        self._this.Init(
            -1 if number is None else number,
            description_wchar,
            enums_c.ModeWriteWithReset if mode is None else mode,
            0 if index is None else index)

    cdef _c.DeviceInformation* c0(self):
        raise_on_null(self._this)

        return self._this


cdef class AiFeatures(object):
    cdef InstantAiCtrl _instant_ai

    def __cinit__(self, InstantAiCtrl instant_ai):
        self._instant_ai = instant_ai

        # extract feature values
        cdef _c.AiFeatures* features = self.c0()

        self.resolution = features.getResolution()
        self.data_size = features.getDataSize()
        self.data_mask = features.getDataMask()
        self.channel_count_max = features.getChannelCountMax()
        self.channel_type = enums.AiChannelType(features.getChannelType())
        self.overall_value_range = features.getOverallValueRange()
        self.thermo_supported = features.getThermoSupported()
        self.buffered_ai_supported = features.getBufferedAiSupported()
        self.channel_start_base = features.getChannelStartBase()
        self.channel_count_base = features.getChannelCountBase()
        self.burst_scan_supported = features.getBurstScanSupported()
        self.scan_count_max = features.getScanCountMax()
        self.trigger_supported = features.getTriggerSupported()
        self.trigger_count = features.getTriggerCount()
        self.trigger_1_supported = features.getTrigger1Supported()

        # prevent modification
        def setattr(self):
            raise Exception("read-only property")

        self.__setattr__ = setattr

    cdef _c.AiFeatures* c0(self):
        return self._instant_ai.c2().getFeatures()

    property value_ranges:
        def __get__(self):
            values = []

            cdef _c.ICollection[enums_c.ValueRange]* collection = self.c0().getValueRanges()

            for i in xrange(collection.getCount()):
                values.append(enums.ValueRange(collection.getItem(i)))

            return values

    property burnout_return_types:
        def __get__(self):
            values = []

            cdef _c.ICollection[enums_c.BurnoutRetType]* collection = self.c0().getBurnoutReturnTypes()

            for i in xrange(collection.getCount()):
                values.append(enums.BurnoutRetType(collection.getItem(i)))

            return values

    property cjc_channels:
        def __get__(self):
            values = []

            cdef _c.ICollection[int32_t]* collection = self.c0().getCjcChannels()

            for i in xrange(collection.getCount()):
                values.append(collection.getItem(i))

            return values

    @property
    def sampling_method(self):
        return enums.SamplingMethod(self.c0().getSamplingMethod())

    @property
    def convert_clock_range(self):
        return math_interval_from_c(self.c0().getConvertClockRange())

    @property
    def scan_clock_range(self):
        return math_interval_from_c(self.c0().getScanClockRange())

    @property
    def trigger_delay_range(self):
        return math_interval_from_c(self.c0().getTriggerDelayRange())

    @property
    def trigger1_delay_range(self):
        return math_interval_from_c(self.c0().getTrigger1DelayRange())


cdef class DeviceCtrlBase:
    cdef _c.DeviceCtrlBase* _this

    def __cinit__(self):
        if self.__class__ == DeviceCtrlBase:
            raise Exception("cannot instantiate abstract base")

    def __dealloc__(self):
        if self._this != NULL:
            self._this.Dispose()

    cdef _c.DeviceCtrlBase* c0(self):
        raise_on_null(self._this)

        return self._this

    property selected_device:
        def __get__(self):
            cdef DeviceInformation device = DeviceInformation()

            self.c0().getSelectedDevice(deref(device.c0()))

            return device

        def __set__(self, DeviceInformation device):
            cdef enums_c.ErrorCode error = self.c0().setSelectedDevice(deref(device.c0()))

            raise_on_failure(error)


cdef class AiCtrlBase(DeviceCtrlBase):
    def __cinit__(self):
        if self.__class__ == AiCtrlBase:
            raise Exception("cannot instantiate abstract base")

    cdef _c.AiCtrlBase* c1(self):
        raise_on_null(self._this)

        return <_c.AiCtrlBase*>self._this

    property features:
        def __get__(self):
            return AiFeatures(self)

    property channel_count:
        def __get__(self):
            return self.c1().getChannelCount()


cdef class InstantAiCtrl(AiCtrlBase):
    def __cinit__(self):
        self._this = _c.AdxInstantAiCtrlCreate()

    cdef _c.InstantAiCtrl* c2(self):
        raise_on_null(self._this)

        return <_c.InstantAiCtrl*>self._this

    @property
    def cjc(self):
        return CjcSetting(self)

    def read(self, start, count=1):
        cdef int32_t[:] raw = cvarray(
            shape=(count,),
            itemsize=sizeof(int32_t),
            format="i")
        cdef double[:] scaled = cvarray(
            shape=(count,),
            itemsize=sizeof(double),
            format="d")
        cdef enums_c.ErrorCode error = self.c2().Read(
            <int32_t>start,
            <int32_t>count,
            &raw[0],
            &scaled[0])

        raise_on_failure(error)

        return (list(raw), list(scaled))

    def read_raw(self, *args, **kwargs):
        (raw, _) = self.read(*args, **kwargs)

        return raw

    def read_scaled(self, *args, **kwargs):
        (_, scaled) = self.read(*args, **kwargs)

        return scaled


#
# DIGITAL I/O
#

class DioFeatures(object):
    def __init__(self, DioCtrlBase di_or_do_base):
        # extract the features object
        cdef _c.DioFeatures* features
        cdef _c.DoCtrlBase* do_base_c

        #if isinstance(di_or_do_base, DiCtrlBase):
            #raise NotImplementedError()
        if isinstance(di_or_do_base, DoCtrlBase):
            do_base_c = <_c.DoCtrlBase*>di_or_do_base._this

            raise_on_null(do_base_c)

            features = do_base_c.getFeatures()
        else:
            assert False

        # extract feature values
        self.port_programmable = features.getPortProgrammable()
        self.port_count = features.getPortCount()
        self.di_supported = features.getDiSupported()
        self.do_supported = features.getDoSupported()
        self.channel_count_max = features.getChannelCountMax()

        # prevent modification
        def setattr(self):
            raise Exception("read-only property")

        self.__setattr__ = setattr


cdef class DioCtrlBase(DeviceCtrlBase):
    cdef _c.DioCtrlBase* c1(self):
        raise_on_null(self._this)

        return <_c.DioCtrlBase*>self._this

    property port_count:
        def __get__(self):
            return self.c1().getPortCount()


class DoFeatures(DioFeatures):
    def __init__(self, DoCtrlBase do_base):
        raise_on_null(do_base._this)

        cdef _c.DoFeatures* features = do_base.c2().getFeatures()

        self.buffered_do_supported = features.getBufferedDoSupported()
        self.burst_scan_supported = features.getBurstScanSupported()
        self.scan_count_max = features.getScanCountMax()
        self.trigger_supported = features.getTriggerSupported()
        self.trigger_count = features.getTriggerCount()

        DioFeatures.__init__(self, do_base)


cdef class DoCtrlBase(DioCtrlBase):
    cdef _c.DoCtrlBase* c2(self):
        raise_on_null(self._this)

        return <_c.DoCtrlBase*>self._this

    property features:
        def __get__(self):
            return DoFeatures(self)


cdef class InstantDoCtrl(DoCtrlBase):
    def __cinit__(self):
        self._this = _c.AdxInstantDoCtrlCreate()

    cdef _c.InstantDoCtrl* c3(self):
        raise_on_null(self._this)

        return <_c.InstantDoCtrl*>self._this

    def read(self, start, count=1):
        cdef uint8_t[:] raw = cvarray(
            shape=(count,),
            itemsize=sizeof(uint8_t),
            format="u")
        cdef enums_c.ErrorCode error = self.c3().Read(
            <int32_t>start,
            <int32_t>count,
            &raw[0])

        raise_on_failure(error)

        # XXX unpack bits into boolean array
        return list(raw)

    def write(self, data, start=0):
        # pack list of bools into bytes
        data_bytes = pack_bits(data)

        # copy output data in memory buffer
        cdef uint8_t[:] raw = cvarray(
            shape=(len(data_bytes),),
            itemsize=sizeof(uint8_t),
            format="B")
        cdef int i

        for (i, v) in enumerate(map(int, data_bytes)):
            raw[i] = v

        # write to hardware
        cdef enums_c.ErrorCode error = self.c3().Write(
            <int32_t>start,
            <int32_t>len(data_bytes),
            &raw[0])

        raise_on_failure(error)
