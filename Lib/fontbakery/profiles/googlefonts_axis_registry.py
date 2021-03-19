from fontbakery.axes_pb2 import AxisProto
from fontbakery.utils import get_Protobuf_Message
from pkg_resources import resource_filename


def AxisRegistry():

    def normalize_name(name):
        return ''.join(name.split(' '))

    registry = {}
    def append_AxisMessage(path):
        axis_dict = {"message": get_Protobuf_Message(AxisProto, path),
                     "fallbacks": {}}
        for fb in axis_dict["message"].fallback:
            axis_dict["fallbacks"][normalize_name(fb.name)] = fb.value
        registry[axis_dict["message"].tag] = axis_dict

    for axis in ["casual.textproto",
                 "cursive.textproto",
                 "flair.textproto",
                 "grade.textproto",
                 "italic.textproto",
                 "monospace.textproto",
                 "optical_size.textproto",
                 "slant.textproto",
                 "softness.textproto",
                 "volume.textproto",
                 "weight.textproto",
                 "width.textproto",
                 "wonky.textproto"]:
        append_AxisMessage(resource_filename('fontbakery', 'data/' + axis))
    return registry
