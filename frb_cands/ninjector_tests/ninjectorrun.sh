#!/bin/bash

list=$1

while read line
do

    workdir=/scratch/mmalenta/ninjector_tests

    export OMP_NUM_THREADS=16

    filename=$(basename $line)
    sourcename=$(echo $filename | sed 's/\([a-zA-Z0-9_\-]*\)_gsb.*/\1/')

    mkdir ${sourcename}
    cd ${sourcename}

    #rsync -avz --progress -e 'ssh -i /home/mmalenta/.ssh/hydrus' malenta@hydrus.jb.man.ac.uk:${line} ./${filename}.gmrt_dat
    #rsync -avz -e 'ssh -i /home/mmalenta/.ssh/hydrus' malenta@hydrus.jb.man.ac.uk:${line}.gmrt_hdr ./${filename}.gmrt_hdr

    scp -i /home/mmalenta/.ssh/hydrus malenta@hydrus.jb.man.ac.uk:${line} ./${filename}.gmrt_dat
    scp -i /home/mmalenta/.ssh/hydrus malenta@hydrus.jb.man.ac.uk:${line}.gmrt_hdr ./${filename}.gmrt_hdr


    filterbank ${filename}.gmrt_dat > ${sourcename}.fil

    rm *.gmrt_dat
    rm *.gmrt_hdr

    mkdir original
    cd original

    /home/mmalenta/code/Bifrost/bin/bifrost -f ${workdir}/${sourcename}/${sourcename}.fil -o ${workdir}/${sourcename}/original --dm_start 0 --dm_end 2000 --single -t 1 -k /home/mmalenta/code/Bifrost/killmask2048.kill

    cat *.cand > allcands_original
    /home/mmalenta/code/Bifrost/scripts/trans_gen_overview.py -cands_file allcands_original
    mv overview*.png ${sourcename}_original.png
    cd ../

    /home/mmalenta/code/ninjector/bin/ninjector -f ${workdir}/${sourcename}/${sourcename}.fil -o ${workdir}/${sourcename}/${sourcename}_injected.fil -r 

    mkdir injected
    cd injected

    /home/mmalenta/code/Bifrost/bin/bifrost -f ${workdir}/${sourcename}/${sourcename}_injected.fil -o ${workdir}/${sourcename}/injected --dm_start 0 --dm_end 2000 --single -t 1 -k /home/mmalenta/code/Bifrost/killmask2048.kill

    cat *.cand > allcands_injected
    /home/mmalenta/code/Bifrost/scripts/trans_gen_overview.py -cands_file allcands_injected
    mv overview*.png ${sourcename}_injected.png
    cd ../
    rm *.fil

    cd ${workdir}

done < $list
