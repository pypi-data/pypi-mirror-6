import gflags

FLAGS = gflags.FLAGS


class SumFlag(gflags.BooleanFlag):

    def Parse(self, arguments):
        """Parses one or more boolean arguemnts.
        
        Args:
        arguments: a single argument or a list of arguments (typically a
        list of default values); a single argument is converted
        internally into a list containing one item.
        """
        if not isinstance(arguments, list):
            # Default value may be a list of values.  Most other arguments
            # will not be, so convert them into a single-item list to make
            # processing simpler below.
            arguments = [arguments]

        if self.present:
            # keep a backup reference to list of previously supplied option values
            values = self.value
        else:
            # "erase" the defaults with an empty list
            values = 0

        for item in arguments:
            # have Flag superclass parse argument, overwriting self.value reference
            gflags.BooleanFlag.Parse(self, item)  # also increments self.present
            if self.value is not None:
                values += {True: 1, False: -1}[bool(self.value)]

        # put list of option values back in the 'value' attribute
        self.value = max(0, values)


def DEFINE_multiboolean(name, default, help, flag_values=FLAGS,
                 **args):
  """Registers a boolean MultiFlag.

  Use the flag on the command line multiple times to increment the
  counter integer.  The 'default' is an integer indicating the
  starting value in the absence of true or false flags.

  """
  parser = gflags.BooleanParser()
  serializer = gflags.ArgumentSerializer()
  gflags.DEFINE_flag(SumFlag(name, default, help, **args),
              flag_values)

DEFINE_multibool = DEFINE_multiboolean

__ALL__ = ["DEFINE_multiboolean", "DEFINE_multibool"]
