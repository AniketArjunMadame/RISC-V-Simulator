#!/usr/bin/env python3
import argparse
import os
import sys
import ram
import loader
import logger
import stats
import core


if not hasattr(stats.Statistics, "__patched__"):
    orig_init = stats.Statistics.__init__
    def patched_init(self, loggr):
        orig_init(self, loggr)
        if not hasattr(self, "register_accesses"):
            self.register_accesses = 0
    stats.Statistics.__init__ = patched_init
    stats.Statistics.__patched__ = True



if hasattr(core, "PipelinedProcessor") and hasattr(core.PipelinedProcessor, "mem_access"):
    _orig_mem_access = core.PipelinedProcessor.mem_access
    def _tracked_mem_access(self, *args, **kwargs):
        if hasattr(self, "stats"):
            try:
                self.stats.increment_memory_access()
            except Exception:
                pass
        return _orig_mem_access(self, *args, **kwargs)
    core.PipelinedProcessor.mem_access = _tracked_mem_access


if hasattr(core, "FPipelinedProcessor"):
    try:
        _orig_fp_mem_access = core.FPipelinedProcessor.mem_access
        def _tracked_fp_mem_access(self, *args, **kwargs):
            if hasattr(self, "stats"):
                try:
                    self.stats.increment_memory_access()
                except Exception:
                    pass
            return _orig_fp_mem_access(self, *args, **kwargs)
        core.FPipelinedProcessor.mem_access = _tracked_fp_mem_access
    except Exception:
        pass



def parse_args():
    parser = argparse.ArgumentParser(description="RISC-V Processor Simulator")
    parser.add_argument('--start', type=lambda x: int(x.replace('0x', '').replace('0X', ''), 16), 
                        required=True,
                        help='Start PC in hex (e.g. 0x80000000 or 80000000)')
    parser.add_argument('r5ob_path', type=str,
                        help='Path to the input r5ob file')
    parser.add_argument('--num_insts', type=int, default=1000,
                        help='Number of instructions to simulate (default: 1000)')
   
    parser.add_argument(
        '--proc',
        type=str,
        choices=['SingleCycleProcessor', 'PipelinedProcessor','FPipelinedProcessor'],
        default='SingleCycleProcessor',
        help='Select processor type: SingleCycleProcessor or PipelinedProcessor (default: SingleCycleProcessor)'
    )
    
    return parser.parse_args()

def run_simulation():
    """Main simulation entry point"""
    
    
    loggr = logger.setup()
    cmd = "python3 " + " ".join(sys.argv)
    loggr.info(f"Running: {cmd}")

    args = parse_args()

    
    if not os.path.isfile(args.r5ob_path):
        loggr.error(f"Error: Executable file '{args.r5ob_path}' does not exist.")
        sys.exit(1)

    
    mem = ram.RAM(loggr)
    loader.load(mem, args.r5ob_path)
    
    
    
    
    
    st = stats.Statistics(loggr)
    
    
    if args.proc == 'SingleCycleProcessor':
        processor = core.SingleCycleProcessor(args.start, mem, loggr, st)
        processor.stats = st  
        loggr.info("Using SingleCycleProcessor")
    elif args.proc == 'PipelinedProcessor':
        processor = core.PipelinedProcessor(args.start, mem, loggr, st)
        processor.stats = st  
        loggr.info("Using PipelinedProcessor")
    elif args.proc == 'FPipelinedProcessor':
        processor = core.FPipelinedProcessor.FPipelinedProcessor(args.start, mem, loggr, st)
        processor.stats = st  
        loggr.info("Using FPipelinedProcessor")
    else:
        loggr.error(f"Invalid processor type: {args.proc}")
        sys.exit(1)

    
    loggr.info(f"Start address: {hex(args.start)}")
    loggr.info(f"Executable path: {args.r5ob_path}")
    loggr.info(f"Number of instructions: {args.num_insts}")

    
    try:
        
        loggr.info(f"Shared stats ID check: simulate={id(st)}, processor={id(processor.stats)}")
        loggr.info(f"Stats before run: cycles={st.clock_cycles}, insts={st.instruction_count}, mem={st.memory_accesses}")
        processor.run(args.num_insts)
    except Exception as e:
        loggr.error(f"Simulation error: {e}")
        import traceback
        loggr.error(traceback.format_exc())
        sys.exit(1)
    
    
    
    loggr.info(f"Stats before write: cycles={st.clock_cycles}, insts={st.instruction_count}, mem={st.memory_accesses}")
    try:
        
        cwd_path = os.path.join(os.getcwd(), "stats.json")
        st.write_statistics(cwd_path)
        try:
            with open(cwd_path, "r") as _f:
                loggr.info(f"stats.json (cwd) content: {_f.read()}")
        except Exception:
            pass

        
        src_path = os.path.join(os.path.dirname(__file__), "stats.json")
        if os.path.abspath(src_path) != os.path.abspath(cwd_path):
            st.write_statistics(src_path)
            try:
                with open(src_path, "r") as _f:
                    loggr.info(f"stats.json (src) content: {_f.read()}")
            except Exception:
                pass

        loggr.info(f"Statistics saved to: {cwd_path} and {src_path}")
    except Exception as e:
        loggr.error(f"Failed writing stats.json: {e}")
        import traceback
        loggr.error(traceback.format_exc())
        sys.exit(1)

    loggr.info("Simulation completed successfully")

if __name__ == "__main__":
    run_simulation()

