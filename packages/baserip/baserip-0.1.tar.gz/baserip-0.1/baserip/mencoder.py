class Command(object):
    def __init__(self, com):
        self._opts = []
        self._sep = ':'
        self.add_opt(com)
    
    def add_opt(self, name, param='', sep=None):
        opts = next((c for c in self._opts if c[0] == name), None)
        if opts is None:
            self._opts.append([str(name), str(param)])
        else:
            opts[1] += (sep or self._sep) + str(param)
    
    def add_opts(self, opts):
        for opt in opts:
            self.add_opt(*opt)
      
    def _gen_opt(self):
        for opt in self._opts:
            yield opt
      
    def _mangle(self):
    # Override this
        for opt in self._gen_opt():
            yield opt
      
    def _split_opt(self):
        for opt in self._mangle():
            for part in opt:
                if part:
                    yield part
      
    def gen_command(self):
        """
        Returns a list of strings which represent a subprocess command 
        suitable for feeding into :py:class:`subprocess.Popen` as the 
        *args* parameter.
        
        :return: list of strings
        :rtype: list
        """
        
        return [opt for opt in self._split_opt()]
    
    def __str__(self):
        return ' '.join(self.gen_command())
    
class Mencoder(Command):
    def __init__(self, bitrate=500, passes=1):
        super().__init__('mencoder')
        self.bitrate = str(bitrate)
        self.passes = passes
        self.pass_ = 0
        
    def _mangle(self):
        for opt in self._gen_opt():
            # copy the option to prevent permanent overwriting
            copt = opt[:]
            
            # if 2 pass or multipass
            if self.passes > 1:
            
                # redirect output to null  and set turbo flag on first pass
                if self.pass_ == 0:
                    if copt[0] == '-o':
                        copt[1] = '/dev/null'
                    if copt[0] == '-x264encopts' or copt[0] == '-lavcopts':
                        copt[1] +=':turbo'

                # Add the (v)pass option
                if copt[0] == '-x264encopts':
                    copt[1] += ':pass={}'.format(self._adjust_pass() + 1)
                if copt[0] == '-lavcopts':
                    copt[1] += ':vpass={}'.format(self._adjust_pass() + 1)

            # Add the bitrate option
            if copt[0] == '-x264encopts':
                copt[1] += ':bitrate={}'.format(self.bitrate)
            if copt[0] == '-lavcopts':
                copt[1] += ':vbitrate={}'.format(self.bitrate)
                
            # Rip subs on first pass only
            if self.pass_ > 0:
                if copt[0] == '-vobsubout':
                    copt = ('-nosub', '')
                elif  copt[0] == '-sid':
                    copt = ('', '')
                
            yield copt
    
    def _adjust_pass(self):
        if self.passes > 2:
            if self.pass_ > 0:
                return 2
        return self.pass_
        
    def gen_passes(self):
        for self.pass_ in range(self.passes):
            yield self.gen_command()

if __name__ == '__main__':
    pass
