"""Assess transcript abundance in RNA-seq experiments using Cufflinks.

http://cufflinks.cbcb.umd.edu/manual.html
"""
import os
import subprocess

from bcbio.pipeline import config_utils

def assemble_transcripts(align_file, ref_file, config, data):
    """Create transcript assemblies using Cufflinks.
    """
    work_dir, fname = os.path.split(align_file)
    num_cores = config["algorithm"].get("num_cores", 1)
    core_flags = ["-p", str(num_cores)] if num_cores > 1 else []
    out_dir = os.path.join(work_dir,
                           "{base}-cufflinks".format(base=os.path.splitext(fname)[0]))
    cl = [config_utils.get_program("cufflinks", config),
          align_file,
          "-o", out_dir,
          "-b", ref_file,
          "-u"]
    cl += core_flags
    tx_file = data["genome_resources"]["rnaseq"]["transcripts"]
    tx_mask_file = data["genome_resources"]["rnaseq"]["transcripts_mask"]
    if tx_file:
        cl += ["-g", tx_file]
    if tx_mask_file:
        cl += ["-M", tx_mask_file]
    out_tx_file = os.path.join(out_dir, "transcripts.gtf")
    if not os.path.exists(out_tx_file):
        subprocess.check_call(cl)
    assert os.path.exists(out_tx_file)
    return out_tx_file
