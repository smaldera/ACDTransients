#!/bin/bash

##SBATCH --partition=milano
#SBATCH --account=fermi:users
#SBATCH --job-name=test
#SBATCH --output=output.txt
#SBATCH --error=output.txt
#
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4g
#
#SBATCH --time=0-01:10:00
#
#    #SBATCH --gpus 



CONTAINERDIR=/sdf/group/fermi/sw/containers
#-B $CONTAINERDIR/rhel6/afs/slac.stanford.edu/package/perl:/afs/slac.stanford.edu/package/perl \
apptainer exec -B /sdf:/sdf \
                -B /sdf/group/fermi/a:/afs/slac/g/glast \
                -B /sdf/group/fermi/a:/afs/slac.stanford.edu/g/glast \
                -B /sdf/group/fermi/sw/package:/afs/slac/package \
                -B /sdf/group/fermi/sw/package:/afs/slac.stanford.edu/package \
                -B $CONTAINERDIR/rhel6/opt/TWWfsw:/opt/TWWfsw \
                -B $CONTAINERDIR/rhel6/usr/local:/usr/local \
                $CONTAINERDIR/fermi-rhel6.20230922.sif sh myjob.sh
