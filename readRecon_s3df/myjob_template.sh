#!/bin/bash


echo "inizializzazione variabili per  reconInterface (meritUtils)"

export GLAST_EXT=/afs/slac/g/glast/ground/GLAST_EXT/redhat6-x86_64-64bit-gcc44/
export PATH=$GLAST_EXT/python/2.7.6/bin:$PATH
export ROOTSYS=$GLAST_EXT/ROOT/v5.34.03-gr01
export LD_LIBRARY_PATH=$ROOTSYS/lib
export PATH=$ROOTSYS/bin:$PATH
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH 
export INST_DIR=/sdf/group/fermi/n/u52/ReleaseManagerBuild/redhat6-x86_64-64bit-gcc44/Optimized/GlastRelease/20-11-00/





# OLD  export PARENT="/nfs/farm/g/glast/u52/ReleaseManagerBuild/redhat6-x86_64-64bit-gcc44/Optimized/GlastRelease/20-11-00"
export PARENT="/sdf/group/fermi/n/u52/ReleaseManagerBuild/redhat6-x86_64-64bit-gcc44/Optimized/GlastRelease/20-11-00/"
export VARIANT=redhat6-x86_64-64bit-gcc44-Optimized



#source /nfs/farm/g/glast/u52/ReleaseManagerBuild/redhat6-x86_64-64bit-gcc44/Optimized/GlastRelease/20-11-00/bin/redhat6-x86_64-64bit-gcc44-Optimized/_setup.sh 
source /sdf/group/fermi/n/u52/ReleaseManagerBuild/redhat6-x86_64-64bit-gcc44/Optimized/GlastRelease/20-11-00/bin/redhat6-x86_64-64bit-gcc44-Optimized/_setup.sh


export LD_LIBRARY_PATH=/sdf/group/fermi/n/u52/ReleaseManagerBuild/redhat6-x86_64-64bit-gcc44/Optimized/GlastRelease/20-11-00/lib/redhat6-x86_64-64bit-gcc44-Optimized/:$LD_LIBRARY_PATH


